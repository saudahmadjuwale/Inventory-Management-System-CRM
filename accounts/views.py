from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Tenant, User
from django.utils import timezone 
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
import uuid
from django.template.loader import render_to_string

resend.api_key = os.environ.get("RESEND_API_KEY")

def send_setup_email(to_email, setup_link):
    try:
        resend.Emails.send({
            "from": "onboarding@resend.dev",  # default works
            "to": to_email,
            "subject": "Set up your account",
            "html": f"""
                <h2>Welcome to GinnieFlow</h2>
                <p>Click below to set your password:</p>
                <a href="{setup_link}">Setup Password</a>
            """
        })
    except Exception as e:
        print("Email error:", e)
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_password_set:
                messages.error(request, 'Please complete your account setup')
                return redirect('login')
            login(request,user)
            if user.is_superuser:
                return redirect('superadmin')
            if user.role == 'owner':
                return redirect('owner',)
            if user.role == 'admin':
                return redirect('admin')
            if user.role == 'agent':
                return redirect('agent')
    return render(request,'authentication/login.html')

def superadmin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('login')
    status = request.GET.get('status', 'active')  
    if status == 'inactive':
        tenants = Tenant.objects.filter(is_active=False)
    elif status == 'all':
        tenants = Tenant.objects.all()
    else:
        tenants = Tenant.objects.filter(is_active=True)
    return render(request, 'dashboard/superadmin.html', {
        'tenants': tenants,
        'status': status
    })
def add_tenant(request):
    if not request.user.is_superuser:
        return redirect('login')
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        owner_email = request.POST.get('owner_email')

        if Tenant.objects.filter(email=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "Tenant with this email already exists")
            return redirect('superadmin')
        tenant = Tenant.objects.create(name=name, email=email)
        token = str(uuid.uuid4())
        expiry = timezone.now() + timezone.timedelta(hours=24)
        user = User.objects.create(
            username=email,
            email=email,
            tenant=tenant,
            role='owner',
            setup_token=token,
            token_expiry=expiry,
            is_password_set=False
        )
        setup_link = f"http://127.0.0.1:8000/accounts/setup/{token}/"
        subject = "Set up your account - Web Ginnie"
        html_content = render_to_string('emails/setup_email.html', {
            'setup_link': setup_link
        })

        email = EmailMultiAlternatives(
            subject=subject,
            body="Please use an HTML compatible email client",  # fallback
            from_email=settings.EMAIL_HOST_USER,
            to=[email]
        )
        email.attach_alternative(html_content, "text/html")
        send_setup_email(email, setup_link)
        return redirect('superadmin')
def update_tenant(request, id):
    if not request.user.is_superuser:
        return redirect('login')
    tenant = Tenant.objects.get(id=id)
    if request.method == 'POST':
        tenant.name = request.POST.get('name')
        tenant.email = request.POST.get('email')
        tenant.save()
    return redirect('superadmin')
def delete_tenant(request, id):
    if not request.user.is_superuser:
        return redirect('login')

    tenant = get_object_or_404(Tenant, id=id)

    if request.method == 'POST':
        tenant.is_active = False
        tenant.save()
        return redirect('superadmin')

    return redirect('superadmin')
def hard_delete_tenant(request, id):
    if not request.user.is_superuser:
        return redirect('login')

    tenant = get_object_or_404(Tenant, id=id)
    if tenant.is_active:
        return HttpResponseForbidden("Deactivate first")
    if request.method == 'POST':
        tenant.delete()

    return redirect('superadmin')
def tenant_detail(request, id):
    if not request.user.is_superuser:
        return redirect('login')
    tenant = Tenant.objects.get(id=id)
    users = User.objects.filter(tenant=tenant)
    return render(request, 'dashboard/tenant_detail.html', {
        'tenant': tenant,
        'users': users
    })
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    tenant = user.tenant

    if request.method == 'POST':
        new_email = request.POST.get('email')

        user.email = new_email
        user.username = new_email
        user.save()

        # keep tenant email in sync
        tenant.email = new_email
        tenant.save()

        messages.success(request, "User updated successfully")

    return redirect('tenant_detail', id=tenant.id)
def setup_password(request, token):
    user = User.objects.filter(setup_token=token).first()

    if not user:
        messages.error(request, "Invalid setup link")
        return redirect('login')

    if user.token_expiry < timezone.now():
        messages.error(request, "Setup link expired")
        return redirect('login')

    if request.method == 'POST':
        password = request.POST.get('password')

        user.set_password(password)
        user.is_password_set = True

        # clear token
        user.setup_token = None
        user.token_expiry = None

        user.save()

        messages.success(request, "Password set successfully. Please login.")
        return redirect('login')

    return render(request, 'authentication/setup_password.html')
def owner_dashboard(request):
    user = request.user
    return render(request, 'dashboard/owner.html', {'user':user})
def logout_view(request):
    logout(request)
    return redirect('login')
