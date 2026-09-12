/** TypeScript mirrors of the JSON the Flask API returns. */

export interface Product {
  id: number
  title: string
  description: string
  
  price: string
  location: string
  created_at: string | null
  owned: boolean
}

export interface User {
  id: number
  username: string
  email: string
  gem_balance: string
}

export interface Order {
  id: number
  user_id: number
  total_price: string
  gem_balance_before: string
  gem_balance_after: string
  created_at: string | null
  product: Product
}

export interface AuthPayload {
  access_token: string
  user: User
}

export interface Pagination {
  page: number
  page_size: number
  total: number
  pages: number
}

export interface ApiResponse<T> {
  data: T
}

export interface PaginatedResponse<T> {
  data: T[]
  pagination: Pagination
}

export interface ApiErrorDetail {
  field: string
  message: string
}

export interface ApiErrorBody {
  error: {
    code: string
    message: string
    details?: ApiErrorDetail[]
  }
}
