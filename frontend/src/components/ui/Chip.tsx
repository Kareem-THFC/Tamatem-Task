import type { ButtonHTMLAttributes, ReactNode } from 'react'

import { cn } from '@/lib/cn'

type Tone = 'neutral' | 'violet' | 'violet-soft' | 'sky' | 'coin' | 'leaf' | 'muted'

const TONE_CLASSES: Record<Tone, string> = {
  neutral: 'border-ink bg-surface text-ink',
  violet: 'border-ink bg-violet text-white',
  'violet-soft': 'border-ink bg-violet-bg text-ink',
  sky: 'border-ink bg-sky-bg text-ink',
  coin: 'border-ink bg-coin text-ink',
  leaf: 'border-leaf-dark bg-leaf-bg text-leaf-dark',
  muted: 'border-muted bg-canvas text-muted-ink',
}

const BASE =
  'inline-flex items-center gap-1.5 rounded-full border-[2.5px] px-3.5 py-1.5 font-extrabold'

/** A static pill: region, status, category. */
export function Chip({
  tone = 'neutral',
  className,
  children,
}: {
  tone?: Tone
  className?: string
  children: ReactNode
}) {
  return (
    <span className={cn(BASE, 'text-xs', TONE_CLASSES[tone], className)}>{children}</span>
  )
}

interface FilterChipProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  active: boolean
  children: ReactNode
}

export function FilterChip({ active, className, children, ...props }: FilterChipProps) {
  return (
    <button
      type="button"
      aria-pressed={active}
      className={cn(
        BASE,
        'cursor-pointer border-ink text-[13px] transition-transform duration-150',
        active ? 'bg-ink text-cream' : 'bg-surface text-ink hover:-translate-y-0.5',
        className,
      )}
      {...props}
    >
      {children}
    </button>
  )
}

const PIN_TONES = {
  violet: 'bg-violet',
  white: 'bg-white',
  muted: 'bg-muted',
} as const

export function RegionPin({
  tone = 'violet',
  className,
}: {
  tone?: keyof typeof PIN_TONES
  className?: string
}) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        'block rotate-[-45deg] rounded-tl-full rounded-tr-full rounded-bl-full',
        PIN_TONES[tone],
        className ?? 'size-3',
      )}
    />
  )
}
