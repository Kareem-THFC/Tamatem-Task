import { ProductArt } from '@/components/products/ProductArt'

/**
 * The full-bleed art panel on the details page.
 *
 * `ProductArt` sets its own `position: relative`, and `cn` does not resolve
 * Tailwind conflicts — so the size is given here rather than by trying to
 * override that with `absolute inset-0`, which loses and collapses the box.
 */
export function ProductShowcase({ productId }: { productId: number }) {
  return (
    <div className="relative border-ink max-lg:border-b-[3px] lg:border-r-[3px]">
      <ProductArt
        productId={productId}
        shapeSize={150}
        className="h-full min-h-85 lg:min-h-140"
      />

      <div aria-hidden="true" className="pointer-events-none absolute inset-0">
        <div className="absolute top-1/2 left-1/2 size-70 -translate-x-1/2 -translate-y-1/2 animate-ringpulse rounded-full bg-white/14" />
        <div className="absolute top-14 left-14 size-8.5 rotate-20 animate-floaty rounded-xl border-[3px] border-ink bg-sky" />
        <div className="absolute right-16 bottom-20 size-11.5 animate-floaty2 rounded-full border-[3px] border-ink bg-tomato" />
        <div className="absolute bottom-32 left-22 size-6 rotate-45 animate-floaty rounded-lg bg-coin" />
      </div>
    </div>
  )
}
