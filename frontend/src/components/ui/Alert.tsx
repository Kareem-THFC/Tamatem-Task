import type { ReactNode } from 'react'

import { cn } from '@/lib/cn'

type Tone = 'error' | 'success' | 'warning' | 'info'


const TONE_CLASSES: Record<Tone, string> = {
  error: 'border-danger bg-danger-bg text-danger-ink',
  success: 'border-ink bg-ink text-cream',
  warning: 'border-ink bg-coin text-ink',
  info: 'border-ink bg-sky-bg text-ink',
}

const MARK_CLASSES: Record<Tone, string> = {
  error: 'bg-danger text-white',
  success: 'bg-leaf text-ink',
  warning: 'bg-ink text-coin',
  info: 'bg-violet text-white',
}

export function Alert({
  tone = 'error',
  className,
  children,
}: {
  tone?: Tone
  className?: string
  children: ReactNode
}) {
  return (
    <div
      role={tone === 'error' ? 'alert' : 'status'}
      className={cn(
        'flex items-center gap-3 rounded-2xl border-[2.5px] px-4 py-3',
        'text-[13px] font-bold',
        TONE_CLASSES[tone],
        className,
      )}
    >
      <span
        aria-hidden="true"
        className={cn(
          'grid size-5.5 shrink-0 place-items-center rounded-full',
          MARK_CLASSES[tone],
        )}
      >
        {tone === 'success' ? (
          // A tick drawn from two borders on a rotated box.
          <span className="mt-[-2px] block h-[5px] w-[9px] rotate-[-45deg] border-b-[2.5px] border-l-[2.5px] border-current" />
        ) : (
          // An exclamation bar; the same mark serves error, warning and info.
          <span className="block h-2.75 w-[2.5px] rounded-xs bg-current" />
        )}
      </span>

      <span className="min-w-0">{children}</span>
    </div>
  )
}
