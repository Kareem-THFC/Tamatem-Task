import { Link } from 'react-router-dom'

import { ProductArt } from '@/components/products/ProductArt'
import { Card } from '@/components/ui/Card'
import { RegionPin } from '@/components/ui/Chip'
import { Skeleton, SkeletonBlock } from '@/components/ui/Skeleton'
import { cn } from '@/lib/cn'
import { formatGems, formatLocation } from '@/lib/format'

/** One product in the store grid, linking to its details page. */
export function ProductCard({
  product,
}: {
  product: {
    id: number
    title: string
    price: string
    location: string
    owned: boolean
  }
}) {
  return (
    <Card interactive className="overflow-hidden">
      <Link to={`/products/${product.id}`} className="block">
        <div className="relative">
          <ProductArt
            productId={product.id}
            className="h-40 border-b-[3px] border-ink"
          />

          {product.owned && (
            <span className="absolute top-3 left-3 inline-flex items-center gap-1.5 rounded-full border-[2.5px] border-ink bg-leaf px-3 py-1 text-[11px] font-extrabold tracking-widest text-white uppercase shadow-[0_3px_0_rgba(42,26,20,0.3)]">
              <span
                aria-hidden="true"
                className="block h-1.5 w-2.5 -translate-y-px -rotate-45 border-b-2 border-l-2 border-white"
              />
              Owned
            </span>
          )}

          <div className="absolute -bottom-4 right-3.5 flex items-center gap-1.5 rounded-[14px] border-[3px] border-ink bg-coin px-3 py-1 shadow-[0_4px_0_rgba(42,26,20,0.3)]">
            <span className="font-display text-lg font-semibold tabular-nums text-ink">
              {formatGems(product.price)}
            </span>
          </div>
        </div>

        <div className="p-5 pt-6">
          <h2 className="line-clamp-2 min-h-[2.3em] font-display text-xl leading-tight font-semibold text-ink">
            {product.title}
          </h2>

          <div className="mt-2 flex items-center gap-2">
            <RegionPin />
            <span className="text-[13px] font-bold text-ink-muted">
              {formatLocation(product.location)}
            </span>
          </div>

          <span
            className={cn(
              'mt-4 block rounded-[14px] border-[2.5px] py-2.5 text-center font-display text-base font-semibold',
              product.owned
                ? 'border-muted bg-canvas text-muted-ink'
                : 'border-ink bg-tomato text-white shadow-[0_5px_0_#9E1C15]',
            )}
          >
            {product.owned ? 'In your inventory' : 'View item'}
          </span>
        </div>
      </Link>
    </Card>
  )
}

/** Placeholder cards shown while a page of products loads. */
export function ProductGridSkeleton({ count = 8 }: { count?: number }) {
  return (
    <div
      role="status"
      aria-label="Loading products"
      className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
    >
      {Array.from({ length: count }, (_, index) => (
        <div
          key={index}
          className="overflow-hidden rounded-[26px] border-[3px] border-ink/30 bg-surface"
        >
          <Skeleton className="h-40 rounded-none" />

          <div className="space-y-2.5 p-5">
            <Skeleton className="h-3.5 w-4/5" />
            <SkeletonBlock className="h-3 w-1/2" />
            <SkeletonBlock className="mt-3 h-9 rounded-xl" />
          </div>
        </div>
      ))}
    </div>
  )
}
