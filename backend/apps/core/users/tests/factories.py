"""Factories for User model."""
import uuid

import factory
from factory.django import DjangoModelFactory

from apps.core.users.models import User


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances."""

    id = factory.LazyFunction(uuid.uuid4)
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")

    class Meta:
        model = User
        django_get_or_create = ("username",)
