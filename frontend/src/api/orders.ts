import { buildQuery, request } from '@/api/client'
import type { ApiResponse, Order, PaginatedResponse } from '@/types/api'

export async function createOrder(productId: number): Promise<Order> {
  const response = await request<ApiResponse<Order>>('/api/orders', {
    method: 'POST',
    body: { product_id: productId },
    auth: true,
  })

  return response.data
}

export async function getOrder(id: number, signal?: AbortSignal): Promise<Order> {
  const response = await request<ApiResponse<Order>>(`/api/orders/${id}`, {
    auth: true,
    signal,
  })

  return response.data
}

export interface ListOrdersParams {
  page?: number
  page_size?: number
  signal?: AbortSignal
}

export function listOrders({
  signal,
  ...params
}: ListOrdersParams = {}): Promise<PaginatedResponse<Order>> {
  return request<PaginatedResponse<Order>>(`/api/orders${buildQuery(params)}`, {
    auth: true,
    signal,
  })
}
