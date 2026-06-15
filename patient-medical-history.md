# Patient Medical History (Historial Médico del Paciente)

Per-patient clinical history view with documentation. Lets authorized roles open a patient's
complete clinical timeline and document care — encounters, vital signs, clinical notes,
diagnoses, and prescriptions (including note signing).

Branch: `bvw/patient-medical-history`.

---

## Why this was built

The data model and DRF viewsets for clinical history already existed
(`Encounter`, `VitalSign`, `ClinicalNote`, `Diagnosis`, `Prescription`, plus `Patient`'s
`blood_type` / `allergies` / `chronic_conditions`), but the feature was **not usable end-to-end**:

- `apps.clinical.urls` (notes/diagnoses/prescriptions) was never included in the project URLConf —
  those endpoints were unreachable.
- There was no way to fetch one patient's history (encounters could only be searched by name).
- `EncounterViewSet.perform_create` never set `organization` (a non-null PROTECT FK), so encounter
  creation failed.
- `ClinicalNoteSerializer` marked `signed_by`/`signed_at` read-only yet required `signed_by` when
  `status='FIRMADA'` — signing a note was impossible through the normal endpoint.
- The frontend `MedicalRecords.tsx` was a flat read-only list of all encounters with no
  per-patient drill-down and no documentation.

**Scope (confirmed with the user):** full history **+ documentation**, reachable from **both** the
Patients list and the Historial Médico page.

---

## Architecture notes (important context)

The backend has a slightly unusual dual layout:

- `accounts/` is a monolithic API layer that imports models from `apps.*` and exposes the
  primary CRUD viewsets at `/api/...` (`/api/patients/`, `/api/doctors/`, `/api/appointments/`,
  `/api/specialties/`, `/api/users/`). The frontend talks to these.
- `apps/encounters`, `apps/clinical`, `apps/patients` each have their **own** serializers/views/urls.
  Of these, only `apps.encounters.urls` was wired up (at `/api/encounters/`). This feature wires up
  `apps.clinical.urls` as well (at `/api/clinical/`).

So clinical history endpoints live under `/api/encounters/...` and `/api/clinical/...`, while the
patient master record is served by the `accounts` layer at `/api/patients/...`.

---

## Backend changes (`backend/`)

| File | Change |
|------|--------|
| `config/urls.py` | Added `path('api/clinical/', include('apps.clinical.urls'))`. |
| `apps/encounters/views.py` | `EncounterViewSet.get_queryset` now supports a `patient_id` query param. `perform_create` now sets `organization=self.request.user.organization`. |
| `apps/clinical/views.py` | Added a `sign` action to `ClinicalNoteViewSet`. |
| `apps/encounters/tests/test_history_api.py` | New — patient filter, org auto-assignment, org scoping. |
| `apps/clinical/tests/__init__.py`, `apps/clinical/tests/test_clinical_api.py` | New — clinical routing, note signing, double-sign guard. |

### Note signing (`POST /api/clinical/clinical-notes/<id>/sign/`)
Sets `status='FIRMADA'`, `signed_by=request.user`, `signed_at=now()`, and
`content_hash = sha256(content)`, satisfying the model's `note_signed_check` constraint. Returns
400 if the note is already `FIRMADA` or is `ANULADA`. This sidesteps the read-only/validate
contradiction in `ClinicalNoteSerializer` (signing is an explicit action, not a normal update).

### API surface used by the feature
```
GET    /api/patients/<id>/                              # patient master record (accounts layer)
GET    /api/encounters/encounters/?patient_id=<uuid>    # encounter timeline for a patient
POST   /api/encounters/encounters/                      # create encounter (org auto-set)
GET    /api/encounters/vitalsigns/?encounter_id=<uuid>
POST   /api/encounters/vitalsigns/
GET    /api/clinical/clinical-notes/?encounter_id=<uuid>
POST   /api/clinical/clinical-notes/
POST   /api/clinical/clinical-notes/<id>/sign/
GET    /api/clinical/diagnoses/?encounter_id=<uuid>
POST   /api/clinical/diagnoses/
GET    /api/clinical/prescriptions/?encounter_id=<uuid>
POST   /api/clinical/prescriptions/
```
All list endpoints are organization-scoped server-side (via the encounter's / patient's org).

> **No schema or migration changes** — all tables already existed.

---

## Frontend changes (`frontend/`)

| File | Change |
|------|--------|
| `src/types/index.ts` | Added `Encounter`, `CreateEncounterPayload`, `VitalSign`, `ClinicalNote`, `Diagnosis`, `Prescription`, and the related choice unions. |
| `src/services/clinicalServices.ts` | New — `encountersService`, `vitalSignsService`, `clinicalNotesService` (incl. `sign`), `diagnosesService`, `prescriptionsService`. |
| `src/services/resourceServices.ts` | Added `patientsService.get(id)`. |
| `src/pages/PatientHistory.tsx` | New page — the medical history view. |
| `src/App.tsx` | Added route `/pacientes/:patientId/historial`. |
| `src/pages/Patients.tsx` | "Ver Historial" button per row → patient history. |
| `src/pages/MedicalRecords.tsx` | Rows are clickable → owning patient's history. |
| `src/components/layout/Sidebar.tsx` | Typed `NavItem.module` as `ModuleKey` (build fix, see Decisions). |
| `src/lib/rbac/can.ts` | Relaxed the `view` ownership gate (see Decisions). |

### `PatientHistory.tsx` layout
- **Header card**: demographics + a highlighted band for **blood type / allergies / chronic
  conditions** (allergies/chronic conditions emphasized in red/amber when present).
- **Encounter timeline**: encounters newest-first. Each is an expandable card; expanding lazily
  loads its vitals, notes, diagnoses, and prescriptions in parallel.
- **Documentation**, gated by the existing `<CanAccess>` guard:
  - "Nueva consulta" → create an `Encounter` (`action="create"`).
  - Per encounter: add Diagnosis, Prescription, Clinical Note, Vital Signs (`action="create"`),
    and "Firmar" a draft note (`action="sign"`).

Styling follows the existing inline-style convention from `MedicalRecords.tsx` / `Patients.tsx`
(`es-DO` date formatting, badge/table patterns, `PageContainer`).

---

## Decisions made

1. **Reused the existing `apps.encounters` / `apps.clinical` viewsets** rather than adding clinical
   CRUD to the `accounts` monolith. They were already written, tested-adjacent, and
   organization-scoped — they just needed wiring and small fixes. This keeps clinical concerns in
   their own apps.

2. **Signing is a dedicated action, not a PATCH.** The serializer keeps signature fields read-only
   (immutability/audit intent); signing goes through `POST .../sign/` which stamps signer, time,
   and content hash atomically. Re-signing or signing an annulled note is rejected.

3. **Encounter `organization` is derived from the request user**, mirroring the established pattern
   in `accounts/views.py` (`perform_create` → `serializer.save(organization=...)`). Clients never
   send it.

4. **Doctor selection via dropdown** in the "Nueva consulta" form and reuse of the encounter's
   doctor for its clinical notes — consistent with how `Appointments.tsx` picks a doctor. There is
   no implicit user→doctor mapping in the data model, so the doctor is chosen explicitly.

5. **RBAC: relaxed the route-level `view` gate** in `src/lib/rbac/can.ts`. Previously, for
   `appointments` / `patients` / `medical_records`, a `view` (or `edit`) check without
   ownership/assignment context returned `false` for everyone except SECRETARY/RECEPTIONIST — which
   blocked **doctors and nurses from the route entirely** (route guards pass no per-record context).
   This also affected the pre-existing `/historial-medico` page. The fix: **viewing is allowed for
   any role that holds the `view` permission** (already checked one line above); **ownership/
   assignment is now only enforced for `edit`**. Verified no existing code passed `context` to a
   `view`/`edit` check for these modules, so nothing relied on the stricter `view` behavior.

6. **Typed `NavItem.module` as `ModuleKey`** in `Sidebar.tsx`. This was a pre-existing type error
   (`string` not assignable to `ModuleKey`) that broke `npm run build` (`tsc && vite build`); it was
   unrelated to the feature but blocked the production build, so it was corrected as a one-line fix.

### Non-goals / limitations
- ICD-10 codes are free-text (no code-lookup service) — matches the current model.
- Lab and Imaging apps exist but are out of scope here.
- No edit/delete UI for already-recorded notes/diagnoses/prescriptions beyond what the API offers;
  the page focuses on viewing history and adding records (and signing notes).

---

## RBAC summary

`medical_records` permissions per role (`src/lib/rbac/permissions.ts`):

| Role | view | create | edit | sign | delete |
|------|:---:|:---:|:---:|:---:|:---:|
| ADMINISTRATOR | ✓ | ✓ | ✓ | ✓ | ✓ |
| DOCTOR | ✓ | ✓ | ✓ | ✓ | — |
| NURSE | ✓ | ✓ | ✓ | — | — |
| SECRETARY / RECEPTIONIST | ✓ | — | — | — | — |
| LAB_TECHNICIAN | — | — | — | — | — |

After the `can.ts` change, anyone with `view` can open the page; documentation buttons appear only
for roles holding `create` / `sign`. Secretaries/receptionists get a read-only history.

---

## Verification

### Backend
```bash
cd backend
source venv/bin/activate
python manage.py check
python -m pytest apps/encounters/tests/test_history_api.py apps/clinical/tests/test_clinical_api.py
```
Current status: `check` clean; **6 tests pass** (patient filter, org auto-assignment, org scoping,
clinical routing, note signing, double-sign guard). Routes (incl. the `sign` action) resolve.

### Frontend
```bash
cd frontend
npm install        # if node_modules is absent
npm run build      # tsc -b && vite build — passes
```

### Manual smoke
Log in as a DOCTOR (or ADMINISTRATOR) → **Pacientes → "Ver Historial"** → header shows
allergies/chronic conditions → **"Nueva consulta"** → expand the encounter → add a diagnosis,
prescription, and clinical note → **"Firmar"** the note → reload and confirm it persists as FIRMADA.
From **Historial Médico**, click an encounter row and confirm it lands on the same patient history.
As a SECRETARY/RECEPTIONIST, confirm the history is read-only (documentation buttons hidden).
