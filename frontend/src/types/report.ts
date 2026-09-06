import type { CashRegisterSession } from '@/types/cashRegister'
import type { ExpenseCategory } from '@/types/expense'
import type { PaymentMethod } from '@/types/sale'

export interface ReportFilters {
  start_date?: string
  end_date?: string
  category_id?: string
  payment_method?: PaymentMethod
  user_id?: string
  cash_register_session_id?: string
}

export interface SalesSummaryRow {
  report_date: string
  sales_count: number
  gross_sales: string
  discounts: string
  final_sales: string
  expenses: string
  estimated_result: string
}

export interface ProductPerformanceRow {
  product_id: string
  product_name: string
  quantity_sold: number
  revenue: string
  average_sale_participation: string
}

export interface CategoryPerformanceRow {
  category_id: string
  category_name: string
  revenue: string
  units_sold: number
  percentage_of_total: string
}

export interface PaymentMethodReportRow {
  payment_method: PaymentMethod
  transactions: number
  revenue: string
  percentage_of_total: string
}

export interface HourlySalesRow {
  hour: string
  sales_count: number
  revenue: string
}

export interface ExpenseAnalysisRow {
  category: ExpenseCategory
  amount: string
  count: number
  percentage_of_total: string
}

export type CashRegisterReportRow = CashRegisterSession
