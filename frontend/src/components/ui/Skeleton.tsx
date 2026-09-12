import { cn } from '@/lib/cn'

export function Skeleton({ className }: { className?: string }) {
  return <div aria-hidden="true" className={cn('skeleton-shimmer rounded-lg', className)} />
}

export function SkeletonBlock({ className }: { className?: string }) {
  return <div aria-hidden="true" className={cn('rounded-lg bg-canvas', className)} />
}
