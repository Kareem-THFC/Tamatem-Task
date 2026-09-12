import { useEffect, useState } from 'react'

import { ApiError } from '@/api/client'
import { listOrders } from '@/api/orders'
import type { Order, Pagination } from '@/types/api'

interface UseOrdersParams {
  page: number
  pageSize: number
}

/**
 * One page of the signed-in user's purchase history.
 *
 * No user id is passed: the endpoint scopes results to the token's own user.
 */
export function useOrders({ page, pageSize }: UseOrdersParams) {
  const [orders, setOrders] = useState<Order[] | null>(null)
  const [pagination, setPagination] = useState<Pagination | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    setError(null)
    setLoading(true)

    listOrders({ page, page_size: pageSize, signal: controller.signal })
      .then((result) => {
        setOrders(result.data)
        setPagination(result.pagination)
        setLoading(false)
      })
      .catch((caught: unknown) => {
        if (controller.signal.aborted) {
          return
        }

        setError(
          caught instanceof ApiError
            ? caught
            : new ApiError('UNEXPECTED_ERROR', 'Something went wrong.', 0),
        )
        setLoading(false)
      })

    return () => controller.abort()
  }, [page, pageSize])

  return { orders, pagination, loading, error }
}
