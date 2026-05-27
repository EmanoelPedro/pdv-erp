export type PaymentMethod = 'CASH' | 'PIX' | 'DEBIT_CARD' | 'CREDIT_CARD' | 'MIXED'

export interface SaleItemPayload {
  product_id: string
  quantity: number
}

export interface CreateSalePayload {
  items: SaleItemPayload[]
  payment_method: PaymentMethod
  cash_amount?: string
  pix_amount?: string
  debit_card_amount?: string
  credit_card_amount?: string
}

export interface SaleItem {
  id: string
  product_id: string
  product_name: string
  unit_price: string
  quantity: number
  total_price: string
  created_at: string
}

export interface Sale {
  id: string
  cash_register_session_id: string
  seller_user_id: string
  payment_method: PaymentMethod
  subtotal_amount: string
  total_amount: string
  cash_amount: string
  pix_amount: string
  debit_card_amount: string
  credit_card_amount: string
  created_at: string
  updated_at: string
  items: SaleItem[]
}
