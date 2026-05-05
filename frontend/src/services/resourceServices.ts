import type {
  PaginatedResponse,
  Specialty,
  Doctor,
  Patient,
  Appointment,
  CreateAppointmentPayload,
} from '../types'
import { api } from '../utils/api'

// ── Specialty ─────────────────────────────────────────────────────────

export const specialtiesService = {
  list(params?: { search?: string; page?: number }) {
    return api.get<PaginatedResponse<Specialty>>('/specialties/', { params })
  },
}

// ── Doctor ────────────────────────────────────────────────────────────

export const doctorsService = {
  list(params?: { search?: string; page?: number }) {
    return api.get<PaginatedResponse<Doctor>>('/doctors/', { params })
  },

  create(payload: Partial<Doctor>) {
    return api.post<Doctor>('/doctors/', payload)
  },

  update(id: string, payload: Partial<Doctor>) {
    return api.patch<Doctor>(`/doctors/${id}/`, payload)
  },
}

// ── Patient ───────────────────────────────────────────────────────────

export const patientsService = {
  list(params?: { search?: string; page?: number }) {
    return api.get<PaginatedResponse<Patient>>('/patients/', { params })
  },

  create(payload: Partial<Patient>) {
    return api.post<Patient>('/patients/', payload)
  },

  update(id: string, payload: Partial<Patient>) {
    return api.patch<Patient>(`/patients/${id}/`, payload)
  },
}

// ── Appointment ───────────────────────────────────────────────────────

export const appointmentsService = {
  list(params?: {
    search?: string
    page?: number
    date?: string
    status?: string
  }) {
    return api.get<PaginatedResponse<Appointment>>('/appointments/', { params })
  },

  get(id: string) {
    return api.get<Appointment>(`/appointments/${id}/`)
  },

  create(payload: CreateAppointmentPayload) {
    return api.post<Appointment>('/appointments/', payload)
  },

  update(id: string, payload: Partial<Appointment>) {
    return api.patch<Appointment>(`/appointments/${id}/`, payload)
  },

  cancel(id: string) {
    return api.patch<Appointment>(`/appointments/${id}/`, {
      status: 'CANCELADA',
    })
  },

  delete(id: string) {
    return api.delete<Appointment>(`/appointments/${id}/`)
  },
}
