export type UserRole = 'OWNER' | 'EMPLOYEE'

export interface AuthUser {
  id: string
  full_name: string
  username: string
  role: UserRole
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginPayload {
  username: string
  pin: string
}

export interface RegisterUserPayload {
  full_name: string
  username: string
  pin: string
  role?: UserRole
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: AuthUser
}

export interface SetupStateResponse {
  has_users: boolean
}
