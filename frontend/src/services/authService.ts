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
