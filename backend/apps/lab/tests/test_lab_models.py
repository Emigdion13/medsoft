"""Test suite for lab app models."""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_docker")

import pytest
from django.conf import settings
from django.db import IntegrityError, transaction

# Configure Django before importing models
import django
django.setup()

from uuid import uuid4

pytestmark = pytest.mark.django_db(transaction=True)

from apps.core.organizations.models import Organization
from apps.core.users.models import User
from apps.doctors.models import Doctor, Specialty
from apps.encounters.models import Encounter
from apps.lab.models import LabOrder, LabOrderItem, LabResult, LabTestCatalog
from apps.patients.models import Patient


@pytest.fixture(scope="function")
def unique_org():
    """Create an organization with a unique name."""
    return Organization.objects.create(
        id=uuid4(),
        name=f"Test Org {uuid4()}",
        phone="+1234567890",
        email="test@example.com",
        address="123 Test St"
    )


@pytest.fixture(scope="function")
def unique_user(unique_org):
    """Create a user with a unique email."""
    user = User.objects.create_user(
        username=f"user{uuid4()}",
        email=f"user{unique_org.id}@test.com",
        password="testpass123",
        first_name="Test",
        last_name="User"
    )
    return user


@pytest.fixture(scope="function")
def unique_patient(unique_org):
    """Create a patient with a unique cedula."""
    return Patient.objects.create(
        id=uuid4(),
        organization=unique_org,
        cedula=f"CED{uuid4().hex[:15]}",  # 3 + 15 = 18 chars (within 20 limit)
        first_name="John",
        last_name="Doe",
        birth_date="1980-01-01",
        sex="M"
    )


@pytest.fixture(scope="function")
def unique_doctor(unique_org, unique_user):
    """Create a doctor with required fields."""
    from apps.doctors.models import Specialty

    specialty = Specialty.objects.get_or_create(
        code="FM",
        defaults={"name": "Family Medicine"}
    )[0]

    return Doctor.objects.create(
        organization=unique_org,
        user=unique_user,
        cedula=f"D{uuid4().hex[:17]}",  # 2 + 18 = 20 chars (max for cedula)
        license_number=f"LIC{uuid4().hex[:57]}",  # 3 + 57 = 60 chars (max for license)
        specialty_main=specialty,
        first_name="Test",
        last_name="Doctor"
    )


@pytest.fixture(scope="function")
def unique_encounter(unique_org, unique_patient, unique_doctor, unique_user):
    """Create a unique encounter."""
    from datetime import datetime

    return Encounter.objects.create(
        id=uuid4(),
        organization=unique_org,
        patient=unique_patient,
        doctor=unique_doctor,
        encounter_type="AMBULATORIO",
        status="ABIERTO",
        start_at=datetime.now(),
        created_by=unique_user
    )


@pytest.fixture(scope="function")
def unique_catalog(unique_org):
    """Create a lab test catalog with a unique code."""
    return LabTestCatalog.objects.create(
        id=uuid4(),
        code=f"CBC-{uuid4()}",
        name="Complete Blood Count"
    )


@pytest.mark.django_db
def test_create_lab_test_catalog(unique_org):
    """Test creating a lab test catalog entry."""
    code = f"CBC-{uuid4()}"
    catalog = LabTestCatalog.objects.create(
        id=uuid4(),
        code=code,
        name="Complete Blood Count",
        is_active=True
    )

    assert catalog.code == code
    assert catalog.name == "Complete Blood Count"
    assert catalog.is_active is True


@pytest.mark.django_db
def test_lab_test_catalog_str(unique_org):
    """Test string representation of lab test catalog."""
    code = f"CBC-{uuid4()}"
    catalog = LabTestCatalog.objects.create(
        id=uuid4(),
        code=code,
        name="Complete Blood Count"
    )

    assert str(catalog) == f"{code}: Complete Blood Count"


@pytest.mark.django_db
def test_lab_test_catalog_is_active_default(unique_org):
    """Test that is_active defaults to True."""
    catalog = LabTestCatalog.objects.create(
        id=uuid4(),
        code=f"CBC-{uuid4()}",
        name="Complete Blood Count"
    )

    assert catalog.is_active is True


@pytest.mark.django_db
def test_lab_test_catalog_unique_code(unique_org):
    """Test that code must be unique."""
    code = f"CBC-{uuid4()}"
    LabTestCatalog.objects.create(
        id=uuid4(),
        code=code,
        name="First CBC"
    )

    with pytest.raises(IntegrityError):
        LabTestCatalog.objects.create(
            id=uuid4(),
            code=code,
            name="Second CBC"
        )


@pytest.mark.django_db
def test_create_lab_order(unique_patient, unique_doctor, unique_org, unique_user, unique_encounter):
    """Test creating a lab order."""
    catalog = LabTestCatalog.objects.create(
        id=uuid4(),
        code=f"CBC-{uuid4()}",
        name="Complete Blood Count"
    )

    order = LabOrder.objects.create(
        patient=unique_patient,
        doctor=unique_doctor,
        organization=unique_org,
        encounter=unique_encounter,
        created_by=unique_user
    )

    item = LabOrderItem.objects.create(
        lab_order=order,
        test=catalog,
        quantity=1
    )

    assert order.patient == unique_patient
    assert order.doctor == unique_doctor
    assert len(order.items.all()) == 1


@pytest.mark.django_db
def test_lab_order_str(unique_patient, unique_doctor, unique_org, unique_user, unique_encounter):
    """Test string representation of lab order."""
    catalog = LabTestCatalog.objects.create(
        id=uuid4(),
        code=f"CBC-{uuid4()}",
        name="Complete Blood Count"
    )

    order = LabOrder.objects.create(
        patient=unique_patient,
        doctor=unique_doctor,
        organization=unique_org,
        encounter=unique_encounter,
        created_by=unique_user
    )

    assert str(order) == f"Lab Order #{order.id} - {unique_patient.last_name}, {unique_patient.first_name}"


@pytest.mark.django_db
def test_lab_order_default_priority(unique_patient, unique_doctor, unique_org, unique_user, unique_encounter):
    """Test that priority defaults to NORMAL."""
    order = LabOrder.objects.create(
        patient=unique_patient,
        doctor=unique_doctor,
        organization=unique_org,
        encounter=unique_encounter,
        created_by=unique_user
    )

    assert order.priority == "NORMAL"


@pytest.mark.django_db
def test_lab_order_default_status(unique_patient, unique_doctor, unique_org, unique_user, unique_encounter):
    """Test that status defaults to PENDING."""
    order = LabOrder.objects.create(
        patient=unique_patient,
        doctor=unique_doctor,
        organization=unique_org,
        encounter=unique_encounter,
        created_by=unique_user
    )

    assert order.status == "PENDING"


@pytest.mark.django_db
def test_create_lab_order_item(unique_patient, unique_doctor, unique_org, unique_user, unique_catalog, unique_encounter):
    """Test creating a lab order item."""
    order = LabOrder.objects.create(
        patient=unique_patient,
        doctor=unique_doctor,
        organization=unique_org,
        encounter=unique_encounter,
        created_by=unique_user
    )

    item = LabOrderItem.objects.create(
        lab_order=order,
        test=unique_catalog,
        quantity=2
    )

    assert item.lab_order == order
    assert item.test == unique_catalog
    assert item.quantity == 2


@pytest.mark.django_db
def test_lab_order_item_str(unique_patient, unique_doctor, unique_org, unique_user, unique_catalog, unique_encounter):
    """Test string representation of lab order item."""
    order = LabOrder.objects.create(
        patient=unique_patient,
        doctor=unique_doctor,
        organization=unique_org,
        encounter=unique_encounter,
        created_by=unique_user
    )

    item = LabOrderItem.objects.create(
        lab_order=order,
        test=unique_catalog,
        quantity=1
    )

    assert str(item) == f"{unique_catalog.name} x{item.quantity}"


@pytest.mark.django_db
def test_lab_order_item_default_status(unique_patient, unique_doctor, unique_org, unique_user, unique_catalog, unique_encounter):
    """Test that status defaults to PENDING."""
    order = LabOrder.objects.create(
        patient=unique_patient,
        doctor=unique_doctor,
        organization=unique_org,
        encounter=unique_encounter,
        created_by=unique_user
    )

    item = LabOrderItem.objects.create(
        lab_order=order,
        test=unique_catalog,
        quantity=1
    )

    assert item.status == "PENDING"


@pytest.mark.django_db
def test_create_lab_result(unique_patient, unique_doctor, unique_org, unique_user, unique_catalog, unique_encounter):
    """Test creating a lab result."""
    order = LabOrder.objects.create(
        patient=unique_patient,
        doctor=unique_doctor,
        organization=unique_org,
        encounter=unique_encounter,
        created_by=unique_user
    )

    item = LabOrderItem.objects.create(
        lab_order=order,
        test=unique_catalog,
        quantity=1
    )

    result = LabResult.objects.create(
        order_item=item,
        value="5.0",
        unit="count",
        is_normal=True
    )

    assert result.order_item == item
    assert result.value == "5.0"
    assert result.unit == "count"


@pytest.mark.django_db
def test_lab_result_str(unique_patient, unique_doctor, unique_org, unique_user, unique_catalog, unique_encounter):
    """Test string representation of lab result."""
    order = LabOrder.objects.create(
        patient=unique_patient,
        doctor=unique_doctor,
        organization=unique_org,
        encounter=unique_encounter,
        created_by=unique_user
    )

    item = LabOrderItem.objects.create(
        lab_order=order,
        test=unique_catalog,
        quantity=1
    )

    result = LabResult.objects.create(
        order_item=item,
        value="5.0",
        unit="count"
    )

    assert str(result) == f"{unique_catalog.name}: 5.0 count"


@pytest.mark.django_db
def test_lab_result_default_flag(unique_patient, unique_doctor, unique_org, unique_user, unique_catalog, unique_encounter):
    """Test that is_normal defaults to False."""
    order = LabOrder.objects.create(
        patient=unique_patient,
        doctor=unique_doctor,
        organization=unique_org,
        encounter=unique_encounter,
        created_by=unique_user
    )

    item = LabOrderItem.objects.create(
        lab_order=order,
        test=unique_catalog,
        quantity=1
    )

    result = LabResult.objects.create(
        order_item=item,
        value="5.0",
        unit="count"
    )

    assert result.is_normal is False


@pytest.mark.django_db
def test_lab_result_anormal_flag(unique_patient, unique_doctor, unique_org, unique_user, unique_catalog, unique_encounter):
    """Test that is_abnormal can be set to True."""
    order = LabOrder.objects.create(
        patient=unique_patient,
        doctor=unique_doctor,
        organization=unique_org,
        encounter=unique_encounter,
        created_by=unique_user
    )

    item = LabOrderItem.objects.create(
        lab_order=order,
        test=unique_catalog,
        quantity=1
    )

    result = LabResult.objects.create(
        order_item=item,
        value="2.0",
        unit="count",
        is_abnormal=True
    )

    assert result.is_abnormal is True


@pytest.mark.django_db
def test_lab_result_critical_flag(unique_patient, unique_doctor, unique_org, unique_user, unique_catalog, unique_encounter):
    """Test that is_critical can be set to True."""
    order = LabOrder.objects.create(
        patient=unique_patient,
        doctor=unique_doctor,
        organization=unique_org,
        encounter=unique_encounter,
        created_by=unique_user
    )

    item = LabOrderItem.objects.create(
        lab_order=order,
        test=unique_catalog,
        quantity=1
    )

    result = LabResult.objects.create(
        order_item=item,
        value="0.5",
        unit="count",
        is_critical=True
    )

    assert result.is_critical is True
