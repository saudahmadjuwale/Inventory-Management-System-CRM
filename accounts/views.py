from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Tenant
# Create your views here.
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
                return redirect('accounts/owner')
            if user.role == 'admin':
                return redirect('accounts/admin')
            if user.role == 'agent':
                return redirect('accounts/agent')
    return render(request,'authentication/login.html')

def superadmin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('login')  
    tenants = Tenant.objects.all()  
    return render(request, 'dashboard/superadmin.html',{'tenants':tenants})
def add_tenant(request):
    if not request.user.is_superuser:
        return redirect('login')
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        Tenant.objects.create(name=name, email=email)
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
        tenant.delete()

        return redirect('superadmin')

    return redirect('superadmin')