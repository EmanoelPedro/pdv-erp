import { apiGet, apiPost, apiPostFormData, apiPut } from '@/services/http'
import type {
  Category,
  CreateCategoryPayload,
  CreateProductPayload,
  UpdateProductPayload,
  Product
} from '@/types/catalog'

export async function listCategories(): Promise<Category[]> {
  return apiGet<Category[]>('/api/v1/catalog/categories')
}

export async function createCategory(payload: CreateCategoryPayload): Promise<Category> {
  return apiPost<Category, CreateCategoryPayload>('/api/v1/catalog/categories', payload)
}

export async function listProducts(search?: string, includeInactive = false): Promise<Product[]> {
  const query = new URLSearchParams()
  if (search) {
    query.set('search', search)
  }
  if (includeInactive) {
    query.set('include_inactive', 'true')
  }
  const suffix = query.size > 0 ? `?${query.toString()}` : ''
  return apiGet<Product[]>(`/api/v1/catalog/products${suffix}`)
}

export async function createProduct(payload: CreateProductPayload): Promise<Product> {
  return apiPost<Product, CreateProductPayload>('/api/v1/catalog/products', payload)
}

export async function uploadProductImage(productId: string, file: File): Promise<Product> {
  const payload = new FormData()
  payload.set('image', file)
  return apiPostFormData<Product>(`/api/v1/catalog/products/${productId}/image`, payload)
}

export async function updateProduct(productId: string, payload: UpdateProductPayload): Promise<Product> {
  return apiPut<Product, UpdateProductPayload>(`/api/v1/catalog/products/${productId}`, payload)
}

export async function deactivateProduct(productId: string): Promise<Product> {
  return apiPost<Product, Record<string, never>>(`/api/v1/catalog/products/${productId}/deactivate`, {})
}

export async function restoreProduct(productId: string): Promise<Product> {
  return apiPost<Product, Record<string, never>>(`/api/v1/catalog/products/${productId}/restore`, {})
}
