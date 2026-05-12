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
from apps.lab.models import LabTestCatalog, LabOrder, LabOrderItem, LabResult


pytestmark = pytest.mark.django_db(transaction=True)


class TestLabTestCatalog:
    """Test LabTestCatalog model."""

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

    def test_create_lab_test_catalog(self, org):
        """Test creating a lab test catalog entry."""
        catalog = LabTestCatalog.objects.create(
            code="CBC",
            name="Complete Blood Count",
            sample_type="Blood",
            unit="count",
            reference_min=4.0,
            reference_max=11.0,
            is_active=True
        )
        
        assert catalog.code == "CBC"
        assert catalog.name == "Complete Blood Count"
        assert catalog.sample_type == "Blood"
        assert catalog.unit == "count"

    def test_lab_test_catalog_str(self, org):
        """Test string representation of lab test catalog."""
        catalog = LabTestCatalog.objects.create(
            code="GLU",
            name="Glucose",
            sample_type="Serum",
            unit="mg/dL"
        )
        
        assert str(catalog) == "GLU — Glucose"

    def test_lab_test_catalog_is_active_default(self, org):
        """Test that lab test catalog defaults to is_active=True."""
        catalog = LabTestCatalog.objects.create(
            code="CBC",
            name="Complete Blood Count",
            sample_type="Blood"
        )
        
        assert catalog.is_active is True

    def test_lab_test_catalog_unique_code(self, org):
        """Test that lab test code must be unique."""
        LabTestCatalog.objects.create(
            code="CBC",
            name="Complete Blood Count",
            sample_type="Blood"
        )

        with pytest.raises(Exception):
            LabTestCatalog.objects.create(
                code="CBC",
                name="Different CBC",
                sample_type="Blood"
            )


class TestLabOrder:
    """Test LabOrder model."""

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

    def test_create_lab_order(self, org, patient, doctor, user):
        """Test creating a lab order."""
        order = LabOrder.objects.create(
            organization=org,
            patient=patient,
            doctor=doctor,
            created_by=user,
            order_number="LAB-001",
            priority="NORMAL",
            status="PENDIENTE"
        )
        
        assert order.organization == org
        assert order.patient == patient
        assert order.doctor == doctor
        assert order.created_by == user
        assert order.order_number == "LAB-001"

    def test_lab_order_str(self, org, patient, doctor, user):
        """Test string representation of lab order."""
        order = LabOrder.objects.create(
            organization=org,
            patient=patient,
            doctor=doctor,
            created_by=user,
            order_number="LAB-002"
        )
        
        expected = f"LAB-002 — {patient}"
        assert str(order) == expected

    def test_lab_order_default_priority(self, org, patient, doctor, user):
        """Test that lab order defaults to NORMAL priority."""
        order = LabOrder.objects.create(
            organization=org,
            patient=patient,
            doctor=doctor,
            created_by=user,
            order_number="LAB-003"
        )
        
        assert order.priority == "NORMAL"

    def test_lab_order_default_status(self, org, patient, doctor, user):
        """Test that lab order defaults to PENDIENTE status."""
        order = LabOrder.objects.create(
            organization=org,
            patient=patient,
            doctor=doctor,
            created_by=user,
            order_number="LAB-004"
        )
        
        assert order.status == "PENDIENTE"


class TestLabOrderItem:
    """Test LabOrderItem model."""

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
    def order(self, org, patient, doctor, user):
        """Create a test lab order."""
        return LabOrder.objects.create(
            organization=org,
            patient=patient,
            doctor=doctor,
            created_by=user,
            order_number="LAB-ITEM-001"
        )

    @pytest.fixture
    def catalog(self, org):
        """Create a test lab test catalog."""
        return LabTestCatalog.objects.create(
            code="CBC",
            name="Complete Blood Count",
            sample_type="Blood",
            unit="count"
        )

    def test_create_lab_order_item(self, order, catalog):
        """Test creating a lab order item."""
        item = LabOrderItem.objects.create(
            lab_order=order,
            lab_test=catalog
        )
        
        assert item.lab_order == order
        assert item.lab_test == catalog

    def test_lab_order_item_str(self, order, catalog):
        """Test string representation of lab order item."""
        item = LabOrderItem.objects.create(
            lab_order=order,
            lab_test=catalog
        )
        
        expected = f"{order} — {catalog}"
        assert str(item) == expected

    def test_lab_order_item_default_status(self, order, catalog):
        """Test that lab order item defaults to PENDIENTE status."""
        item = LabOrderItem.objects.create(
            lab_order=order,
            lab_test=catalog
        )
        
        assert item.status == "PENDIENTE"


class TestLabResult:
    """Test LabResult model."""

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
    def order(self, org, patient, doctor, user):
        """Create a test lab order."""
        return LabOrder.objects.create(
            organization=org,
            patient=patient,
            doctor=doctor,
            created_by=user,
            order_number="LAB-RESULT-001"
        )

    @pytest.fixture
    def catalog(self, org):
        """Create a test lab test catalog."""
        return LabTestCatalog.objects.create(
            code="CBC",
            name="Complete Blood Count",
            sample_type="Blood",
            unit="count",
            reference_min=4.0,
            reference_max=11.0
        )

    @pytest.fixture
    def item(self, order, catalog):
        """Create a test lab order item."""
        return LabOrderItem.objects.create(
            lab_order=order,
            lab_test=catalog
        )

    @pytest.fixture
    def tech_user(self, org):
        """Create a test technician user."""
        user = User.objects.create_user(
            username=f"tech_{org.id}",
            email=f"tech_{org.id}@test.com",
            first_name="Tech",
            last_name="User",
            password="testpass123",
            organization_id=org.id
        )
        user.role = 'LAB_TECHNICIAN'
        user.save()
        return user

    def test_create_lab_result(self, item, tech_user):
        """Test creating a lab result."""
        result = LabResult.objects.create(
            lab_order_item=item,
            result_numeric=5.0,
            unit="million/µL",
            ref_min=4.0,
            ref_max=11.0,
            result_flag="NORMAL",
            processed_by=tech_user
        )
        
        assert result.lab_order_item == item
        assert result.result_numeric == 5.0
        assert result.unit == "million/µL"
        assert result.ref_min == 4.0
        assert result.ref_max == 11.0

    def test_lab_result_str(self, item, tech_user):
        """Test string representation of lab result."""
        result = LabResult.objects.create(
            lab_order_item=item,
            result_numeric=5.0,
            unit="million/µL",
            result_flag="NORMAL",
            processed_by=tech_user
        )
        
        expected = f"{item} — NORMAL"
        assert str(result) == expected

    def test_lab_result_default_flag(self, item, tech_user):
        """Test that lab result defaults to NORMAL flag."""
        result = LabResult.objects.create(
            lab_order_item=item,
            result_numeric=5.0,
            unit="million/µL",
            processed_by=tech_user
        )
        
        assert result.result_flag == "NORMAL"

    def test_lab_result_anormal_flag(self, item, tech_user):
        """Test creating a lab result with ANORMAL flag."""
        result = LabResult.objects.create(
            lab_order_item=item,
            result_numeric=12.0,
            unit="million/µL",
            ref_min=4.0,
            ref_max=11.0,
            result_flag="ANORMAL",
            processed_by=tech_user
        )
        
        assert result.result_flag == "ANORMAL"

    def test_lab_result_critico_flag(self, item, tech_user):
        """Test creating a lab result with CRITICO flag."""
        result = LabResult.objects.create(
            lab_order_item=item,
            result_numeric=25.0,
            unit="million/µL",
            ref_min=4.0,
            ref_max=11.0,
            result_flag="CRITICO",
            processed_by=tech_user
        )
        
        assert result.result_flag == "CRITICO"
