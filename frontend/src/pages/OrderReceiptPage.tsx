import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'

import { OrderReceipt } from '@/components/orders/OrderReceipt'
import { PurchaseCelebration } from '@/components/orders/PurchaseCelebration'
import { ReceiptSkeleton } from '@/components/orders/ReceiptSkeleton'
import { StatePanel } from '@/components/ui/StatePanel'
import { useOrder } from '@/hooks/useOrder'

export function OrderReceiptPage() {
  const { id } = useParams<{ id: string }>()
  const orderId = Number(id)

  const navigate = useNavigate()
  const location = useLocation()

  const justPurchased = Boolean(
    (location.state as { justPurchased?: boolean } | null)?.justPurchased,
  )

  const { order, loading, error } = useOrder(orderId)

  if (loading) {
    return <ReceiptSkeleton />
  }

  if (error) {
    const notFound = error.code === 'ORDER_NOT_FOUND'

    return (
      <StatePanel
        tone={notFound ? 'empty' : 'error'}
        title={notFound ? 'Receipt not found' : 'Could not load this receipt'}
        description={error.message}
        action={{ label: 'My orders', onClick: () => navigate('/orders') }}
      />
    )
  }

  if (!order) {
    return null
  }

  if (justPurchased) {
    return (
      <PurchaseCelebration productTitle={order.product.title}>
        <OrderReceipt order={order} />
      </PurchaseCelebration>
    )
  }

  return (
    <div className="mx-auto max-w-2xl space-y-5">
      <div className="space-y-1">
        <Link to="/orders" className="text-sm font-bold text-ink-muted hover:text-ink">
          &larr; Back to my orders
        </Link>

        <h1 className="font-display text-3xl font-semibold tracking-tight text-ink">
          Order #{order.id}
        </h1>
      </div>

      <OrderReceipt order={order} />
    </div>
  )
}
