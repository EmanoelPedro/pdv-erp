import type { PaymentMethod } from '@/types/sale'

export type ExpenseCategory =
  | 'INGREDIENTS'
  | 'PACKAGING'
  | 'UTILITIES'
  | 'MAINTENANCE'
  | 'CLEANING'
  | 'WITHDRAWAL'
  | 'PERSONAL_USE'
  | 'OTHER'

export interface Expense {
  id: string
  cash_register_session_id: string | null
  description: string
  amount: string
  category: ExpenseCategory
  payment_method: PaymentMethod
  notes: string | null
  created_by_user_id: string
  expense_date: string
  created_at: string
  updated_at: string
}

export interface ExpenseFilters {
  start_date?: string
  end_date?: string
  category?: ExpenseCategory
  cash_register_session_id?: string
}

export interface ExpensePayload {
  description: string
  amount: string
  category: ExpenseCategory
  payment_method: PaymentMethod
  notes?: string | null
  cash_register_session_id?: string | null
  expense_date?: string | null
}