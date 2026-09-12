import { cn } from '@/lib/cn'

export function Spinner({ className }: { className?: string }) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        'inline-block animate-spin rounded-full border-[3px] border-sand border-t-tomato',
        className ?? 'size-5',
      )}
    />
  )
}
