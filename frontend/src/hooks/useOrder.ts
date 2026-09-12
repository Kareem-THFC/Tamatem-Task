import { useEffect, useState } from 'react'

import { ApiError } from '@/api/client'
import { getOrder } from '@/api/orders'
import type { Order } from '@/types/api'

/** A single order by id, for the receipt page. */
export function useOrder(id: number) {
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    setOrder(null)
    setError(null)
    setLoading(true)

    getOrder(id, controller.signal)
      .then((result) => {
        setOrder(result)
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
  }, [id])

  return { order, loading, error }
}
