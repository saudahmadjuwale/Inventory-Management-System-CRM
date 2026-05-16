from django.db import models
from django.contrib.auth.models import AbstractUser


class Tenant(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

    role = models.CharField(
    max_length=20,
    choices=[
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('agent', 'Agent'),
    ],
    default='agent'
)

    is_password_set = models.BooleanField(default=False)
    setup_token = models.CharField(max_length=255, null=True, blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)