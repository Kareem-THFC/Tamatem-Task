import { Spinner } from '@/components/ui/Spinner'
import { cn } from '@/lib/cn'
import type { Pagination as PaginationMeta } from '@/types/api'

function pageItems(page: number, pages: number): Array<number | 'gap'> {
  if (pages <= 7) {
    return Array.from({ length: pages }, (_, index) => index + 1)
  }

  const items: Array<number | 'gap'> = [1]

  const start = Math.max(2, page - 1)
  const end = Math.min(pages - 1, page + 1)

  if (start > 2) {
    items.push('gap')
  }

  for (let index = start; index <= end; index += 1) {
    items.push(index)
  }

  if (end < pages - 1) {
    items.push('gap')
  }

  items.push(pages)

  return items
}

const CELL =
  'grid size-11 place-items-center rounded-[14px] border-[2.5px] font-display text-lg font-semibold'

export function Pagination({
  pagination,
  onPageChange,
  disabled = false,
  busy = false,
  noun = 'items in stock',
}: {
  pagination: PaginationMeta
  onPageChange: (page: number) => void
  disabled?: boolean
  busy?: boolean
  noun?: string
}) {
  const { page, pages, total } = pagination

  if (total === 0) {
    return null
  }

  const summary = (
    <p className="flex items-center gap-2.5 text-sm font-bold text-ink-soft">
      {busy && <Spinner className="size-4" />}

      <span>
        <span className="font-display text-xl font-semibold text-ink tabular-nums">
          {total}
        </span>{' '}
        {noun} · page {page} of {Math.max(pages, 1)}
      </span>
    </p>
  )

  if (pages <= 1) {
    return <div className="flex justify-center">{summary}</div>
  }

  return (
    <nav
      aria-label="Pagination"
      className="flex flex-wrap items-center justify-between gap-4"
    >
      {summary}

      <div className="flex flex-wrap items-center gap-2.5">
        <Arrow
          direction="previous"
          disabled={disabled || page <= 1}
          onClick={() => onPageChange(page - 1)}
        />

        {pageItems(page, pages).map((item, index) =>
          item === 'gap' ? (
            <span
              key={`gap-${index}`}
              aria-hidden="true"
              className="px-1 font-extrabold text-ink-muted"
            >
              ···
            </span>
          ) : (
            <button
              key={item}
              type="button"
              disabled={disabled}
              aria-current={item === page ? 'page' : undefined}
              aria-label={`Page ${item}`}
              onClick={() => onPageChange(item)}
              className={cn(
                CELL,
                'border-ink transition-transform duration-150',
                item === page
                  ? 'bg-tomato text-white shadow-[0_4px_0_#9E1C15]'
                  : 'cursor-pointer bg-surface text-ink shadow-hard-xs hover:-translate-y-0.5',
                disabled && 'cursor-not-allowed opacity-60',
              )}
            >
              {item}
            </button>
          ),
        )}

        <Arrow
          direction="next"
          disabled={disabled || page >= pages}
          onClick={() => onPageChange(page + 1)}
        />
      </div>
    </nav>
  )
}

function Arrow({
  direction,
  disabled,
  onClick,
}: {
  direction: 'previous' | 'next'
  disabled: boolean
  onClick: () => void
}) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      aria-label={direction === 'previous' ? 'Previous page' : 'Next page'}
      className={cn(
        CELL,
        'text-base font-extrabold',
        disabled
          ? 'cursor-not-allowed border-muted bg-canvas text-muted'
          : 'cursor-pointer border-ink bg-surface text-ink shadow-hard-xs transition-transform duration-150 hover:-translate-y-0.5',
      )}
    >
      <span aria-hidden="true">{direction === 'previous' ? '‹' : '›'}</span>
    </button>
  )
}
