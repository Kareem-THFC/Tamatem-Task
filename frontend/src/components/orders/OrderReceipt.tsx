import { type ReactNode } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { ProductArt } from '@/components/products/ProductArt'
import { Button } from '@/components/ui/Button'
import { RegionPin } from '@/components/ui/Chip'
import { CoinAmount } from '@/components/ui/CoinAmount'
import { formatDateTime, formatGems, formatLocation } from '@/lib/format'
import type { Order } from '@/types/api'

/** The receipt card itself, shown both on its own and inside a celebration. */
export function OrderReceipt({ order }: { order: Order }) {
  const navigate = useNavigate()

  return (
    <div className="rounded-[28px] border-[3px] border-ink bg-surface p-7 shadow-[0_10px_0_rgba(42,26,20,0.3)] sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b-[2.5px] border-dashed border-ink/18 pb-4">
        <p className="font-display text-[22px] font-semibold text-ink">Receipt</p>
        <p className="text-[13px] font-bold text-ink-muted">
          #{order.id} · {formatDateTime(order.created_at)}
        </p>
      </div>

      <PurchasedItem order={order} />

      <dl className="space-y-2.5 border-b-[2.5px] border-dashed border-ink/18 py-5 text-sm">
        <Row label="Unit price">{formatGems(order.product.price)} gems</Row>
        <Row label="Quantity">1</Row>
        <Row label="Balance before">{formatGems(order.gem_balance_before)} gems</Row>
        <Row label="Balance after" tone="leaf">
          {formatGems(order.gem_balance_after)} gems
        </Row>
      </dl>

      <div className="flex items-center justify-between gap-4 pt-5">
        <p className="text-[13px] font-extrabold tracking-[0.12em] text-ink-muted uppercase">
          Total paid
        </p>

        <CoinAmount amount={order.total_price} size="xl" className="text-tomato" />
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <Button className="flex-1" onClick={() => navigate('/products')}>
          Back to store
        </Button>

        <Button variant="secondary" onClick={() => navigate('/orders')}>
          My orders
        </Button>
      </div>
    </div>
  )
}

function PurchasedItem({ order }: { order: Order }) {
  return (
    <div className="flex items-center gap-4 border-b-[2.5px] border-dashed border-ink/18 py-5">
      <ProductArt
        productId={order.product.id}
        shapeSize={26}
        className="size-16 shrink-0 rounded-[20px] border-[3px] border-ink"
      />

      <div className="min-w-0 flex-1">
        <Link
          to={`/products/${order.product.id}`}
          className="block font-display text-xl font-semibold text-ink hover:text-tomato"
        >
          {order.product.title}
        </Link>

        <p className="mt-0.5 flex items-center gap-1.5 text-[13px] font-bold text-ink-muted">
          <RegionPin className="size-2.5" />
          {formatLocation(order.product.location)} · qty 1
        </p>
      </div>

      <CoinAmount amount={order.product.price} size="lg" className="shrink-0" />
    </div>
  )
}

function Row({
  label,
  tone,
  children,
}: {
  label: string
  tone?: 'leaf'
  children: ReactNode
}) {
  return (
    <div className="flex items-center justify-between gap-4">
      <dt className="font-semibold text-ink-soft">{label}</dt>
      <dd
        className={`font-bold tabular-nums ${tone === 'leaf' ? 'text-leaf-dark' : 'text-ink'}`}
      >
        {children}
      </dd>
    </div>
  )
}
