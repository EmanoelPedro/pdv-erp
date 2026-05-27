import { defineStore } from 'pinia'

import { getCurrentUser, getSetupState, login, logout, registerUser } from '@/services/auth'
import { clearStoredAuthToken, getStoredAuthToken, setStoredAuthToken } from '@/services/authSession'
import { ApiError } from '@/services/http'
import type { AuthUser, LoginPayload, RegisterUserPayload } from '@/types/auth'

type AuthStatus = 'idle' | 'loading' | 'ready'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: getStoredAuthToken() as string | null,
    user: null as AuthUser | null,
    hasUsers: false,
    initializationError: null as string | null,
    status: 'idle' as AuthStatus
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token && state.user),
    isOwner: (state) => state.user?.role === 'OWNER'
  },
  actions: {
    async initialize() {
      if (this.status === 'loading' || this.status === 'ready') {
        return
      }

      this.status = 'loading'
      this.initializationError = null

      try {
        const setupState = await getSetupState()
        this.hasUsers = setupState.has_users

        if (this.token) {
          try {
            this.user = await getCurrentUser()
          } catch {
            this.clearSession()
          }
        }
      } catch (error) {
        this.clearSession()
        this.hasUsers = false
        this.initializationError =
          error instanceof Error
            ? error.message
            : 'Nao foi possivel conectar com a API local.'
      } finally {
        this.status = 'ready'
      }
    },
    async login(payload: LoginPayload) {
      const response = await login(payload)
      this.token = response.access_token
      this.user = response.user
      this.hasUsers = true
      this.initializationError = null
      setStoredAuthToken(response.access_token)
    },
    async bootstrapOwner(payload: RegisterUserPayload) {
      await registerUser(payload)
      await this.login({ username: payload.username, pin: payload.pin })
    },
    async createUser(payload: RegisterUserPayload) {
      const createdUser = await registerUser(payload)
      this.hasUsers = true
      return createdUser
    },
    async refreshCurrentUser() {
      if (!this.token) {
        return
      }
      this.user = await getCurrentUser()
    },
    async logout() {
      if (this.token) {
        try {
          await logout()
        } catch (error) {
          if (error instanceof ApiError && error.status < 500) {
            // Ignore stale or already invalidated sessions and continue local logout.
          }
        }
      }

      this.initializationError = null
      this.clearSession()
    },
    clearSession() {
      this.token = null
      this.user = null
      clearStoredAuthToken()
    }
  }
})
