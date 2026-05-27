export interface DashboardProductHighlight {
  product_id: string
  product_name: string
  quantity_sold: number
  revenue: string
}

export interface DashboardCategoryHighlight {
  category_id: string
  category_name: string
  revenue: string
  units_sold: number
}

export interface DashboardHourlyPoint {
  hour: string
  sales_count: number
  revenue: string
}

export interface DashboardDailyRevenuePoint {
  report_date: string
  revenue: string
}

export interface DashboardSummary {
  report_date: string
  revenue_today: string
  expenses_today: string
  profit_estimate_today: string
  average_ticket_today: string
  sales_count_today: number
  latest_cash_difference: string | null
  latest_cash_difference_at: string | null
  best_selling_product_today: DashboardProductHighlight | null
  best_category_today: DashboardCategoryHighlight | null
  sales_by_hour_today: DashboardHourlyPoint[]
  revenue_last_7_days: DashboardDailyRevenuePoint[]
}