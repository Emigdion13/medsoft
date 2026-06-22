"""Tests for patient medical history API behaviors on encounters."""
import pytest

from apps.core.organizations.tests.factories import OrganizationFactory
from apps.core.users.tests.factories import UserFactory
from apps.doctors.tests.factories import DoctorFactory
from apps.patients.tests.factories import PatientFactory
from apps.encounters.tests.factories import EncounterFactory


@pytest.mark.django_db
class TestEncounterHistoryApi:
    def test_filter_by_patient_id(self, api_client):
        """GET ?patient_id=<uuid> returns only that patient's encounters."""
        org = OrganizationFactory.create()
        user = UserFactory.create(organization=org)
        api_client.force_authenticate(user=user)

        patient_a = PatientFactory.create(organization=org)
        patient_b = PatientFactory.create(organization=org)
        EncounterFactory.create(organization=org, patient=patient_a)
        EncounterFactory.create(organization=org, patient=patient_a)
        EncounterFactory.create(organization=org, patient=patient_b)

        resp = api_client.get(
            '/api/encounters/encounters/', {'patient_id': str(patient_a.id)}
        )

        assert resp.status_code == 200
        results = resp.json()['results']
        assert len(results) == 2
        assert {r['patient']['id'] for r in results} == {str(patient_a.id)}

    def test_create_sets_organization_from_user(self, api_client):
        """POST encounter auto-assigns the requesting user's organization."""
        org = OrganizationFactory.create()
        user = UserFactory.create(organization=org)
        api_client.force_authenticate(user=user)

        patient = PatientFactory.create(organization=org)
        doctor = DoctorFactory.create(organization=org)

        resp = api_client.post('/api/encounters/encounters/', {
            'patient_id': str(patient.id),
            'doctor_id': str(doctor.id),
            'encounter_type': 'AMBULATORIO',
            'start_at': '2026-06-15T10:00:00Z',
        }, format='json')

        assert resp.status_code == 201, resp.content
        from apps.encounters.models import Encounter
        enc = Encounter.objects.get(id=resp.json()['id'])
        assert enc.organization_id == org.id
        assert enc.created_by_id == user.id

    def test_org_scoping_excludes_other_orgs(self, api_client):
        """A user only sees encounters from their own organization."""
        org = OrganizationFactory.create()
        other_org = OrganizationFactory.create()
        user = UserFactory.create(organization=org)
        api_client.force_authenticate(user=user)

        EncounterFactory.create(organization=other_org)

        resp = api_client.get('/api/encounters/encounters/')
        assert resp.status_code == 200
        assert resp.json()['count'] == 0
