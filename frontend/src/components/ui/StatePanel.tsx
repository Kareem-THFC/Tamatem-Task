import type { ReactNode } from 'react'

import { Button } from '@/components/ui/Button'

function EmptyMark() {
  return (
    <div aria-hidden="true" className="relative size-30">
      <div className="absolute inset-0 rounded-[38px] border-[3px] border-dashed border-violet bg-violet-bg" />
      <div className="absolute top-13 left-8.5 h-5.5 w-4 rounded-full bg-violet" />
      <div className="absolute top-13 left-17.5 h-5.5 w-4 rounded-full bg-violet" />
      <div className="absolute top-21.5 left-11 h-3 w-8 rounded-t-[26px] bg-violet" />
    </div>
  )
}

function ErrorMark() {
  return (
    <div
      aria-hidden="true"
      className="grid size-17.5 place-items-center rounded-3xl border-[3px] border-ink bg-danger shadow-[0_6px_0_rgba(42,26,20,0.25)]"
    >
      <span className="block h-7.5 w-1.25 rounded-[3px] bg-white" />
    </div>
  )
}


export function StatePanel({
  tone = 'empty',
  title,
  description,
  action,
  secondaryAction,
}: {
  tone?: 'empty' | 'error'
  title: string
  description?: ReactNode
  action?: { label: string; onClick: () => void }
  secondaryAction?: { label: string; onClick: () => void }
}) {
  const isError = tone === 'error'

  return (
    <div
      className={
        isError
          ? 'flex flex-col items-center gap-4 rounded-[26px] border-[3px] border-danger bg-danger-bg px-6 py-12 text-center'
          : 'flex flex-col items-center gap-4 rounded-[26px] border-[3px] border-ink bg-cream px-6 py-14 text-center shadow-hard'
      }
    >
      {isError ? <ErrorMark /> : <EmptyMark />}

      <div className="space-y-2">
        <p className="font-display text-2xl font-semibold text-ink">{title}</p>

        {description && (
          <p
            className={`mx-auto max-w-sm text-sm leading-relaxed ${
              isError ? 'text-danger-ink' : 'text-ink-muted'
            }`}
          >
            {description}
          </p>
        )}
      </div>

      {(action || secondaryAction) && (
        <div className="flex flex-wrap items-center justify-center gap-3 pt-1">
          {action && (
            <Button size="sm" onClick={action.onClick}>
              {action.label}
            </Button>
          )}

          {secondaryAction && (
            <Button size="sm" variant="secondary" onClick={secondaryAction.onClick}>
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}
    </div>
  )
}
