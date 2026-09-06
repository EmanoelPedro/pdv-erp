import { apiGet } from '@/services/http'
import type { DashboardSummary } from '@/types/dashboard'
import type {
  CashRegisterReportRow,
  CategoryPerformanceRow,
  ExpenseAnalysisRow,
  HourlySalesRow,
  PaymentMethodReportRow,
  ProductPerformanceRow,
  ReportFilters,
  SalesSummaryRow
} from '@/types/report'

function buildQuery(filters?: ReportFilters): string {
  if (!filters) {
    return ''
  }

  const query = new URLSearchParams()

  if (filters.start_date) {
    query.set('start_date', filters.start_date)
  }
  if (filters.end_date) {
    query.set('end_date', filters.end_date)
  }
  if (filters.category_id) {
    query.set('category_id', filters.category_id)
  }
  if (filters.payment_method) {
    query.set('payment_method', filters.payment_method)
  }
  if (filters.user_id) {
    query.set('user_id', filters.user_id)
  }
  if (filters.cash_register_session_id) {
    query.set('cash_register_session_id', filters.cash_register_session_id)
  }

  return query.size > 0 ? `?${query.toString()}` : ''
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  return apiGet<DashboardSummary>('/api/v1/dashboard/summary')
}

export async function listSalesReport(
  filters?: ReportFilters
): Promise<SalesSummaryRow[]> {
  return apiGet<SalesSummaryRow[]>(
    `/api/v1/reports/sales${buildQuery(filters)}`
  )
}

export async function listProductReport(
  filters?: ReportFilters
): Promise<ProductPerformanceRow[]> {
  return apiGet<ProductPerformanceRow[]>(
    `/api/v1/reports/products${buildQuery(filters)}`
  )
}

export async function listCategoryReport(
  filters?: ReportFilters
): Promise<CategoryPerformanceRow[]> {
  return apiGet<CategoryPerformanceRow[]>(
    `/api/v1/reports/categories${buildQuery(filters)}`
  )
}

export async function listPaymentMethodReport(
  filters?: ReportFilters
): Promise<PaymentMethodReportRow[]> {
  return apiGet<PaymentMethodReportRow[]>(
    `/api/v1/reports/payments${buildQuery(filters)}`
  )
}

export async function listHourlySalesReport(
  filters?: ReportFilters
): Promise<HourlySalesRow[]> {
  return apiGet<HourlySalesRow[]>(
    `/api/v1/reports/hourly-sales${buildQuery(filters)}`
  )
}

export async function listCashRegisterReport(
  filters?: ReportFilters
): Promise<CashRegisterReportRow[]> {
  return apiGet<CashRegisterReportRow[]>(
    `/api/v1/reports/cash-registers${buildQuery(filters)}`
  )
}

export async function listExpenseAnalysisReport(
  filters?: ReportFilters
): Promise<ExpenseAnalysisRow[]> {
  return apiGet<ExpenseAnalysisRow[]>(
    `/api/v1/reports/expenses${buildQuery(filters)}`
  )
}
