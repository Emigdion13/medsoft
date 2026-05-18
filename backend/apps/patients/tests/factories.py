"""Factories for Patient model."""
import uuid
from datetime import date, timedelta

import factory
from factory.django import DjangoModelFactory

from apps.core.organizations.tests.factories import OrganizationFactory
from apps.patients.models import Patient


class PatientFactory(DjangoModelFactory):
    """Factory for creating Patient instances."""

    id = factory.LazyFunction(uuid.uuid4)
    organization = factory.SubFactory(OrganizationFactory)
    identity_type = 'CEDULA'
    cedula = factory.Sequence(lambda n: f"{n:013d}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    birth_date = factory.LazyFunction(lambda: date.today() - timedelta(days=365 * 40))
    sex = 'M'
    nationality = 'DOMINICANA'
    phone_primary = factory.Faker("phone_number")
    email = factory.LazyAttribute(lambda obj: f"{obj.first_name.lower()}.{obj.last_name.lower()}@example.com")
    status = 'ACTIVO'

    class Meta:
        model = Patient
        django_get_or_create = ("cedula",)
