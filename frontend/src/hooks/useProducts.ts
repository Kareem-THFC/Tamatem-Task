import { useEffect, useState } from 'react'

import { ApiError } from '@/api/client'
import { listProducts, type ProductSort } from '@/api/products'
import type { Pagination, Product } from '@/types/api'

interface UseProductsParams {
  page: number
  pageSize: number
  location: string
  search: string
  sort: ProductSort
}


export function useProducts({
  page,
  pageSize,
  location,
  search,
  sort,
}: UseProductsParams) {
  const [products, setProducts] = useState<Product[] | null>(null)
  const [pagination, setPagination] = useState<Pagination | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    setError(null)
    setLoading(true)

    listProducts({
      page,
      page_size: pageSize,
      location,
      search,
      sort,
      signal: controller.signal,
    })
      .then((result) => {
        setProducts(result.data)
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
  }, [page, pageSize, location, search, sort])

  return { products, pagination, loading, error }
}
