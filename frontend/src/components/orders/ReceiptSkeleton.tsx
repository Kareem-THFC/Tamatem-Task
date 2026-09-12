import { Skeleton, SkeletonBlock } from '@/components/ui/Skeleton'

export function ReceiptSkeleton() {
  return (
    <div role="status" aria-label="Loading receipt" className="mx-auto max-w-2xl space-y-5">
      <Skeleton className="h-9 w-48" />

      <div className="space-y-4 rounded-[28px] border-[3px] border-ink/30 bg-surface p-8">
        <SkeletonBlock className="h-6 w-full" />
        <Skeleton className="h-16 w-full rounded-[20px]" />
        <SkeletonBlock className="h-24 w-full" />
        <SkeletonBlock className="h-12 w-full" />
      </div>
    </div>
  )
}
