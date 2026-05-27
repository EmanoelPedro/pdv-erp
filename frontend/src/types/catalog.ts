export interface Category {
  id: string
  name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Product {
  id: string
  category_id: string
  name: string
  price: string
  emoji: string | null
  image_path: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface UpdateProductPayload {
  category_id: string
  name: string
  price: string
  emoji?: string | null
  remove_image: boolean
}

export interface CreateCategoryPayload {
  name: string
}

export interface CreateProductPayload {
  category_id: string
  name: string
  price: string
  emoji?: string
}
