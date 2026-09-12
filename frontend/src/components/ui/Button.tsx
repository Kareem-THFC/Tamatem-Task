import type { ButtonHTMLAttributes, ReactNode } from 'react'

import { Spinner } from '@/components/ui/Spinner'
import { cn } from '@/lib/cn'

type Variant = 'primary' | 'secondary' | 'accent' | 'coin'
type Size = 'sm' | 'md' | 'lg'

const VARIANT_CLASSES: Record<Variant, string> = {
  primary: cn(
    'border-ink bg-tomato text-white',
    'shadow-[0_6px_0_#9E1C15] hover:shadow-[0_8px_0_#9E1C15] active:shadow-[0_1px_0_#9E1C15]',
  ),
  secondary: cn(
    'border-ink bg-surface text-ink',
    'shadow-[0_6px_0_rgba(42,26,20,0.2)] hover:shadow-[0_8px_0_rgba(42,26,20,0.2)]',
    'active:shadow-[0_1px_0_rgba(42,26,20,0.2)]',
  ),
  accent: cn(
    'border-ink bg-violet text-white',
    'shadow-[0_6px_0_#4A2FC7] hover:shadow-[0_8px_0_#4A2FC7] active:shadow-[0_1px_0_#4A2FC7]',
  ),
  coin: cn(
    'border-ink bg-coin text-ink',
    'shadow-[0_6px_0_rgba(42,26,20,0.3)] hover:shadow-[0_8px_0_rgba(42,26,20,0.3)]',
    'active:shadow-[0_1px_0_rgba(42,26,20,0.3)]',
  ),
}

const SIZE_CLASSES: Record<Size, string> = {
  sm: 'rounded-xl border-[2.5px] px-4 py-2 text-[15px]',
  md: 'rounded-2xl border-[3px] px-6 py-3 text-[17px]',
  lg: 'rounded-[20px] border-[3px] px-7 py-4 text-[21px]',
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  loading?: boolean
  fullWidth?: boolean
  children: ReactNode
}

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  fullWidth = false,
  disabled,
  className,
  children,
  ...props
}: ButtonProps) {
  const isDisabled = disabled || loading

  return (
    <button
      disabled={isDisabled}
      className={cn(
        'inline-flex items-center justify-center gap-2 border font-display leading-none',
        'transition-[transform,box-shadow] duration-120',
        SIZE_CLASSES[size],
        fullWidth && 'w-full',

        isDisabled
          ? // No shadow at all: with nothing to sink onto, it reads as inert.
            'cursor-not-allowed border-muted bg-canvas text-muted-ink shadow-none'
          : cn(
              VARIANT_CLASSES[variant],
              'cursor-pointer hover:-translate-y-0.5 active:translate-y-1.25',
            ),
        className,
      )}
      {...props}
    >
      {loading && <Spinner className="size-[1em]" />}
      {children}
    </button>
  )
}
