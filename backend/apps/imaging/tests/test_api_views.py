"""Tests for Imaging API views."""
import pytest
from django.urls import reverse

from apps.imaging.models import (
    ImagingTypeCatalog,
    ImagingOrder,
    ImagingReport,
    ImagingFile,
)
from apps.core_organizations.tests.factories import OrganizationFactory
from apps.encounters.tests.factories import EncounterFactory
from apps.patients.tests.factories import PatientFactory
from apps.doctors.tests.factories import DoctorFactory
from apps.core_users.tests.factories import UserFactory


@pytest.mark.django_db
class TestImagingTypeCatalogViewSet:
    """Tests for ImagingTypeCatalog API views."""

    def test_list_imaging_type_catalog(self, api_client):
        """Test listing imaging type catalogs."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        ImagingTypeCatalog.objects.create(
            code='RX',
            name='Radiography',
            modality='X-ray',
        )
        ImagingTypeCatalog.objects.create(
            code='CT',
            name='Computed Tomography',
            modality='CT',
        )

        url = reverse('api:imagingtypecatalog-list')
        response = api_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_create_imaging_type_catalog(self, api_client):
        """Test creating an imaging type catalog."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        url = reverse('api:imagingtypecatalog-list')
        data = {
            'code': 'MRI',
            'name': 'Magnetic Resonance Imaging',
            'modality': 'MRI',
        }

        response = api_client.post(url, data)

        assert response.status_code == 201
        assert ImagingTypeCatalog.objects.filter(code='MRI').exists()

    def test_retrieve_imaging_type_catalog(self, api_client):
        """Test retrieving a specific imaging type catalog."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        catalog = ImagingTypeCatalog.objects.create(
            code='US',
            name='Ultrasound',
            modality='US',
        )

        url = reverse('api:imagingtypecatalog-detail', kwargs={'pk': catalog.pk})
        response = api_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 'US'

    def test_update_imaging_type_catalog(self, api_client):
        """Test updating an imaging type catalog."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        catalog = ImagingTypeCatalog.objects.create(
            code='TEST',
            name='Original Name',
            modality='US',
        )

        url = reverse('api:imagingtypecatalog-detail', kwargs={'pk': catalog.pk})
        data = {
            'code': 'TEST',
            'name': 'Updated Name',
            'modality': 'CT',
        }

        response = api_client.put(url, data)

        assert response.status_code == 200
        catalog.refresh_from_db()
        assert catalog.name == 'Updated Name'


@pytest.mark.django_db
class TestImagingOrderViewSet:
    """Tests for ImagingOrder API views."""

    def test_list_imaging_orders(self, api_client):
        """Test listing imaging orders."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()
        imaging_type = ImagingTypeCatalog.objects.create(
            code='CT',
            name='CT Scan',
            modality='CT',
        )

        ImagingOrder.objects.create(
            organization=organization,
            encounter=encounter,
            patient=patient,
            doctor=doctor,
            imaging_type=imaging_type,
            order_number='IMG-001',
            clinical_indication='Test indication',
        )

        url = reverse('api:imagingorder-list')
        response = api_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert 'count' in data
        assert data['count'] >= 1

    def test_create_imaging_order(self, api_client):
        """Test creating an imaging order."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()
        imaging_type = ImagingTypeCatalog.objects.create(
            code='MRI',
            name='MRI',
            modality='MRI',
        )

        url = reverse('api:imagingorder-list')
        data = {
            'organization_id': str(organization.id),
            'encounter_id': str(encounter.id),
            'patient_id': str(patient.id),
            'doctor_id': str(doctor.id),
            'imaging_type_catalog_id': str(imaging_type.id),
            'order_number': 'NEW-IMG-001',
            'priority': 'NORMAL',
            'clinical_indication': 'Routine checkup',
        }

        response = api_client.post(url, data)

        assert response.status_code == 201
        assert ImagingOrder.objects.filter(order_number='NEW-IMG-001').exists()

    def test_retrieve_imaging_order(self, api_client):
        """Test retrieving a specific imaging order."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()
        imaging_type = ImagingTypeCatalog.objects.create(
            code='RX',
            name='Radiography',
            modality='X-ray',
        )

        order = ImagingOrder.objects.create(
            organization=organization,
            encounter=encounter,
            patient=patient,
            doctor=doctor,
            imaging_type=imaging_type,
            order_number='RET-IMG-001',
            clinical_indication='Test indication',
        )

        url = reverse('api:imagingorder-detail', kwargs={'pk': order.pk})
        response = api_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['order_number'] == 'RET-IMG-001'

    def test_update_imaging_order_status(self, api_client):
        """Test updating imaging order status."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()
        imaging_type = ImagingTypeCatalog.objects.create(
            code='US',
            name='Ultrasound',
            modality='US',
        )

        order = ImagingOrder.objects.create(
            organization=organization,
            encounter=encounter,
            patient=patient,
            doctor=doctor,
            imaging_type=imaging_type,
            order_number='UPD-IMG-001',
            status='PENDIENTE',
            clinical_indication='Test indication',
        )

        url = reverse('api:imagingorder-detail', kwargs={'pk': order.pk})
        data = {
            'status': 'REALIZADA',
        }

        response = api_client.patch(url, data, format='json')

        assert response.status_code == 200
        order.refresh_from_db()
        assert order.status == 'REALIZADA'


@pytest.mark.django_db
class TestImagingReportViewSet:
    """Tests for ImagingReport API views."""

    def test_list_imaging_reports(self, api_client):
        """Test listing imaging reports."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()
        imaging_type = ImagingTypeCatalog.objects.create(
            code='CT',
            name='CT Scan',
            modality='CT',
        )

        order = ImagingOrder.objects.create(
            organization=organization,
            encounter=encounter,
            patient=patient,
            doctor=doctor,
            imaging_type=imaging_type,
            order_number='REP-001',
            clinical_indication='Test indication',
        )
        technician = UserFactory.create()

        ImagingReport.objects.create(
            imaging_order=order,
            technician_user=technician,
            findings='No acute findings.',
            impression='Normal CT scan.',
            status='BORRADOR',
        )

        url = reverse('api:imagingreport-list')
        response = api_client.get(url)

        assert response.status_code == 200

    def test_create_imaging_report(self, api_client):
        """Test creating an imaging report."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()
        imaging_type = ImagingTypeCatalog.objects.create(
            code='MRI',
            name='MRI',
            modality='MRI',
        )

        order = ImagingOrder.objects.create(
            organization=organization,
            encounter=encounter,
            patient=patient,
            doctor=doctor,
            imaging_type=imaging_type,
            order_number='REP-002',
            clinical_indication='Test indication',
        )
        technician = UserFactory.create()

        url = reverse('api:imagingreport-list')
        data = {
            'imaging_order_id': str(order.id),
            'technician_user_id': str(technician.id),
            'findings': 'Abnormal tissue detected.',
            'impression': 'Suspicious mass in left breast.',
            'recommendations': 'Biopsy recommended.',
            'status': 'BORRADOR',
        }

        response = api_client.post(url, data)

        assert response.status_code == 201
        assert ImagingReport.objects.filter(
            findings='Abnormal tissue detected.'
        ).exists()

    def test_update_imaging_report_status(self, api_client):
        """Test updating imaging report status."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()
        imaging_type = ImagingTypeCatalog.objects.create(
            code='US',
            name='Ultrasound',
            modality='US',
        )

        order = ImagingOrder.objects.create(
            organization=organization,
            encounter=encounter,
            patient=patient,
            doctor=doctor,
            imaging_type=imaging_type,
            order_number='UPD-REP-001',
            clinical_indication='Test indication',
        )
        technician = UserFactory.create()

        report = ImagingReport.objects.create(
            imaging_order=order,
            technician_user=technician,
            findings='Initial findings.',
            impression='Initial impression.',
            status='BORRADOR',
        )

        url = reverse('api:imagingreport-detail', kwargs={'pk': report.pk})
        data = {
            'status': 'FIRMADA',
            'findings': 'Updated findings.',
        }

        response = api_client.patch(url, data, format='json')

        assert response.status_code == 200
        report.refresh_from_db()
        assert report.status == 'FIRMADA'
        assert report.findings == 'Updated findings.'


@pytest.mark.django_db
class TestImagingFileViewSet:
    """Tests for ImagingFile API views."""

    def test_list_imaging_files(self, api_client):
        """Test listing imaging files."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()
        imaging_type = ImagingTypeCatalog.objects.create(
            code='CT',
            name='CT Scan',
            modality='CT',
        )

        order = ImagingOrder.objects.create(
            organization=organization,
            encounter=encounter,
            patient=patient,
            doctor=doctor,
            imaging_type=imaging_type,
            order_number='FILE-001',
            clinical_indication='Test indication',
        )
        uploaded_by = UserFactory.create()

        ImagingFile.objects.create(
            imaging_order=order,
            file_name='scan_001.dcm',
            file_type='DICOM',
            storage_uri='/storage/patients/123/scans/scan_001.dcm',
            size_bytes=15728640,
            sha256='a1b2c3d4e5f6' * 10,
            uploaded_by=uploaded_by,
        )

        url = reverse('api:imagingfile-list')
        response = api_client.get(url)

        assert response.status_code == 200

    def test_create_imaging_file(self, api_client):
        """Test creating an imaging file."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()
        imaging_type = ImagingTypeCatalog.objects.create(
            code='RX',
            name='Radiography',
            modality='X-ray',
        )

        order = ImagingOrder.objects.create(
            organization=organization,
            encounter=encounter,
            patient=patient,
            doctor=doctor,
            imaging_type=imaging_type,
            order_number='FILE-002',
            clinical_indication='Test indication',
        )
        uploaded_by = UserFactory.create()

        url = reverse('api:imagingfile-list')
        data = {
            'imaging_order_id': str(order.id),
            'file_name': 'new_scan.dcm',
            'file_type': 'DICOM',
            'storage_uri': '/storage/patients/456/scans/new_scan.dcm',
            'size_bytes': 20971520,
            'sha256': 'f6e5d4c3b2a1' * 10,
            'uploaded_by_id': str(uploaded_by.id),
        }

        response = api_client.post(url, data)

        assert response.status_code == 201
        assert ImagingFile.objects.filter(file_name='new_scan.dcm').exists()

    def test_retrieve_imaging_file(self, api_client):
        """Test retrieving a specific imaging file."""
        user = UserFactory.create(is_staff=True, is_superuser=True)
        api_client.force_authenticate(user=user)

        organization = OrganizationFactory.create()
        encounter = EncounterFactory.create()
        patient = PatientFactory.create()
        doctor = DoctorFactory.create()
        imaging_type = ImagingTypeCatalog.objects.create(
            code='MRI',
            name='MRI',
            modality='MRI',
        )

        order = ImagingOrder.objects.create(
            organization=organization,
            encounter=encounter,
            patient=patient,
            doctor=doctor,
            imaging_type=imaging_type,
            order_number='RET-FILE-001',
            clinical_indication='Test indication',
        )
        uploaded_by = UserFactory.create()

        img_file = ImagingFile.objects.create(
            imaging_order=order,
            file_name='ret_scan.dcm',
            file_type='DICOM',
            storage_uri='/storage/ret_scan.dcm',
            size_bytes=10485760,
            sha256='abcdef' * 20,
            uploaded_by=uploaded_by,
        )

        url = reverse('api:imagingfile-detail', kwargs={'pk': img_file.pk})
        response = api_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['file_name'] == 'ret_scan.dcm'
