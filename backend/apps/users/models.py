# PATH: apps/users/models.py

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
import secrets
from datetime import timedelta
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        extra_fields.setdefault('role', 'customer')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = [
        ('admin',      'Admin'),
        ('moderator',  'Moderator'),  # will be used later
        ('customer',   'Customer'),
    ]

    name            = models.CharField(max_length=255)
    email           = models.EmailField(unique=True)
    phone           = models.CharField(max_length=20, blank=True, null=True)
    role            = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    # True once the user clicks the link sent by send-verification-email/.
    # Kept separate from is_active so an unverified account can still log in
    # (we just show a "please verify" banner) rather than being locked out.
    email_verified  = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.email} ({self.role})'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_customer(self):
        return self.role == 'customer'


class UserSession(models.Model):
    """
    Tracks one row per login (per device/browser). This is what makes the
    "Active Sessions" feature on the frontend possible — without this table,
    JWT alone has no concept of "sessions" at all (it's stateless by design).

    A row is created every time a user logs in successfully (see LoginView).
    It stores the refresh token's unique ID (jti) so we can blacklist that
    SPECIFIC session later without logging out every other device.
    """
    user           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sessions')
    refresh_jti    = models.CharField(max_length=255, unique=True, help_text='JWT ID of the refresh token for this session')
    device         = models.CharField(max_length=255, blank=True, default='Unknown device')
    browser        = models.CharField(max_length=100, blank=True, default='Unknown browser')
    ip_address     = models.GenericIPAddressField(null=True, blank=True)
    location       = models.CharField(max_length=255, blank=True, default='Unknown')
    last_active    = models.DateTimeField(auto_now=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_sessions'
        ordering = ['-last_active']

    def __str__(self):
        return f'{self.user.email} — {self.device} ({self.browser})'


class TwoFactorAuth(models.Model):
    """
    One row per user. Stores the TOTP secret used to generate/verify the
    6-digit codes shown in apps like Google Authenticator.

    is_enabled becomes True only AFTER the user scans the QR code and
    successfully verifies one code — this proves they actually set up
    their authenticator app correctly before we start requiring it.
    """
    user        = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='two_factor')
    secret      = models.CharField(max_length=64)
    is_enabled  = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'two_factor_auth'

    def __str__(self):
        return f'2FA for {self.user.email} ({"enabled" if self.is_enabled else "pending"})'


class EmailVerification(models.Model):
    """
    One row per verification email sent. The token is single-use (is_used
    flips to True once consumed) and expires after 24 hours by default,
    matching the same pattern used for password reset links.
    """
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_verifications')
    token       = models.CharField(max_length=64, unique=True)
    is_used     = models.BooleanField(default=False)
    expires_at  = models.DateTimeField()
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'email_verifications'

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    @classmethod
    def create_for_user(cls, user, validity_hours=24):
        return cls.objects.create(
            user=user,
            token=secrets.token_urlsafe(32),
            expires_at=timezone.now() + timedelta(hours=validity_hours),
        )