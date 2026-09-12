import { Link, useNavigate, useSearchParams } from 'react-router-dom'

import { ProductArt } from '@/components/products/ProductArt'
import { Card } from '@/components/ui/Card'
import { RegionPin } from '@/components/ui/Chip'
import { CoinAmount } from '@/components/ui/CoinAmount'
import { Pagination } from '@/components/ui/Pagination'
import { Skeleton, SkeletonBlock } from '@/components/ui/Skeleton'
import { StatePanel } from '@/components/ui/StatePanel'
import { useOrders } from '@/hooks/useOrders'
import { formatDateTime, formatLocation } from '@/lib/format'

const PAGE_SIZE = 10

/**
 * The signed-in user's purchase history. The endpoint scopes results to the
 * token's own user, so no user id is sent.
 */
export function OrdersPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()

  const page = Math.max(Number(searchParams.get('page')) || 1, 1)

  const { orders, pagination, loading, error } = useOrders({
    page,
    pageSize: PAGE_SIZE,
  })

  return (
    <div className="space-y-7">
      <div className="space-y-1.5">
        <h1 className="font-display text-4xl font-semibold tracking-tight text-ink">
          My orders
        </h1>
        <p className="text-base text-ink-soft">Every purchase, newest first.</p>
      </div>

      {loading && !orders && <OrdersSkeleton />}

      {!loading && error && (
        <StatePanel
          tone="error"
          title="Could not load your orders"
          description={error.message}
        />
      )}

      {!loading && !error && orders && pagination && (
        <>
          {orders.length === 0 ? (
            <StatePanel
              title="No purchases yet"
              description="Once you buy something it will appear here with its receipt."
              action={{ label: 'Browse the store', onClick: () => navigate('/products') }}
            />
          ) : (
            <ul className="space-y-4">
              {orders.map((order) => (
                <li key={order.id}>
                  <Card interactive>
                    <Link
                      to={`/orders/${order.id}`}
                      className="flex flex-wrap items-center gap-4 p-5"
                    >
                      <ProductArt
                        productId={order.product.id}
                        shapeSize={24}
                        className="size-14 shrink-0 rounded-[18px] border-[3px] border-ink"
                      />

                      <div className="min-w-0 flex-1">
                        <p className="font-display text-lg font-semibold text-ink">
                          {order.product.title}
                        </p>

                        <p className="mt-0.5 flex flex-wrap items-center gap-1.5 text-[13px] font-bold text-ink-muted">
                          <RegionPin className="size-2.5" />
                          {formatLocation(order.product.location)} · order #{order.id} ·{' '}
                          {formatDateTime(order.created_at)}
                        </p>
                      </div>

                      <div className="text-right">
                        <CoinAmount amount={order.total_price} />
                        <p className="text-xs font-bold text-ink-muted">
                          View receipt &rarr;
                        </p>
                      </div>
                    </Link>
                  </Card>
                </li>
              ))}
            </ul>
          )}

          <Pagination
            pagination={pagination}
            disabled={loading}
            onPageChange={(nextPage) => {
              setSearchParams({ page: String(nextPage) })
            }}
            busy={loading}
            noun="orders"
          />
        </>
      )}
    </div>
  )
}

function OrdersSkeleton() {
  return (
    <div role="status" aria-label="Loading orders" className="space-y-4">
      {Array.from({ length: 4 }, (_, index) => (
        <div
          key={index}
          className="flex items-center gap-4 rounded-[26px] border-[3px] border-ink/30 bg-surface p-5"
        >
          <Skeleton className="size-14 shrink-0 rounded-[18px]" />

          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-52" />
            <SkeletonBlock className="h-3 w-36" />
          </div>

          <SkeletonBlock className="h-5 w-20" />
        </div>
      ))}
    </div>
  )
}
