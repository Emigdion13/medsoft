"""Factories for Encounter model."""
import uuid
from datetime import datetime, timedelta

import factory
from factory.django import DjangoModelFactory

from apps.core.organizations.tests.factories import OrganizationFactory
from apps.core.users.tests.factories import UserFactory
from apps.doctors.tests.factories import DoctorFactory
from apps.patients.tests.factories import PatientFactory
from apps.encounters.models import Encounter


class EncounterFactory(DjangoModelFactory):
    """Factory for creating Encounter instances."""

    id = factory.LazyFunction(uuid.uuid4)
    organization = factory.SubFactory(OrganizationFactory)
    patient = factory.SubFactory(PatientFactory)
    doctor = factory.SubFactory(DoctorFactory)
    encounter_type = 'AMBULATORIO'
    status = 'ABIERTO'
    start_at = factory.LazyFunction(lambda: datetime.now() - timedelta(hours=1))
    end_at = None
    chief_complaint = factory.Faker("sentence")

    class Meta:
        model = Encounter
        django_get_or_create = None
