import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_docker")

import pytest
from django.conf import settings

# Configure Django before importing models
import django
django.setup()

from apps.core.organizations.models import Organization
from apps.core.users.models import User
from apps.doctors.models import Doctor, Specialty
from apps.patients.models import Patient
from apps.imaging.models import ImagingTypeCatalog, ImagingOrder, ImagingReport


pytestmark = pytest.mark.django_db(transaction=True)


class TestImagingTypeCatalog:
    """Test ImagingTypeCatalog model."""

    @pytest.fixture
    def org(self):
        """Create a test organization."""
        return Organization.objects.get_or_create(
            name="Test Organization",
            defaults={
                "phone": "+1234567890",
                "email": "test@example.com",
                "address": "123 Test St"
            }
        )[0]

    def test_create_imaging_type_catalog(self, org):
        """Test creating an imaging type catalog entry."""
        catalog = ImagingTypeCatalog.objects.create(
            code="CXR",
            name="Chest X-ray",
            modality="RX",
            is_active=True
        )
        
        assert catalog.code == "CXR"
        assert catalog.name == "Chest X-ray"
        assert catalog.modality == "RX"

    def test_imaging_type_catalog_str(self, org):
        """Test string representation of imaging type catalog."""
        catalog = ImagingTypeCatalog.objects.create(
            code="MRI_BRAIN",
            name="Brain MRI",
            modality="MRI",
            is_active=True
        )
        
        assert str(catalog) == "MRI_BRAIN — Brain MRI"

    def test_imaging_type_catalog_is_active_default(self, org):
        """Test that imaging type catalog defaults to is_active=True."""
        catalog = ImagingTypeCatalog.objects.create(
            code="CXR",
            name="Chest X-ray",
            modality="RX"
        )
        
        assert catalog.is_active is True

    def test_imaging_type_catalog_unique_code(self, org):
        """Test that imaging type code must be unique."""
        ImagingTypeCatalog.objects.create(
            code="CXR",
            name="Chest X-ray",
            modality="RX"
        )
        
        with pytest.raises(Exception):
            ImagingTypeCatalog.objects.create(
                code="CXR",
                name="Different CXR",
                modality="RX"
            )


class TestImagingOrder:
    """Test ImagingOrder model."""

    @pytest.fixture
    def org(self):
        """Create a test organization."""
        return Organization.objects.get_or_create(
            name="Test Organization",
            defaults={
                "phone": "+1234567890",
                "email": "test@example.com",
                "address": "123 Test St"
            }
        )[0]

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

    @pytest.fixture
    def doctor(self, org):
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
        user.role = 'DOCTOR'
        user.save()

        specialty = Specialty.objects.get_or_create(
            code="GEN",
            defaults={
                "name": "General Practice",
                "description": "General medical practice"
            }
        )[0]

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
    def user(self, org):
        """Create a test user."""
        return User.objects.create_user(
            username=f"user_{org.id}",
            email=f"user_{org.id}@test.com",
            first_name="Test",
            last_name="User",
            password="testpass123",
            organization_id=org.id
        )

    @pytest.fixture
    def imaging_type(self, org):
        """Create an imaging type catalog."""
        return ImagingTypeCatalog.objects.create(
            code="CXR",
            name="Chest X-ray",
            modality="RX"
        )

    def test_create_imaging_order(self, org, patient, doctor, user, imaging_type):
        """Test creating an imaging order."""
        order = ImagingOrder.objects.create(
            organization=org,
            patient=patient,
            doctor=doctor,
            created_by=user,
            imaging_type=imaging_type,
            order_number="IMG-001",
            priority="NORMAL",
            status="PENDIENTE",
            clinical_indication="Chest pain evaluation"
        )
        
        assert order.organization == org
        assert order.patient == patient
        assert order.doctor == doctor
        assert order.created_by == user
        assert order.imaging_type == imaging_type
        assert order.order_number == "IMG-001"

    def test_imaging_order_str(self, org, patient, doctor, user, imaging_type):
        """Test string representation of imaging order."""
        order = ImagingOrder.objects.create(
            organization=org,
            patient=patient,
            doctor=doctor,
            created_by=user,
            imaging_type=imaging_type,
            order_number="IMG-002",
            clinical_indication="Brain scan"
        )
        
        expected = f"IMG-002 — {patient}"
        assert str(order) == expected

    def test_imaging_order_default_priority(self, org, patient, doctor, user, imaging_type):
        """Test that imaging order defaults to NORMAL priority."""
        order = ImagingOrder.objects.create(
            organization=org,
            patient=patient,
            doctor=doctor,
            created_by=user,
            imaging_type=imaging_type,
            order_number="IMG-003",
            clinical_indication="Default status test"
        )
        
        assert order.priority == "NORMAL"

    def test_imaging_order_default_status(self, org, patient, doctor, user, imaging_type):
        """Test that imaging order defaults to PENDIENTE status."""
        order = ImagingOrder.objects.create(
            organization=org,
            patient=patient,
            doctor=doctor,
            created_by=user,
            imaging_type=imaging_type,
            order_number="IMG-004",
            clinical_indication="Default status test"
        )
        
        assert order.status == "PENDIENTE"


class TestImagingReport:
    """Test ImagingReport model."""

    @pytest.fixture
    def org(self):
        """Create a test organization."""
        return Organization.objects.get_or_create(
            name="Test Organization",
            defaults={
                "phone": "+1234567890",
                "email": "test@example.com",
                "address": "123 Test St"
            }
        )[0]

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

    @pytest.fixture
    def doctor(self, org):
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
        user.role = 'DOCTOR'
        user.save()

        specialty = Specialty.objects.get_or_create(
            code="GEN",
            defaults={
                "name": "General Practice",
                "description": "General medical practice"
            }
        )[0]

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
    def user(self, org):
        """Create a test user."""
        return User.objects.create_user(
            username=f"user_{org.id}",
            email=f"user_{org.id}@test.com",
            first_name="Test",
            last_name="User",
            password="testpass123",
            organization_id=org.id
        )

    @pytest.fixture
    def technician(self, org):
        """Create a test technician user."""
        user = User.objects.create_user(
            username=f"tech_{org.id}",
            email=f"tech_{org.id}@test.com",
            first_name="Tech",
            last_name="User",
            password="testpass123",
            organization_id=org.id
        )
        return user

    @pytest.fixture
    def radiologist(self, org):
        """Create a test radiologist user."""
        user = User.objects.create_user(
            username=f"rad_{org.id}",
            email=f"rad_{org.id}@test.com",
            first_name="Radiology",
            last_name="Doctor",
            password="testpass123",
            organization_id=org.id
        )
        user.role = 'DOCTOR'
        user.save()
        return user

    @pytest.fixture
    def order(self, org, patient, doctor, user):
        """Create a test imaging order."""
        imaging_type = ImagingTypeCatalog.objects.create(
            code="CXR",
            name="Chest X-ray",
            modality="RX"
        )
        return ImagingOrder.objects.create(
            organization=org,
            patient=patient,
            doctor=doctor,
            created_by=user,
            imaging_type=imaging_type,
            order_number="IMG-REP-001",
            clinical_indication="Chest X-ray"
        )

    def test_create_imaging_report(self, order, technician):
        """Test creating an imaging report."""
        report = ImagingReport.objects.create(
            imaging_order=order,
            technician_user=technician,
            findings="Clear lung fields, no acute cardiopulmonary abnormality.",
            impression="Normal chest radiograph",
            status="BORRADOR"
        )
        
        assert report.imaging_order == order
        assert report.technician_user == technician
        assert report.findings == "Clear lung fields, no acute cardiopulmonary abnormality."
        assert report.impression == "Normal chest radiograph"

    def test_imaging_report_str(self, order, technician):
        """Test string representation of imaging report."""
        report = ImagingReport.objects.create(
            imaging_order=order,
            technician_user=technician,
            findings="Findings",
            impression="Impression",
            status="BORRADOR"
        )
        
        expected = f"{order} — BORRADOR"
        assert str(report) == expected

    def test_imaging_report_default_status(self, order, technician):
        """Test that imaging report defaults to BORRADOR status."""
        report = ImagingReport.objects.create(
            imaging_order=order,
            technician_user=technician,
            findings="Default",
            impression="Default"
        )
        
        assert report.status == "BORRADOR"

    def test_imaging_report_with_radiologist(self, order, technician, radiologist):
        """Test creating an imaging report with a radiologist."""
        report = ImagingReport.objects.create(
            imaging_order=order,
            technician_user=technician,
            radiologist_user=radiologist,
            findings="Normal study.",
            impression="No acute finding.",
            status="PENDIENTE"
        )
        
        assert report.radiologist_user == radiologist

    def test_imaging_report_with_recommendations(self, order, technician):
        """Test creating an imaging report with recommendations."""
        report = ImagingReport.objects.create(
            imaging_order=order,
            technician_user=technician,
            findings="Findings",
            impression="Impression",
            recommendations="Follow-up recommended in 6 months.",
            status="BORRADOR"
        )
        
        assert report.recommendations == "Follow-up recommended in 6 months."

    def test_imaging_report_content_hash(self, order, technician):
        """Test creating an imaging report with content hash."""
        report = ImagingReport.objects.create(
            imaging_order=order,
            technician_user=technician,
            findings="Findings",
            impression="Impression",
            status="BORRADOR",
            content_hash="a1b2c3d4e5f6"
        )
        
        assert report.content_hash == "a1b2c3d4e5f6"
