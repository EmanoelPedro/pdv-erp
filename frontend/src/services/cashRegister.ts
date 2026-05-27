import { apiGet, apiPost } from '@/services/http'
import type {
  CashRegisterSession,
  CashRegisterHistoryFilters,
  CloseCashRegisterPayload,
  OpenCashRegisterPayload
} from '@/types/cashRegister'

const LAST_CLOSED_SESSION_KEY = 'cash-register:last-closed'

export async function getCurrentCashRegister(): Promise<CashRegisterSession> {
  return apiGet<CashRegisterSession>('/api/v1/cash-register/current')
}

export async function openCashRegister(
  payload: OpenCashRegisterPayload
): Promise<CashRegisterSession> {
  return apiPost<CashRegisterSession, OpenCashRegisterPayload>(
    '/api/v1/cash-register/open',
    payload
  )
}

export async function closeCashRegister(
  sessionId: string,
  payload: CloseCashRegisterPayload
): Promise<CashRegisterSession> {
  return apiPost<CashRegisterSession, CloseCashRegisterPayload>(
    `/api/v1/cash-register/${sessionId}/close`,
    payload
  )
}

function buildHistoryQuery(filters?: CashRegisterHistoryFilters): string {
  const params = new URLSearchParams()

  if (filters?.start_date) {
    params.set('start_date', filters.start_date)
  }
  if (filters?.end_date) {
    params.set('end_date', filters.end_date)
  }

  const query = params.toString()
  return query ? `?${query}` : ''
}

export async function listCashRegisterHistory(
  filters?: CashRegisterHistoryFilters
): Promise<CashRegisterSession[]> {
  return apiGet<CashRegisterSession[]>(`/api/v1/cash-register/history${buildHistoryQuery(filters)}`)
}

export async function getCashRegisterSession(sessionId: string): Promise<CashRegisterSession> {
  return apiGet<CashRegisterSession>(`/api/v1/cash-register/${sessionId}`)
}

export function saveLastClosedSession(session: CashRegisterSession): void {
  window.sessionStorage.setItem(LAST_CLOSED_SESSION_KEY, JSON.stringify(session))
}

export function getLastClosedSession(): CashRegisterSession | null {
  const value = window.sessionStorage.getItem(LAST_CLOSED_SESSION_KEY)

  if (!value) {
    return null
  }

  try {
    return JSON.parse(value) as CashRegisterSession
  } catch {
    window.sessionStorage.removeItem(LAST_CLOSED_SESSION_KEY)
    return null
  }
}

export function clearLastClosedSession(): void {
  window.sessionStorage.removeItem(LAST_CLOSED_SESSION_KEY)
}
