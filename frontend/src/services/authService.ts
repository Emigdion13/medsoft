import type {
  AuthResponse,
  LoginPayload,
  RegisterPayload,
  User,
  UserListItem,
  PaginatedResponse,
} from '../types'
import { api } from '../utils/api'

export const authService = {
  login(payload: LoginPayload) {
    return api.post<AuthResponse>('/auth/login/', payload)
  },

  register(payload: RegisterPayload) {
    return api.post<AuthResponse>('/auth/register/', payload)
  },

  refresh(refresh: string) {
    return api.post<{ access: string }>('/auth/refresh/', { refresh })
  },

  me() {
    return api.get<User>('/auth/me/')
  },
}

export const usersService = {
  list(params?: { search?: string; page?: number }) {
    return api.get<PaginatedResponse<UserListItem>>('/users/', { params })
  },

  create(payload: Partial<UserListItem> & { password?: string }) {
    return api.post<UserListItem>('/users/', payload)
  },

  update(id: string, payload: Partial<UserListItem>) {
    return api.patch<UserListItem>(`/users/${id}/`, payload)
  },
}

export interface SecretaryDoctorAssignment {
  id: string
  secretary_id?: string
  doctor_id?: string
  doctor_name: string
  is_active: boolean
  created_at: string
}

export const secretaryDoctorService = {
  list(secretaryId: string) {
    console.log('[secretaryDoctorService] list called with:', secretaryId)
    return api.get<PaginatedResponse<SecretaryDoctorAssignment>>('/secretary-doctors/', {
      params: { secretary_id: secretaryId },
    }).then(r => { console.log('[secretaryDoctorService] result:', r); return r })
  },

  create(secretaryId: string, doctorId: string) {
    return api.post<SecretaryDoctorAssignment>('/secretary-doctors/', {
      secretary_id: secretaryId,
      doctor_id: doctorId,
    })
  },

  delete(id: string) {
    return api.delete(`/secretary-doctors/${id}/`)
  },
}
