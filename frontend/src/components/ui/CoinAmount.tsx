import { cn } from '@/lib/cn'
import { formatGems } from '@/lib/format'

type Size = 'sm' | 'md' | 'lg' | 'xl'

const SIZE_CLASSES: Record<Size, { text: string; coin: string }> = {
  sm: { text: 'text-sm', coin: 'size-3.5 border-2' },
  md: { text: 'text-lg', coin: 'size-5 border-[2.5px]' },
  lg: { text: 'text-2xl', coin: 'size-6 border-[2.5px]' },
  xl: { text: 'text-[44px] leading-none', coin: 'size-9 border-[3px]' },
}

export function CoinAmount({
  amount,
  size = 'md',
  className,
}: {
  amount: string
  size?: Size
  className?: string
}) {
  const styles = SIZE_CLASSES[size]

  return (
    <span className={cn('inline-flex items-center gap-2', className)}>
      <span
        aria-hidden="true"
        className={cn('block shrink-0 rounded-full border-ink bg-coin', styles.coin)}
      />
      <span className={cn('font-display font-semibold tabular-nums', styles.text)}>
        {formatGems(amount)}
      </span>
    </span>
  )
}
