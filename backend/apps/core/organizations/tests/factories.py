"""Factories for Organization model."""
import factory
from factory.django import DjangoModelFactory

from apps.core.organizations.models import Organization


class OrganizationFactory(DjangoModelFactory):
    """Factory for creating Organization instances."""

    name = factory.Sequence(lambda n: f"Organization {n}")
    phone = factory.Faker("phone_number")
    email = factory.LazyAttribute(lambda obj: f"{obj.name.replace(' ', '.').lower()}@example.com")
    address = factory.Faker("address")

    class Meta:
        model = Organization
        django_get_or_create = ("name",)
