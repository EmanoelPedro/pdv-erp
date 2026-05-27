import { apiGet, apiPost, apiPostWithoutBody } from '@/services/http'
import type {
  AuthUser,
  LoginPayload,
  LoginResponse,
  RegisterUserPayload,
  SetupStateResponse
} from '@/types/auth'

export async function getSetupState(): Promise<SetupStateResponse> {
  return apiGet<SetupStateResponse>('/api/v1/auth/setup-state')
}

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  return apiPost<LoginResponse, LoginPayload>('/api/v1/auth/login', payload)
}

export async function registerUser(payload: RegisterUserPayload): Promise<AuthUser> {
  return apiPost<AuthUser, RegisterUserPayload>('/api/v1/auth/register', payload)
}

export async function getCurrentUser(): Promise<AuthUser> {
  return apiGet<AuthUser>('/api/v1/auth/me')
}

export async function listUsers(): Promise<AuthUser[]> {
  return apiGet<AuthUser[]>('/api/v1/auth/users')
}

export async function logout(): Promise<void> {
  await apiPostWithoutBody<void>('/api/v1/auth/logout')
}
