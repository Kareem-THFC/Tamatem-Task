import { buildQuery, request } from '@/api/client'
import type { ApiResponse, PaginatedResponse, Product } from '@/types/api'

export type ProductSort = 'default' | 'price_asc' | 'price_desc'

export interface ListProductsParams {
  page?: number
  page_size?: number
  location?: string
  search?: string
  sort?: ProductSort
  signal?: AbortSignal
}

export function listProducts({
  signal,
  ...params
}: ListProductsParams = {}): Promise<PaginatedResponse<Product>> {
  return request<PaginatedResponse<Product>>(`/api/products${buildQuery(params)}`, {
    auth: true,
    signal,
  })
}

export async function getProduct(
  id: number,
  signal?: AbortSignal,
): Promise<Product> {
  const response = await request<ApiResponse<Product>>(`/api/products/${id}`, {
    auth: true,
    signal,
  })

  return response.data
}
