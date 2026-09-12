import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { ApiError } from '@/api/client'
import { createOrder } from '@/api/orders'
import { ProductShowcase } from '@/components/products/ProductShowcase'
import { PurchasePanel } from '@/components/products/PurchasePanel'
import { Chip, RegionPin } from '@/components/ui/Chip'
import { Skeleton, SkeletonBlock } from '@/components/ui/Skeleton'
import { StatePanel } from '@/components/ui/StatePanel'
import { useAuth } from '@/context/auth-context'
import { useProduct } from '@/hooks/useProduct'
import { toastError } from '@/lib/toast'
import { formatLocation } from '@/lib/format'

export function ProductDetailsPage() {
  const { id } = useParams<{ id: string }>()
  const productId = Number(id)

  const navigate = useNavigate()
  const { user, signOut, setUser } = useAuth()

  const [confirming, setConfirming] = useState(false)
  const [purchasing, setPurchasing] = useState(false)

  const { product, setProduct, loading, error } = useProduct(productId)

  async function handlePurchase() {
    setPurchasing(true)

    try {
      const order = await createOrder(productId)

      if (user) {
        setUser({ ...user, gem_balance: order.gem_balance_after })
      }

      navigate(`/orders/${order.id}`, { replace: true, state: { justPurchased: true } })
    } catch (caught) {
      const apiError =
        caught instanceof ApiError
          ? caught
          : new ApiError('UNEXPECTED_ERROR', 'Something went wrong.', 0)

      if (apiError.code === 'TOKEN_EXPIRED' || apiError.code === 'INVALID_TOKEN') {
        signOut()
        navigate('/login', { state: { from: `/products/${productId}` } })
        return
      }

      if (apiError.code === 'PRODUCT_ALREADY_OWNED') {
        setProduct((current) => (current === null ? null : { ...current, owned: true }))
      }

      toastError(apiError.message)

      setPurchasing(false)
      setConfirming(false)
    }
  }

  if (!Number.isInteger(productId) || productId < 1) {
    return (
      <StatePanel
        title="Item not found"
        description="That product id is not valid."
        action={{ label: 'Back to store', onClick: () => navigate('/products') }}
      />
    )
  }

  if (loading) {
    return <DetailsSkeleton />
  }

  if (error) {
    const notFound = error.code === 'PRODUCT_NOT_FOUND'

    return (
      <StatePanel
        tone={notFound ? 'empty' : 'error'}
        title={notFound ? 'Item not found' : 'Could not load this item'}
        description={error.message}
        action={{ label: 'Back to store', onClick: () => navigate('/products') }}
      />
    )
  }

  if (!product) {
    return null
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-4">
        <Link
          to="/products"
          className="inline-flex items-center gap-2.5 rounded-[14px] border-[2.5px] border-ink bg-cream px-4 py-2.5 text-sm font-extrabold text-ink shadow-hard-xs transition-transform duration-120 hover:-translate-x-0.5"
        >
          <span
            aria-hidden="true"
            className="block size-0 border-y-6 border-r-8 border-y-transparent border-r-ink"
          />
          Back to store
        </Link>

        <p className="text-[13px] font-bold text-ink-muted">
          Store · {formatLocation(product.location)} · {product.title}
        </p>
      </div>

      <div className="overflow-hidden rounded-4xl border-[3px] border-ink bg-cream shadow-hard-lg">
        <div className="grid lg:grid-cols-[1.05fr_1fr]">
          <ProductShowcase productId={product.id} />

          <div className="flex flex-col gap-6 p-8 lg:p-12">
            <div className="flex flex-wrap gap-2.5">
              <Chip tone="violet">
                <RegionPin tone="white" />
                {formatLocation(product.location)}
              </Chip>
              <Chip tone={product.owned ? 'leaf' : 'neutral'}>
                {product.owned ? 'Owned' : 'Available now'}
              </Chip>
            </div>

            <div className="space-y-3">
              <h1 className="font-display text-4xl leading-none font-semibold tracking-tight text-ink sm:text-5xl">
                {product.title}
              </h1>

              <p className="max-w-lg text-base leading-relaxed text-ink-soft">
                {product.description}
              </p>
            </div>

            <PurchasePanel
              product={product}
              confirming={confirming}
              purchasing={purchasing}
              onStartConfirm={() => setConfirming(true)}
              onCancel={() => setConfirming(false)}
              onConfirm={handlePurchase}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

function DetailsSkeleton() {
  return (
    <div role="status" aria-label="Loading item" className="space-y-5">
      <SkeletonBlock className="h-11 w-40 rounded-[14px]" />

      <div className="overflow-hidden rounded-4xl border-[3px] border-ink/30 bg-cream">
        <div className="grid lg:grid-cols-[1.05fr_1fr]">
          <Skeleton className="min-h-85 rounded-none lg:min-h-140" />

          <div className="space-y-5 p-8 lg:p-12">
            <SkeletonBlock className="h-7 w-40 rounded-full" />
            <Skeleton className="h-12 w-3/4" />
            <SkeletonBlock className="h-4 w-full" />
            <SkeletonBlock className="h-4 w-5/6" />
            <SkeletonBlock className="mt-6 h-52 rounded-[26px]" />
          </div>
        </div>
      </div>
    </div>
  )
}
