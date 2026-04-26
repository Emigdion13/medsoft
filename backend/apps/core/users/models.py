import uuid

from django.contrib.auth.hashers import make_password, check_password
from django.db import models


class UserManager(models.Manager):
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
            email=email.lower(),
            first_name=first_name,
            last_name=last_name,
            organization_id=organization_id,
        )
        user.password_hash = make_password(password)
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
        user.save(using=self._db)
        return user


class User(models.Model):
    """Identidad de usuarios del sistema (auth)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'core_organizations.Organization',
        on_delete=models.PROTECT,
        db_column='organization_id',
    )
    username = models.CharField(max_length=150)
    email = models.EmailField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password_hash = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def check_password(self, raw_password: str) -> bool:
        """Check if the password matches the stored hash."""
        return check_password(raw_password, self.password_hash)

    def set_password(self, raw_password: str) -> None:
        """Set the user's password with hashed value."""
        self.password_hash = make_password(raw_password)

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
        indexes = [
            models.Index(fields=['organization'], name='user_org_idx'),
            models.Index(fields=['is_active'], name='user_is_active_idx'),
            models.Index(
                fields=['deleted_at'], name='user_deleted_at_idx'
            ),
        ]

    def __str__(self):
        return self.full_name
