"""Tests for clinical documentation API (routing + note signing)."""
import pytest

from apps.core.organizations.tests.factories import OrganizationFactory
from apps.core.users.tests.factories import UserFactory
from apps.doctors.tests.factories import DoctorFactory
from apps.encounters.tests.factories import EncounterFactory
from apps.clinical.models import ClinicalNote, Diagnosis


@pytest.mark.django_db
class TestClinicalApi:
    def _auth(self, api_client):
        org = OrganizationFactory.create()
        user = UserFactory.create(organization=org)
        api_client.force_authenticate(user=user)
        return org, user

    def test_diagnosis_endpoint_is_routed(self, api_client):
        """Proves apps.clinical.urls is wired into the project URLConf."""
        org, user = self._auth(api_client)
        encounter = EncounterFactory.create(organization=org)

        resp = api_client.post('/api/clinical/diagnoses/', {
            'encounter': str(encounter.id),
            'icd10_code': 'J00',
            'description': 'Resfriado común',
            'diagnosis_type': 'PRINCIPAL',
            'is_primary': True,
        }, format='json')

        assert resp.status_code == 201, resp.content
        assert Diagnosis.objects.filter(encounter=encounter, icd10_code='J00').exists()

    def test_sign_clinical_note(self, api_client):
        """POST .../sign/ marks the note FIRMADA with signer, timestamp and hash."""
        org, user = self._auth(api_client)
        encounter = EncounterFactory.create(organization=org)
        doctor = DoctorFactory.create(organization=org)

        note = ClinicalNote.objects.create(
            encounter=encounter,
            doctor=doctor,
            note_type='EVOLUCION',
            content='Paciente estable.',
            status='BORRADOR',
            created_by=user,
        )

        resp = api_client.post(f'/api/clinical/clinical-notes/{note.id}/sign/')

        assert resp.status_code == 200, resp.content
        note.refresh_from_db()
        assert note.status == 'FIRMADA'
        assert note.signed_by_id == user.id
        assert note.signed_at is not None
        assert note.content_hash

    def test_cannot_sign_twice(self, api_client):
        org, user = self._auth(api_client)
        encounter = EncounterFactory.create(organization=org)
        doctor = DoctorFactory.create(organization=org)
        note = ClinicalNote.objects.create(
            encounter=encounter, doctor=doctor, note_type='EVOLUCION',
            content='x', status='BORRADOR', created_by=user,
        )
        api_client.post(f'/api/clinical/clinical-notes/{note.id}/sign/')
        resp = api_client.post(f'/api/clinical/clinical-notes/{note.id}/sign/')
        assert resp.status_code == 400
