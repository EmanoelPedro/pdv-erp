import { apiDelete, apiGet, apiPost, apiPut } from '@/services/http'
import type { Expense, ExpenseFilters, ExpensePayload } from '@/types/expense'

function buildExpenseQuery(filters?: ExpenseFilters): string {
  const params = new URLSearchParams()

  if (filters?.start_date) {
    params.set('start_date', filters.start_date)
  }
  if (filters?.end_date) {
    params.set('end_date', filters.end_date)
  }
  if (filters?.category) {
    params.set('category', filters.category)
  }
  if (filters?.cash_register_session_id) {
    params.set('cash_register_session_id', filters.cash_register_session_id)
  }

  const query = params.toString()
  return query ? `?${query}` : ''
}

export async function listExpenses(
  filters?: ExpenseFilters
): Promise<Expense[]> {
  return apiGet<Expense[]>(`/api/v1/expenses${buildExpenseQuery(filters)}`)
}

export async function getExpense(expenseId: string): Promise<Expense> {
  return apiGet<Expense>(`/api/v1/expenses/${expenseId}`)
}

export async function createExpense(payload: ExpensePayload): Promise<Expense> {
  return apiPost<Expense, ExpensePayload>('/api/v1/expenses', payload)
}

export async function updateExpense(
  expenseId: string,
  payload: ExpensePayload
): Promise<Expense> {
  return apiPut<Expense, ExpensePayload>(
    `/api/v1/expenses/${expenseId}`,
    payload
  )
}

export async function deleteExpense(expenseId: string): Promise<void> {
  return apiDelete<void>(`/api/v1/expenses/${expenseId}`)
}
