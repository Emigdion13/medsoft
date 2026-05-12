"""Tests for Lab API views."""
import pytest
from django.urls import reverse

from apps.lab.models import (
    LabTestCatalog,
    LabOrder,
    LabOrderItem,
    LabResult,
)
from apps.core_organizations.tests.factories import OrganizationFactory
from apps.encounters.tests.factories import EncounterFactory
from apps.patients.tests.factories import PatientFactory
from apps.doctors.tests.factories import DoctorFactory
from apps.core_users.tests.factories import UserFactory


@pytest.mark.django_db
class TestLabTestCatalogViewSet:
    """Tests for LabTestCatalog API views."""

    def test_list_lab_test_catalog(self, api_client):
        """Test listing lab test catalogs."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        LabTestCatalog.objects.create(
            code='CBC',
            name='Complete Blood Count',
            sample_type='Blood',
        )
        LabTestCatalog.objects.create(
            code='CMP',
            name='Comprehensive Metabolic Panel',
            sample_type='Blood',
        )

        url = reverse('api:labtestcatalog-list')
        response = api_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_create_lab_test_catalog(self, api_client):
        """Test creating a lab test catalog."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        url = reverse('api:labtestcatalog-list')
        data = {
            'code': 'GLUC',
            'name': 'Glucose Test',
            'sample_type': 'Blood',
            'reference_min': 70.0,
            'reference_max': 100.0,
        }

        response = api_client.post(url, data)

        assert response.status_code == 201
        assert LabTestCatalog.objects.filter(code='GLUC').exists()

    def test_retrieve_lab_test_catalog(self, api_client):
        """Test retrieving a specific lab test catalog."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        catalog = LabTestCatalog.objects.create(
            code='MRI',
            name='Magnetic Resonance Imaging',
            sample_type='Body',
        )

        url = reverse('api:labtestcatalog-detail', kwargs={'pk': catalog.pk})
        response = api_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 'MRI'

    def test_update_lab_test_catalog(self, api_client):
        """Test updating a lab test catalog."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        catalog = LabTestCatalog.objects.create(
            code='TEST',
            name='Original Name',
            sample_type='Blood',
        )

        url = reverse('api:labtestcatalog-detail', kwargs={'pk': catalog.pk})
        data = {
            'code': 'TEST',
            'name': 'Updated Name',
            'sample_type': 'Urine',
        }

        response = api_client.put(url, data)

        assert response.status_code == 200
        catalog.refresh_from_db()
        assert catalog.name == 'Updated Name'


@pytest.mark.django_db
class TestLabOrderViewSet:
    """Tests for LabOrder API views."""

    def test_list_lab_orders(self, api_client):
        """Test listing lab orders."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()

        LabOrder.objects.create(
            organization=organization,
            encounter=encounter,
            patient=patient,
            doctor=doctor,
            order_number='ORD-001',
        )

        url = reverse('api:laborder-list')
        response = api_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert 'count' in data
        assert data['count'] >= 1

    def test_create_lab_order(self, api_client):
        """Test creating a lab order."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()

        url = reverse('api:laborder-list')
        data = {
            'organization_id': str(organization.id),
            'encounter_id': str(encounter.id),
            'patient_id': str(patient.id),
            'doctor_id': str(doctor.id),
            'order_number': 'NEW-001',
            'priority': 'NORMAL',
        }

        response = api_client.post(url, data)

        assert response.status_code == 201
        assert LabOrder.objects.filter(order_number='NEW-001').exists()

    def test_retrieve_lab_order(self, api_client):
        """Test retrieving a specific lab order."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()

        order = LabOrder.objects.create(
            organization=organization,
            encounter=encounter,
            patient=patient,
            doctor=doctor,
            order_number='RET-001',
        )

        url = reverse('api:laborder-detail', kwargs={'pk': order.pk})
        response = api_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['order_number'] == 'RET-001'

    def test_update_lab_order_status(self, api_client):
        """Test updating lab order status."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()

        order = LabOrder.objects.create(
            organization=organization,
            encounter=encounter,
            patient=patient,
            doctor=doctor,
            order_number='UPD-001',
            status='PENDIENTE',
        )

        url = reverse('api:laborder-detail', kwargs={'pk': order.pk})
        data = {
            'status': 'EN_PROCESO',
        }

        response = api_client.patch(url, data, format='json')

        assert response.status_code == 200
        order.refresh_from_db()
        assert order.status == 'EN_PROCESO'


@pytest.mark.django_db
class TestLabOrderItemViewSet:
    """Tests for LabOrderItem API views."""

    def test_list_lab_order_items(self, api_client):
        """Test listing lab order items."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()

        order = LabOrder.objects.create(
            organization=organization,
            encounter=encounter,
            patient=patient,
            doctor=doctor,
            order_number='ITEM-001',
        )
        catalog = LabTestCatalog.objects.create(
            code='CBC',
            name='Complete Blood Count',
            sample_type='Blood',
        )

        LabOrderItem.objects.create(
            lab_order=order,
            lab_test=catalog,
        )

        url = reverse('api:laborderitem-list')
        response = api_client.get(url)

        assert response.status_code == 200

    def test_create_lab_order_item(self, api_client):
        """Test creating a lab order item."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()

        order = LabOrder.objects.create(
            organization=organization,
            encounter=encounter,
            patient=patient,
            doctor=doctor,
            order_number='ITEM-002',
        )
        catalog = LabTestCatalog.objects.create(
            code='CMP',
            name='Comprehensive Metabolic Panel',
            sample_type='Blood',
        )

        url = reverse('api:laborderitem-list')
        data = {
            'lab_order_id': str(order.id),
            'lab_test_id': str(catalog.id),
        }

        response = api_client.post(url, data)

        assert response.status_code == 201
        assert LabOrderItem.objects.filter(
            lab_order=order,
            lab_test=catalog,
        ).exists()


@pytest.mark.django_db
class TestLabResultViewSet:
    """Tests for LabResult API views."""

    def test_list_lab_results(self, api_client):
        """Test listing lab results."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()

        order = LabOrder.objects.create(
            organization=organization,
            encounter=encounter,
            patient=patient,
            doctor=doctor,
            order_number='RES-001',
        )
        catalog = LabTestCatalog.objects.create(
            code='GLUC',
            name='Glucose',
            sample_type='Blood',
        )
        item = LabOrderItem.objects.create(
            lab_order=order,
            lab_test=catalog,
        )

        processed_by = UserFactory.create()

        LabResult.objects.create(
            lab_order_item=item,
            result_numeric=95.5,
            unit='mg/dL',
            result_flag='NORMAL',
            processed_by=processed_by,
        )

        url = reverse('api:labresult-list')
        response = api_client.get(url)

        assert response.status_code == 200

    def test_create_lab_result(self, api_client):
        """Test creating a lab result."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()

        order = LabOrder.objects.create(
            organization=organization,
            encounter=encounter,
            patient=patient,
            doctor=doctor,
            order_number='RES-002',
        )
        catalog = LabTestCatalog.objects.create(
            code='CBC',
            name='Complete Blood Count',
            sample_type='Blood',
        )
        item = LabOrderItem.objects.create(
            lab_order=order,
            lab_test=catalog,
        )
        processed_by = UserFactory.create()

        url = reverse('api:labresult-list')
        data = {
            'lab_order_item_id': str(item.id),
            'result_numeric': 120.5,
            'unit': 'mg/dL',
            'result_flag': 'ANORMAL',
            'processed_by_id': str(processed_by.id),
        }

        response = api_client.post(url, data)

        assert response.status_code == 201
        assert LabResult.objects.filter(result_numeric=120.5).exists()

    def test_update_lab_result_review(self, api_client):
        """Test updating lab result with review."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()

        order = LabOrder.objects.create(
            organization=organization,
            encounter=encounter,
            patient=patient,
            doctor=doctor,
            order_number='REV-001',
        )
        catalog = LabTestCatalog.objects.create(
            code='TEST',
            name='Test',
            sample_type='Blood',
        )
        item = LabOrderItem.objects.create(
            lab_order=order,
            lab_test=catalog,
        )
        processed_by = UserFactory.create()
        reviewed_by = UserFactory.create()

        result = LabResult.objects.create(
            lab_order_item=item,
            result_numeric=100.0,
            unit='mg/dL',
            result_flag='ANORMAL',
            processed_by=processed_by,
        )

        url = reverse('api:labresult-detail', kwargs={'pk': result.pk})
        data = {
            'reviewed_by_id': str(reviewed_by.id),
            'status': 'FIRMADA',
        }

        response = api_client.patch(url, data, format='json')

        assert response.status_code == 200
        result.refresh_from_db()
        assert result.reviewed_by == reviewed_by
