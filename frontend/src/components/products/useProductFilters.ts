import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import type { ProductSort } from '@/api/products'
import { SORT_OPTIONS } from '@/components/products/filter-options'
import { useDebouncedValue } from '@/hooks/useDebouncedValue'

const SEARCH_DEBOUNCE_MS = 300

export type ProductFilters = {
  /** Committed URL state — the list request is built from these four. */
  page: number
  location: string
  search: string
  sort: ProductSort
  /** The raw field value, which runs ahead of the committed `search`. */
  searchInput: string
  setSearchInput: (value: string) => void
  /** True while the field and the committed search disagree. */
  searchPending: boolean
  hasFilters: boolean
  setLocation: (location: string) => void
  setSort: (sort: ProductSort) => void
  setPage: (page: number) => void
  clearAll: () => void
}

/** Anything can be typed in the URL, so an unrecognised sort falls back. */
function readSort(value: string | null): ProductSort {
  return SORT_OPTIONS.some((option) => option.value === value)
    ? (value as ProductSort)
    : 'default'
}

function nextParams(
  current: URLSearchParams,
  changes: Record<string, string>,
): URLSearchParams {
  const params = new URLSearchParams(current)

  for (const [key, value] of Object.entries(changes)) {
    if (value) {
      params.set(key, value)
    } else {
      params.delete(key)
    }
  }

  if (!('page' in changes)) {
    params.delete('page')
  }

  return params
}


export function useProductFilters(): ProductFilters {
  const [searchParams, setSearchParams] = useSearchParams()

  const page = Math.max(Number(searchParams.get('page')) || 1, 1)
  const location = searchParams.get('location') ?? ''
  const search = searchParams.get('search') ?? ''
  const sort = readSort(searchParams.get('sort'))

  const [searchInput, setSearchInput] = useState(search)
  const debouncedSearch = useDebouncedValue(searchInput, SEARCH_DEBOUNCE_MS)

  useEffect(() => {
    if (debouncedSearch !== searchInput || debouncedSearch === search) {
      return
    }

    setSearchParams(
      (current) => nextParams(current, { search: debouncedSearch }),
      { replace: true },
    )
  }, [debouncedSearch, searchInput, search, setSearchParams])

  const [trackedSearch, setTrackedSearch] = useState(search)

  if (trackedSearch !== search) {
    setTrackedSearch(search)
    setSearchInput(search)
  }

  function applyFilter(changes: Record<string, string>) {
    setSearchParams((current) => nextParams(current, changes))
  }

  return {
    page,
    location,
    search,
    sort,
    searchInput,
    setSearchInput,
    searchPending: searchInput !== search,
    hasFilters: Boolean(location || search),
    setLocation: (nextLocation) => applyFilter({ location: nextLocation }),
    setSort: (nextSort) =>
      applyFilter({ sort: nextSort === 'default' ? '' : nextSort }),
    setPage: (nextPage) => applyFilter({ page: String(nextPage) }),
    clearAll: () => {
      setSearchInput('')
      setSearchParams({})
    },
  }
}
