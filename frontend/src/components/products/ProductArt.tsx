import { cn } from '@/lib/cn'

interface Theme {
  /** The gradient field. */
  background: string
  /** Angle of the stripe overlay, in degrees. */
  stripes: number
  /** Fill of the centre shape. */
  shape: string
}

const THEMES: Theme[] = [
  { background: 'radial-gradient(circle at 30% 25%, #9A7BFF, #5B3EE8)', stripes: 45, shape: '#FFC53D' },
  { background: 'radial-gradient(circle at 70% 20%, #7EDBFF, #2296D8)', stripes: -45, shape: '#FFF3E4' },
  { background: 'radial-gradient(circle at 40% 30%, #FF8A6E, #C4231B)', stripes: 90, shape: '#FFF3E4' },
  { background: 'radial-gradient(circle at 50% 30%, #86D98F, #2E8B3C)', stripes: 45, shape: '#FFF3E4' },
  { background: 'radial-gradient(circle at 60% 25%, #FFD86B, #E39A00)', stripes: -45, shape: '#FFF3E4' },
]

/** How the centre shape is cut. Paired with a theme by the same id. */
const SHAPES = [
  'rotate-45 rounded-[14px]', // a diamond
  'rounded-full', // a disc
  'rounded-[22px]', // a rounded square
  'rounded-[14px]', // a plain tile
  'rotate-45 rounded-full', // a rotated disc reads as a circle
] as const

export function ProductArt({
  productId,
  className,
  shapeSize = 64,
}: {
  productId: number
  className?: string
  shapeSize?: number
}) {
  const theme = THEMES[productId % THEMES.length]
  const shape = SHAPES[productId % SHAPES.length]

  return (
    <div
      aria-hidden="true"
      className={cn('relative overflow-hidden', className)}
      style={{ background: theme.background }}
    >
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: `repeating-linear-gradient(${theme.stripes}deg, rgba(255,255,255,.09) 0 10px, transparent 10px 20px)`,
        }}
      />

      <div
        className={cn(
          'absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2',
          'border-[3px] border-ink shadow-[0_6px_0_rgba(42,26,20,0.3)]',
          shape,
        )}
        style={{ width: shapeSize, height: shapeSize, background: theme.shape }}
      />
    </div>
  )
}
