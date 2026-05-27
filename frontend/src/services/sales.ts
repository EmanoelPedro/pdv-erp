import { apiPost } from '@/services/http'
import type { CashRegisterSession } from '@/types/cashRegister'
import type { CreateSalePayload, Sale } from '@/types/sale'

interface CreateSaleResponse {
  sale: Sale
  cash_register_session: CashRegisterSession
}

export async function createSale(payload: CreateSalePayload): Promise<CreateSaleResponse> {
  return apiPost<CreateSaleResponse, CreateSalePayload>('/api/v1/sales', payload)
}
