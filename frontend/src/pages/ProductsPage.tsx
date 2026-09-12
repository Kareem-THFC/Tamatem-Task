import { ProductCard, ProductGridSkeleton } from '@/components/products/ProductCard'
import { ProductFilterBar } from '@/components/products/ProductFilters'
import { useProductFilters } from '@/components/products/useProductFilters'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { StatePanel } from '@/components/ui/StatePanel'
import { useAuth } from '@/context/auth-context'
import { useProducts } from '@/hooks/useProducts'
import { cn } from '@/lib/cn'
import { formatLocation } from '@/lib/format'

const PAGE_SIZE = 8

/** Explain an empty result in terms of whichever filters caused it. */
function emptyDescription({
  search,
  location,
}: {
  search: string
  location: string
}): string {
  const region = formatLocation(location)

  if (search && location) {
    return `Nothing matching that search is listed in ${region}. Try another region, or a different term.`
  }

  if (search) {
    return 'Try a shorter term, or check the spelling.'
  }

  if (location) {
    return `No drops for ${region} right now. Try another region.`
  }

  return 'The catalogue is empty. Import the products CSV on the backend to fill it.'
}

export function ProductsPage() {
  const { user } = useAuth()

  const filters = useProductFilters()
  const { page, location, search, sort, searchPending } = filters

  const { products, pagination, loading, error } = useProducts({
    page,
    pageSize: PAGE_SIZE,
    location,
    search,
    sort,
  })

  function goToPage(nextPage: number) {
    filters.setPage(nextPage)
  }

  return (
    <div className="space-y-7">
      <div className="relative overflow-hidden rounded-4xl border-[3px] border-ink bg-linear-to-br from-sand to-cream px-8 py-9 shadow-hard-lg">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 overflow-hidden"
        >
          <div className="absolute -top-12 right-16 size-42 rotate-24 rounded-[56px] bg-violet/14" />
          <div className="absolute -bottom-10 right-60 size-28 rounded-full bg-sky/20" />
        </div>

        <div className="relative">
          <p className="text-[13px] font-bold tracking-[0.12em] text-violet uppercase">
            Regional drops
          </p>

          <h1 className="mt-2 font-display text-4xl leading-tight font-semibold tracking-tight text-ink sm:text-[44px]">
            {user ? `Hey ${user.username}, ready to restock?` : 'Browse the market'}
          </h1>

          <p className="mt-2.5 max-w-xl text-base text-ink-soft">
            Every item is priced in gems and locked to its store region.
            {!user && ' Sign in to spend your balance.'}
          </p>
        </div>
      </div>

      <ProductFilterBar filters={filters} busy={loading} />

      {loading && !products && (
        <div className="space-y-6">
          <ProductGridSkeleton count={PAGE_SIZE} />

          <div className="flex items-center justify-center gap-3">
            <Spinner className="size-5.5" />
            <span className="text-[13px] font-bold text-ink-muted">
              Fetching the drop table…
            </span>
          </div>
        </div>
      )}

      {!loading && error && (
        <StatePanel
          tone="error"
          title="Connection dropped"
          description={`${error.message} Your gems are safe.`}
        />
      )}

      {!error && products && pagination && (
        <>
          {products.length === 0 ? (
            <StatePanel
              title={search ? `No matches for "${search}"` : 'Nothing here yet'}
              description={emptyDescription({ search, location })}
              action={
                filters.hasFilters
                  ? { label: 'Clear filters', onClick: filters.clearAll }
                  : undefined
              }
            />
          ) : (
            <div
              aria-busy={searchPending}
              className={cn(
                'transition-opacity duration-200 ease-out',
                searchPending ? 'pointer-events-none opacity-40' : 'opacity-100',
              )}
            >
              <div className="grid animate-rise gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {products.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            </div>
          )}

          <Pagination
            pagination={{
              ...pagination,
              page: Math.min(page, Math.max(pagination.pages, 1)),
            }}
            onPageChange={goToPage}
            disabled={loading}
            busy={searchPending}
            noun={search ? 'matches' : 'items in stock'}
          />
        </>
      )}
    </div>
  )
}
