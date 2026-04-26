import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Custom manager for User model."""

    def create_user(
        self,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        password: str | None = None,
        organization_id: uuid.UUID | None = None,
    ) -> 'User':
        """Create a regular user with hashed password."""
        if not password:
            raise ValueError('Password is required')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            organization_id=organization_id,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        password: str | None = None,
        organization_id: uuid.UUID | None = None,
    ) -> 'User':
        """Create a superuser with hashed password."""
        user = self.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            organization_id=organization_id,
        )
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Identidad de usuarios del sistema (auth)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'core_organizations.Organization',
        on_delete=models.PROTECT,
        db_column='organization_id',
    )
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    role = models.CharField(
        max_length=20,
        choices=[
            ('DOCTOR', 'Doctor'),
            ('NURSE', 'Nurse'),
            ('SECRETARY', 'Secretary'),
            ('RECEPTIONIST', 'Receptionist'),
            ('LAB_TECHNICIAN', 'Lab Technician'),
            ('ADMINISTRATOR', 'Administrator'),
        ],
        default='RECEPTIONIST',
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def email_lower(self) -> str:
        return self.email.lower()

    def check_password(self, raw_password: str) -> bool:
        """Check if the password matches the stored hash."""
        return check_password(raw_password, self.password)

    def set_password(self, raw_password: str) -> None:
        """Set the user's password with hashed value."""
        self.password = make_password(raw_password)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'username'],
                condition=models.Q(deleted_at__isnull=True),
                name='user_org_username_unique',
            ),
            models.UniqueConstraint(
                fields=['organization', 'email'],
                condition=models.Q(deleted_at__isnull=True),
                name='user_org_email_unique',
            ),
        ]

    def __str__(self):
        return self.full_name
