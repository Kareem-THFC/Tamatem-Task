import { useEffect, useState } from 'react'

import { ApiError } from '@/api/client'
import { getProduct } from '@/api/products'
import type { Product } from '@/types/api'

/**
 * A single product by id.
 *
 * `setProduct` is returned so a caller that already learned something about
 * the item — a purchase reporting it as owned — can correct the copy on
 * screen without a second round trip.
 */
export function useProduct(id: number) {
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    setProduct(null)
    setError(null)
    setLoading(true)

    getProduct(id, controller.signal)
      .then((result) => {
        setProduct(result)
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

  return { product, setProduct, loading, error }
}
