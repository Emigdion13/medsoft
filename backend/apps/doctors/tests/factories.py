"""Factories for Doctor model."""
import uuid

import factory
from factory.django import DjangoModelFactory

from apps.core.organizations.tests.factories import OrganizationFactory
from apps.core.users.tests.factories import UserFactory
from apps.doctors.models import Doctor, Specialty


class SpecialtyFactory(DjangoModelFactory):
    """Factory for creating Specialty instances."""

    code = factory.Sequence(lambda n: f"SPEC{n:03d}")
    name = factory.Sequence(lambda n: f"Specialty {n}")
    description = factory.Faker("sentence")
    is_active = True

    class Meta:
        model = Specialty


class DoctorFactory(DjangoModelFactory):
    """Factory for creating Doctor instances."""

    id = factory.LazyFunction(uuid.uuid4)
    organization = factory.SubFactory(OrganizationFactory)
    user = factory.SubFactory(UserFactory)
    cedula = factory.Sequence(lambda n: f"{n:013d}")
    license_number = factory.Sequence(lambda n: f"LIC{n:06d}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    specialty_main = factory.SubFactory(SpecialtyFactory)
    phone = factory.Faker("phone_number")
    email = factory.LazyAttribute(lambda obj: f"{obj.first_name.lower()}.{obj.last_name.lower()}@doctor.com")
    is_active = True

    class Meta:
        model = Doctor
        django_get_or_create = ("cedula",)
