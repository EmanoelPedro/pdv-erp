export type CashRegisterStatus = 'OPEN' | 'CLOSED'

export interface CashRegisterTotals {
  sales_amount: string
  sales_count: number
  average_ticket_amount: string
  total_received_amount: string
  expenses_amount: string
  cash_expenses_amount: string
  expected_amount: string
  cash_sales_amount: string
  pix_sales_amount: string
  debit_card_sales_amount: string
  credit_card_sales_amount: string
  mixed_sales_amount: string
  cash_received_amount: string
  pix_received_amount: string
  debit_card_received_amount: string
  credit_card_received_amount: string
  last_sale_at: string | null
}

export interface CashRegisterSession {
  id: string
  status: CashRegisterStatus
  opening_amount: string
  expected_amount: string
  closing_amount: string | null
  difference_amount: string | null
  opened_at: string
  closed_at: string | null
  created_at: string
  updated_at: string
  totals: CashRegisterTotals
}

export interface OpenCashRegisterPayload {
  opening_amount: string
}

export interface CloseCashRegisterPayload {
  closing_amount: string
  owner_pin: string
}

export interface CashRegisterHistoryFilters {
  start_date?: string
  end_date?: string
}
