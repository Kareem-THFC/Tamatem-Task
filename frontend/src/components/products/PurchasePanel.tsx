import { Link, useNavigate } from 'react-router-dom'

import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { CoinAmount } from '@/components/ui/CoinAmount'
import { useAuth } from '@/context/auth-context'
import { formatGems } from '@/lib/format'
import type { Product } from '@/types/api'

interface PurchasePanelProps {
  product: Product
  confirming: boolean
  purchasing: boolean
  onStartConfirm: () => void
  onCancel: () => void
  onConfirm: () => void
}

/** Price summary and whichever call to action the current state allows. */
export function PurchasePanel({
  product,
  confirming,
  purchasing,
  onStartConfirm,
  onCancel,
  onConfirm,
}: PurchasePanelProps) {
  const { isAuthenticated } = useAuth()

  return (
    <div className="mt-auto rounded-[26px] border-[3px] border-ink bg-surface p-7 shadow-hard">
      <PriceRow price={product.price} />

      <div className="pt-5">
        {!isAuthenticated && <SignInPrompt productId={product.id} />}

        {/* Owned wins over every other state: no purchase to offer. */}
        {isAuthenticated && product.owned && <OwnedNotice />}

        {isAuthenticated && !product.owned && !confirming && (
          <BuyPrompt price={product.price} onStartConfirm={onStartConfirm} />
        )}

        {isAuthenticated && !product.owned && confirming && (
          <ConfirmPurchase
            price={product.price}
            purchasing={purchasing}
            onCancel={onCancel}
            onConfirm={onConfirm}
          />
        )}
      </div>
    </div>
  )
}

function Label({ children }: { children: string }) {
  return (
    <p className="mb-1.5 text-[11px] font-extrabold tracking-[0.12em] text-ink-muted uppercase">
      {children}
    </p>
  )
}

function PriceRow({ price }: { price: string }) {
  return (
    <div className="flex items-end justify-between gap-5 border-b-[2.5px] border-dashed border-ink/18 pb-5">
      <div>
        <Label>Price</Label>
        <CoinAmount amount={price} size="lg" />
      </div>

      <div className="text-right">
        <Label>Total</Label>
        {/* One order is one item, so the total is the price. */}
        <p className="font-display text-[44px] leading-none font-semibold tracking-tight text-tomato tabular-nums">
          {formatGems(price)}
        </p>
      </div>
    </div>
  )
}

function SignInPrompt({ productId }: { productId: number }) {
  const navigate = useNavigate()

  return (
    <div className="space-y-3">
      <Alert tone="info">Sign in to buy this item with your gems.</Alert>

      <Button
        size="lg"
        fullWidth
        onClick={() => navigate('/login', { state: { from: `/products/${productId}` } })}
      >
        Sign in to buy
      </Button>
    </div>
  )
}

function OwnedNotice() {
  return (
    <div className="space-y-3">
      <Button size="lg" fullWidth disabled>
        Already owned
      </Button>

      <p className="text-center text-[13px] font-bold text-ink-soft">
        This item is in your inventory.{' '}
        <Link to="/orders" className="font-extrabold text-tomato hover:underline">
          View your orders
        </Link>
      </p>
    </div>
  )
}

function BuyPrompt({
  price,
  onStartConfirm,
}: {
  price: string
  onStartConfirm: () => void
}) {
  const { user } = useAuth()
  const canAfford = !user || Number(user.gem_balance) >= Number(price)

  return (
    <div className="space-y-3">
      <Button size="lg" fullWidth disabled={!canAfford} onClick={onStartConfirm}>
        {canAfford ? 'Buy now' : 'Not enough gems'}
      </Button>

      <p className="flex items-center justify-center gap-2 text-[13px] font-bold text-ink-soft">
        <span aria-hidden="true" className="block size-4 rounded-full bg-leaf" />
        One per account · delivered to {user?.username} instantly
      </p>
    </div>
  )
}

/** A deliberate second step: gems are spent immediately, with no refund flow. */
function ConfirmPurchase({
  price,
  purchasing,
  onCancel,
  onConfirm,
}: {
  price: string
  purchasing: boolean
  onCancel: () => void
  onConfirm: () => void
}) {
  const { user } = useAuth()

  return (
    <div className="space-y-4 rounded-[20px] border-[2.5px] border-tomato bg-tomato/6 p-5">
      <div className="space-y-1">
        <p className="flex flex-wrap items-center gap-2 font-display text-lg font-semibold text-ink">
          Spend <CoinAmount amount={price} /> on this item?
        </p>

        {user && (
          <p className="text-[13px] font-bold text-ink-muted">
            Your balance is {formatGems(user.gem_balance)} gems.
          </p>
        )}
      </div>

      <div className="flex gap-3">
        <Button className="flex-1" loading={purchasing} onClick={onConfirm}>
          Confirm
        </Button>

        <Button variant="secondary" disabled={purchasing} onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </div>
  )
}
