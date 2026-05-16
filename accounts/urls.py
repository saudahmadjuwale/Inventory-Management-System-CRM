from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('login',views.login_view,name='login'),
    # superadmin
    path('superadmin',views.superadmin_dashboard,name='superadmin'),
    path('add-tenant/', views.add_tenant, name='add-tenant'),
    path('update-tenant/<int:id>/', views.update_tenant, name='update-tenant'),
    path('delete-tenant/<int:id>/', views.delete_tenant, name='delete-tenant'),
    path('hard-delete-tenant/<int:id>/', views.hard_delete_tenant, name='hard-delete-tenant'),
]
