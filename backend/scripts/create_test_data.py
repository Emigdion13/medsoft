#!/usr/bin/env python
"""Create test data for MediSoft development/testing."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_docker')
django.setup()

from datetime import datetime, timedelta
from apps.core.organizations.models import Organization
from apps.doctors.models import Specialty, Doctor
from apps.patients.models import Patient
from apps.appointments.models import Appointment
from apps.core.users.models import User


def create_test_data():
    print("Creating test data...")

    # 1. Create organization
    org, _ = Organization.objects.get_or_create(
        name='MediSoft Clinic',
        defaults={
            'address': 'Main Street 123',
            'phone': '+1234567890'
        }
    )
    print(f"✓ Organization: {org.name}")

    # 2. Create specialty
    spec, _ = Specialty.objects.get_or_create(
        code='GEN',
        defaults={
            'name': 'General Medicine',
            'description': 'General Medical Practice'
        }
    )
    print(f"✓ Specialty: {spec.name}")

    # 3. Create doctor user and profile
    doc_user, _ = User.objects.get_or_create(
        username='doctor',
        defaults={
            'email': 'doctor@medisoft.local',
            'is_active': True,
            'role': 'DOCTOR'
        }
    )
    if not doc_user.password:
        doc_user.set_password('doctor')
        doc_user.save()

    doc, _ = Doctor.objects.get_or_create(
        cedula='1234567',
        defaults={
            'organization': org,
            'user': doc_user,
            'license_number': 'MED-001',
            'first_name': 'John',
            'last_name': 'Doe',
            'specialty_main': spec,
            'phone': '+1234567890',
            'email': 'john@medisoft.local'
        }
    )
    print(f"✓ Doctor: {doc.first_name} {doc.last_name}")

    # 4. Create patient
    pat, _ = Patient.objects.get_or_create(
        cedula='00112345678',
        defaults={
            'organization': org,
            'identity_type': 'CEDULA',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'birth_date': datetime(1990, 1, 1).date(),
            'sex': 'F',
            'nationality': 'DOMINICANA',
            'phone_primary': '+0987654321',
            'email': 'jane@example.com',
            'address': '456 Oak Ave'
        }
    )
    print(f"✓ Patient: {pat.first_name} {pat.last_name}")

    # 5. Create appointment
    from django.utils import timezone
    now = timezone.now()
    appt, created = Appointment.objects.get_or_create(
        organization=org,
        patient=pat,
        doctor=doc,
        start_at=now + timedelta(hours=1),
        end_at=now + timedelta(hours=2),
        defaults={
            'appointment_type': 'CONSULTA',
            'status': 'PROGRAMADA',
            'reason': 'Routine checkup',
        }
    )
    if created:
        print(f"✓ Appointment created: {str(appt.id)[:8]}...")
    else:
        print(f"✓ Appointment already exists: {str(appt.id)[:8]}...")

    # Summary
    print("\n" + "=" * 40)
    print("Summary:")
    print(f"  Organizations: {Organization.objects.count()}")
    print(f"  Specialties: {Specialty.objects.count()}")
    print(f"  Doctors: {Doctor.objects.count()}")
    print(f"  Patients: {Patient.objects.count()}")
    print(f"  Appointments: {Appointment.objects.count()}")


if __name__ == '__main__':
    create_test_data()
