import { useId } from 'react'

import type { ProductSort } from '@/api/products'
import { REGIONS, SORT_OPTIONS } from '@/components/products/filter-options'
import type { ProductFilters } from '@/components/products/useProductFilters'
import { FilterChip, RegionPin } from '@/components/ui/Chip'
import { cn } from '@/lib/cn'

export function SearchField({
  value,
  onChange,
  busy = false,
}: {
  value: string
  onChange: (value: string) => void
  busy?: boolean
}) {
  const id = useId()

  return (
    <div className="relative w-full min-w-0 sm:w-64">
      <label htmlFor={id} className="sr-only">
        Search products
      </label>

      <span
        aria-hidden="true"
        className="pointer-events-none absolute top-1/2 left-4 -translate-y-1/2"
      >
        <span className="block size-3.5 rounded-full border-[2.5px] border-ink-muted" />
        <span className="absolute -right-1 -bottom-1 block h-[2.5px] w-2 rotate-45 rounded-full bg-ink-muted" />
      </span>

      <input
        id={id}
        type="search"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Search items…"
        className={cn(
          'w-full rounded-2xl border-[2.5px] border-ink bg-surface py-2.5 pr-10 pl-11',
          'text-sm font-semibold text-ink shadow-hard-xs',
          'placeholder:font-semibold placeholder:text-muted',
          // `type="search"` makes WebKit draw its own clear button once the
          // field has a value, which would sit next to the styled one below.
          '[&::-webkit-search-cancel-button]:appearance-none',
          'focus:border-violet focus:shadow-[0_0_0_4px_rgba(123,92,255,0.22),0_4px_0_rgba(42,26,20,0.12)]',
          'focus:outline-none',
        )}
      />

      {value && (
        <button
          type="button"
          onClick={() => onChange('')}
          aria-label="Clear search"
          className="absolute top-1/2 right-3 grid size-6 -translate-y-1/2 cursor-pointer place-items-center rounded-full bg-ink/10 text-ink-muted hover:bg-ink/20 hover:text-ink"
        >
          <span aria-hidden="true" className="text-sm leading-none font-extrabold">
            ×
          </span>
        </button>
      )}

      {busy && (
        <span className="sr-only" role="status">
          Searching
        </span>
      )}
    </div>
  )
}

export function SortSelect({
  value,
  onChange,
}: {
  value: ProductSort
  onChange: (value: ProductSort) => void
}) {
  const id = useId()

  return (
    <div className="flex w-full items-center gap-2 sm:w-auto">
      <label
        htmlFor={id}
        className="text-[13px] font-extrabold whitespace-nowrap text-ink-muted"
      >
        Sort
      </label>

      <select
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value as ProductSort)}
        className={cn(
          'min-w-0 flex-1 sm:flex-none',
          'cursor-pointer rounded-2xl border-[2.5px] border-ink bg-surface px-3 py-2.5',
          'text-[13px] font-extrabold text-ink shadow-hard-xs',
          'focus:border-violet focus:outline-none',
        )}
      >
        {SORT_OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  )
}

export function RegionFilter({
  value,
  onChange,
}: {
  value: string
  onChange: (value: string) => void
}) {
  return (
  
    <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:items-center">
      <span className="flex items-center gap-2 text-[13px] font-extrabold text-ink-muted sm:mr-1">
        <RegionPin />
        Region
      </span>

      <div className="grid grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:items-center">
        {REGIONS.map((region) => (
          <FilterChip
            key={region.value || 'all'}
            active={value === region.value}
            onClick={() => onChange(region.value)}
            className={cn('justify-center', region.value === '' && 'col-span-2')}
          >
            {region.label}
          </FilterChip>
        ))}
      </div>
    </div>
  )
}

/** The filter row above the grid: region chips, search, sort. */
export function ProductFilterBar({
  filters,
  busy = false,
}: {
  filters: ProductFilters
  busy?: boolean
}) {
  return (
    <div
      className={cn(
        'flex flex-col gap-4',
        'sm:flex-row sm:flex-wrap sm:items-center sm:justify-between sm:gap-3',
      )}
    >
      <RegionFilter value={filters.location} onChange={filters.setLocation} />

      <div className="flex w-full flex-col gap-3 sm:w-auto sm:flex-row sm:flex-wrap sm:items-center">
        <SearchField
          value={filters.searchInput}
          onChange={filters.setSearchInput}
          busy={filters.searchPending || busy}
        />

        <SortSelect value={filters.sort} onChange={filters.setSort} />
      </div>
    </div>
  )
}
