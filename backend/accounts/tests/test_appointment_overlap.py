import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_docker")

import pytest
from django.conf import settings

# Configure Django before importing models
import django
django.setup()

from accounts.serializers import AppointmentSerializer
from apps.core.organizations.models import Organization
from apps.doctors.models import Doctor, Specialty
from apps.patients.models import Patient
from apps.appointments.models import Appointment


pytestmark = pytest.mark.django_db(transaction=True)


class TestAppointmentOverlapValidation:
    """Test appointment overlap validation in the serializer."""

    @pytest.fixture
    def org(self):
        """Create a test organization."""
        return Organization.objects.create(
            name="Test Organization",
            phone="+1234567890",
            email="test@example.com",
            address="123 Test St"
        )

    @pytest.fixture
    def specialty(self):
        """Create a specialty for doctors."""
        return Specialty.objects.create(
            code="GEN",
            name="General Practice",
            description="General medical practice"
        )

    @pytest.fixture
    def doctor(self, org, specialty):
        """Create a test doctor."""
        from apps.core.users.models import User

        user = User.objects.create_user(
            username=f"doctor_{org.id}",
            email=f"doctor_{org.id}@test.com",
            first_name="John",
            last_name="Doe",
            password="testpass123",
            organization_id=org.id
        )
        # Set role directly since it's not passed to create_user
        user.role = 'DOCTOR'
        user.save()

        return Doctor.objects.create(
            user=user,
            cedula="MED123456",
            license_number="LIC789012",
            first_name="John",
            last_name="Doe",
            specialty_main=specialty,
            phone="+1234567890",
            email=f"doctor_{org.id}@test.com",
            organization=org
        )

    @pytest.fixture
    def patient(self, org):
        """Create a test patient."""
        return Patient.objects.create(
            identity_type='CEDULA',
            cedula="12345678901",
            first_name="Jane",
            last_name="Smith",
            birth_date="1990-01-01",
            sex="F",
            nationality="DOMINICANA",
            phone_primary="+1234567891",
            email=f"patient_{org.id}@test.com",
            organization=org,
            status='ACTIVO'
        )

    def test_valid_appointment_creation(self, doctor, patient):
        """Test that a valid non-overlapping appointment can be created."""
        from datetime import datetime, timezone

        start_at = datetime(2026, 4, 30, 10, 0, tzinfo=timezone.utc)
        end_at = datetime(2026, 4, 30, 11, 0, tzinfo=timezone.utc)

        serializer = AppointmentSerializer(data={
            'doctor_id': str(doctor.id),
            'patient_id': str(patient.id),
            'start_at': start_at.isoformat(),
            'end_at': end_at.isoformat(),
            'status': 'PROGRAMADA',
            'reason': 'Test appointment'
        }, context={'request': None})
        
        assert serializer.is_valid(), f"Expected valid data, got errors: {serializer.errors}"
        appt = serializer.save(organization=doctor.organization)
        
        assert appt.doctor == doctor
        assert appt.patient == patient
        assert appt.start_at == start_at
        assert appt.end_at == end_at

    def test_overlapping_appointment_rejected(self, doctor, patient):
        """Test that overlapping appointment is rejected."""
        from datetime import datetime, timezone

        # Create first appointment
        start1 = datetime(2026, 4, 30, 10, 0, tzinfo=timezone.utc)
        end1 = datetime(2026, 4, 30, 11, 0, tzinfo=timezone.utc)
        
        serializer1 = AppointmentSerializer(data={
            'doctor_id': str(doctor.id),
            'patient_id': str(patient.id),
            'start_at': start1.isoformat(),
            'end_at': end1.isoformat(),
            'status': 'PROGRAMADA',
            'reason': 'First appointment'
        }, context={'request': None})
        assert serializer1.is_valid(), f"Expected valid data, got errors: {serializer1.errors}"
        appt1 = serializer1.save(organization=doctor.organization)

        # Try to create overlapping appointment
        start2 = datetime(2026, 4, 30, 10, 30, tzinfo=timezone.utc)
        end2 = datetime(2026, 4, 30, 11, 30, tzinfo=timezone.utc)

        serializer2 = AppointmentSerializer(data={
            'doctor_id': str(doctor.id),
            'patient_id': str(patient.id),
            'start_at': start2.isoformat(),
            'end_at': end2.isoformat(),
            'status': 'PROGRAMADA',
            'reason': 'Overlapping appointment'
        }, context={'request': None})
        
        assert not serializer2.is_valid()
        assert 'start_at' in serializer2.errors
        assert 'end_at' in serializer2.errors

    def test_non_overlapping_appointment_allowed(self, doctor, patient):
        """Test that non-overlapping appointments are allowed."""
        from datetime import datetime, timezone

        # Create first appointment
        start1 = datetime(2026, 4, 30, 10, 0, tzinfo=timezone.utc)
        end1 = datetime(2026, 4, 30, 11, 0, tzinfo=timezone.utc)
        
        serializer1 = AppointmentSerializer(data={
            'doctor_id': str(doctor.id),
            'patient_id': str(patient.id),
            'start_at': start1.isoformat(),
            'end_at': end1.isoformat(),
            'status': 'PROGRAMADA',
            'reason': 'First appointment'
        }, context={'request': None})
        assert serializer1.is_valid(), f"Expected valid data, got errors: {serializer1.errors}"
        appt1 = serializer1.save(organization=doctor.organization)

        # Try to create non-overlapping appointment (starts when first ends)
        start2 = datetime(2026, 4, 30, 11, 0, tzinfo=timezone.utc)
        end2 = datetime(2026, 4, 30, 12, 0, tzinfo=timezone.utc)

        serializer2 = AppointmentSerializer(data={
            'doctor_id': str(doctor.id),
            'patient_id': str(patient.id),
            'start_at': start2.isoformat(),
            'end_at': end2.isoformat(),
            'status': 'PROGRAMADA',
            'reason': 'Next appointment'
        }, context={'request': None})
        
        assert serializer2.is_valid(), f"Expected valid data, got errors: {serializer2.errors}"
        appt2 = serializer2.save(organization=doctor.organization)

        # Verify both appointments exist
        assert Appointment.objects.filter(pk=appt1.pk).exists()
        assert Appointment.objects.filter(pk=appt2.pk).exists()

    def test_appointment_start_before_end_validation(self, doctor, patient):
        """Test that start_at must be before end_at."""
        from datetime import datetime, timezone

        # Same time for start and end (invalid)
        serializer = AppointmentSerializer(data={
            'doctor_id': str(doctor.id),
            'patient_id': str(patient.id),
            'start_at': datetime(2026, 4, 30, 10, 0, tzinfo=timezone.utc).isoformat(),
            'end_at': datetime(2026, 4, 30, 10, 0, tzinfo=timezone.utc).isoformat(),
            'status': 'PROGRAMADA',
            'reason': 'Invalid time range'
        }, context={'request': None})
        
        assert not serializer.is_valid()
        assert 'end_at' in serializer.errors

    def test_no_overlap_different_doctors(self, org, patient):
        """Test that same time slot is allowed for different doctors."""
        from datetime import datetime, timezone
        from apps.core.users.models import User

        specialty = Specialty.objects.first()
        if not specialty:
            specialty = Specialty.objects.create(
                code="GEN2",
                name="General Practice 2",
                description="Second general practice"
            )

        user1 = User.objects.create_user(
            username=f"doctor1_{org.id}",
            email=f"doctor1_{org.id}@test.com",
            first_name="Doctor",
            last_name="One",
            password="testpass123",
            organization_id=org.id
        )
        user1.role = 'DOCTOR'
        user1.save()

        doctor1 = Doctor.objects.create(
            user=user1,
            cedula="MED000001",
            license_number="LIC000001",
            first_name="Doctor",
            last_name="One",
            specialty_main=specialty,
            phone="+1234567890",
            email=f"doctor1_{org.id}@test.com",
            organization=org
        )

        user2 = User.objects.create_user(
            username=f"doctor2_{org.id}",
            email=f"doctor2_{org.id}@test.com",
            first_name="Doctor",
            last_name="Two",
            password="testpass123",
            organization_id=org.id
        )
        user2.role = 'DOCTOR'
        user2.save()

        doctor2 = Doctor.objects.create(
            user=user2,
            cedula="MED000002",
            license_number="LIC000002",
            first_name="Doctor",
            last_name="Two",
            specialty_main=specialty,
            phone="+1234567891",
            email=f"doctor2_{org.id}@test.com",
            organization=org
        )

        start_at = datetime(2026, 4, 30, 10, 0, tzinfo=timezone.utc)
        end_at = datetime(2026, 4, 30, 11, 0, tzinfo=timezone.utc)

        # Appointment for doctor 1
        serializer1 = AppointmentSerializer(data={
            'doctor_id': str(doctor1.id),
            'patient_id': str(patient.id),
            'start_at': start_at.isoformat(),
            'end_at': end_at.isoformat(),
            'status': 'PROGRAMADA',
            'reason': 'Doctor 1 appointment'
        }, context={'request': None})
        assert serializer1.is_valid(), f"Expected valid data, got errors: {serializer1.errors}"
        appt1 = serializer1.save(organization=org)

        # Appointment for doctor 2 at same time (should be allowed)
        serializer2 = AppointmentSerializer(data={
            'doctor_id': str(doctor2.id),
            'patient_id': str(patient.id),
            'start_at': start_at.isoformat(),
            'end_at': end_at.isoformat(),
            'status': 'PROGRAMADA',
            'reason': 'Doctor 2 appointment'
        }, context={'request': None})
        
        assert serializer2.is_valid(), f"Expected valid data, got errors: {serializer2.errors}"
        appt2 = serializer2.save(organization=org)

        # Both appointments should exist
        assert Appointment.objects.filter(pk=appt1.pk).exists()
        assert Appointment.objects.filter(pk=appt2.pk).exists()

    def test_nested_appointment_rejected(self, doctor, patient):
        """Test that nested appointments (one completely inside another) are rejected."""
        from datetime import datetime, timezone

        # Create first appointment (10:00-12:00)
        start1 = datetime(2026, 4, 30, 10, 0, tzinfo=timezone.utc)
        end1 = datetime(2026, 4, 30, 12, 0, tzinfo=timezone.utc)
        
        serializer1 = AppointmentSerializer(data={
            'doctor_id': str(doctor.id),
            'patient_id': str(patient.id),
            'start_at': start1.isoformat(),
            'end_at': end1.isoformat(),
            'status': 'PROGRAMADA',
            'reason': 'First appointment'
        }, context={'request': None})
        assert serializer1.is_valid(), f"Expected valid data, got errors: {serializer1.errors}"
        appt1 = serializer1.save(organization=doctor.organization)

        # Try to create nested appointment (10:30-11:30)
        start2 = datetime(2026, 4, 30, 10, 30, tzinfo=timezone.utc)
        end2 = datetime(2026, 4, 30, 11, 30, tzinfo=timezone.utc)

        serializer2 = AppointmentSerializer(data={
            'doctor_id': str(doctor.id),
            'patient_id': str(patient.id),
            'start_at': start2.isoformat(),
            'end_at': end2.isoformat(),
            'status': 'PROGRAMADA',
            'reason': 'Nested appointment'
        }, context={'request': None})
        
        assert not serializer2.is_valid()
        assert 'start_at' in serializer2.errors

    def test_adjacent_appointments_allowed(self, doctor, patient):
        """Test that adjacent appointments (end of one = start of next) are allowed."""
        from datetime import datetime, timezone

        # Create first appointment
        start1 = datetime(2026, 4, 30, 10, 0, tzinfo=timezone.utc)
        end1 = datetime(2026, 4, 30, 11, 0, tzinfo=timezone.utc)
        
        serializer1 = AppointmentSerializer(data={
            'doctor_id': str(doctor.id),
            'patient_id': str(patient.id),
            'start_at': start1.isoformat(),
            'end_at': end1.isoformat(),
            'status': 'PROGRAMADA',
            'reason': 'First appointment'
        }, context={'request': None})
        assert serializer1.is_valid(), f"Expected valid data, got errors: {serializer1.errors}"
        appt1 = serializer1.save(organization=doctor.organization)

        # Create adjacent appointment starting exactly when first ends
        start2 = end1  # Exactly when first appointment ends
        end2 = datetime(2026, 4, 30, 12, 0, tzinfo=timezone.utc)

        serializer2 = AppointmentSerializer(data={
            'doctor_id': str(doctor.id),
            'patient_id': str(patient.id),
            'start_at': start2.isoformat(),
            'end_at': end2.isoformat(),
            'status': 'PROGRAMADA',
            'reason': 'Adjacent appointment'
        }, context={'request': None})
        
        assert serializer2.is_valid(), f"Expected valid data, got errors: {serializer2.errors}"
        appt2 = serializer2.save(organization=doctor.organization)

        # Both should exist
        assert Appointment.objects.filter(pk=appt1.pk).exists()
        assert Appointment.objects.filter(pk=appt2.pk).exists()

    def test_update_appointment_allows_same_slot(self, doctor, patient):
        """Test that updating an appointment doesn't flag its own slot as overlap."""
        from datetime import datetime, timezone

        # Create initial appointment
        start = datetime(2026, 4, 30, 10, 0, tzinfo=timezone.utc)
        end = datetime(2026, 4, 30, 11, 0, tzinfo=timezone.utc)
        
        serializer = AppointmentSerializer(data={
            'doctor_id': str(doctor.id),
            'patient_id': str(patient.id),
            'start_at': start.isoformat(),
            'end_at': end.isoformat(),
            'status': 'PROGRAMADA',
            'reason': 'Initial appointment'
        }, context={'request': None})
        assert serializer.is_valid(), f"Expected valid data, got errors: {serializer.errors}"
        appt = serializer.save(organization=doctor.organization)

        # Update the appointment (same times)
        update_serializer = AppointmentSerializer(
            appt,
            data={
                'doctor_id': str(doctor.id),
                'patient_id': str(patient.id),
                'start_at': start.isoformat(),
                'end_at': end.isoformat(),
                'status': 'PROGRAMADA',
                'reason': 'Updated reason'
            },
            context={'request': None}
        )
        
        assert update_serializer.is_valid(), f"Expected valid data, got errors: {update_serializer.errors}"
        updated_appt = update_serializer.save()

        # Verify the update worked
        assert updated_appt.reason == "Updated reason"
