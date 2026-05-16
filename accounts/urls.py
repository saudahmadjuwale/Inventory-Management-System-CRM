from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('login',views.login_view,name='login'),
    # superadmin
    path('superadmin',views.superadmin_dashboard,name='superadmin'),
    path('add-tenant/', views.add_tenant, name='add-tenant'),
    path('update-tenant/<int:id>/', views.update_tenant, name='update-tenant'),
    path('delete-tenant/<int:id>/', views.delete_tenant, name='delete-tenant'),
    path('hard-delete-tenant/<int:id>/', views.hard_delete_tenant, name='hard-delete-tenant'),
    path('tenant/<int:id>/', views.tenant_detail, name='tenant_detail'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit-user'),
    # path('setup/<str:token>/', views.setup_password, name='setup_password'),
    path('owner',views.owner_dashboard,name='owner'),
    path('logout/', views.logout_view, name='logout')
]
