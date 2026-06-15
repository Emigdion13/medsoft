import type {
  PaginatedResponse,
  Encounter,
  CreateEncounterPayload,
  VitalSign,
  ClinicalNote,
  Diagnosis,
  Prescription,
} from '../types'
import { api } from '../utils/api'

// ── Encounter ─────────────────────────────────────────────────────────

export const encountersService = {
  list(params?: { patient_id?: string; search?: string; page?: number; page_size?: number }) {
    return api.get<PaginatedResponse<Encounter>>('/encounters/encounters/', { params })
  },

  get(id: string) {
    return api.get<Encounter>(`/encounters/encounters/${id}/`)
  },

  create(payload: CreateEncounterPayload) {
    return api.post<Encounter>('/encounters/encounters/', payload)
  },

  update(id: string, payload: Partial<CreateEncounterPayload>) {
    return api.patch<Encounter>(`/encounters/encounters/${id}/`, payload)
  },
}

// ── Vital signs ───────────────────────────────────────────────────────

export const vitalSignsService = {
  list(params?: { encounter_id?: string; page_size?: number }) {
    return api.get<PaginatedResponse<VitalSign>>('/encounters/vitalsigns/', { params })
  },

  create(payload: Partial<VitalSign> & { encounter: string }) {
    return api.post<VitalSign>('/encounters/vitalsigns/', payload)
  },
}

// ── Clinical notes ────────────────────────────────────────────────────

export const clinicalNotesService = {
  list(params?: { encounter_id?: string; page_size?: number }) {
    return api.get<PaginatedResponse<ClinicalNote>>('/clinical/clinical-notes/', { params })
  },

  create(payload: { encounter: string; doctor: string; note_type: string; content: string }) {
    return api.post<ClinicalNote>('/clinical/clinical-notes/', payload)
  },

  update(id: string, payload: Partial<Pick<ClinicalNote, 'content' | 'note_type'>>) {
    return api.patch<ClinicalNote>(`/clinical/clinical-notes/${id}/`, payload)
  },

  sign(id: string) {
    return api.post<ClinicalNote>(`/clinical/clinical-notes/${id}/sign/`)
  },
}

// ── Diagnoses ─────────────────────────────────────────────────────────

export const diagnosesService = {
  list(params?: { encounter_id?: string; page_size?: number }) {
    return api.get<PaginatedResponse<Diagnosis>>('/clinical/diagnoses/', { params })
  },

  create(payload: {
    encounter: string
    icd10_code: string
    description: string
    diagnosis_type: string
    is_primary?: boolean
  }) {
    return api.post<Diagnosis>('/clinical/diagnoses/', payload)
  },

  update(id: string, payload: Partial<Diagnosis>) {
    return api.patch<Diagnosis>(`/clinical/diagnoses/${id}/`, payload)
  },
}

// ── Prescriptions ─────────────────────────────────────────────────────

export const prescriptionsService = {
  list(params?: { encounter_id?: string; page_size?: number }) {
    return api.get<PaginatedResponse<Prescription>>('/clinical/prescriptions/', { params })
  },

  create(payload: {
    encounter: string
    medication_name: string
    dose: string
    frequency: string
    route: string
    duration_days?: number | null
    instructions?: string | null
  }) {
    return api.post<Prescription>('/clinical/prescriptions/', payload)
  },

  update(id: string, payload: Partial<Prescription>) {
    return api.patch<Prescription>(`/clinical/prescriptions/${id}/`, payload)
  },
}
