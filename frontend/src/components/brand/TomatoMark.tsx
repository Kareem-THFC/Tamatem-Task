import { cn } from '@/lib/cn'

export function TomatoMark({
  size = 40,
  className,
}: {
  size?: number
  className?: string
}) {
  const leafWidth = size * 0.4
  const leafHeight = size * 0.2
  const border = Math.max(2, Math.round(size * 0.075))

  return (
    <span
      role="img"
      aria-label="Loot Market"
      className={cn('relative block shrink-0', className)}
      style={{ width: size, height: size }}
    >
      <span
        className="absolute inset-0 block rounded-full border-ink"
        style={{
          borderWidth: border,
          background: 'radial-gradient(circle at 32% 28%, #FF6A57, #E63329)',
          boxShadow: `0 ${Math.round(size * 0.1)}px 0 rgba(42,26,20,.25)`,
        }}
      />

      <span
        className="absolute left-1/2 block -translate-x-1/2 border-ink bg-leaf"
        style={{
          width: leafWidth,
          height: leafHeight,
          top: -leafHeight * 0.9,
          borderWidth: Math.max(2, border - 0.5),
          borderRadius: `${leafHeight}px ${leafHeight}px ${size * 0.07}px ${size * 0.07}px`,
        }}
      />
    </span>
  )
}

export function TomatoMascot({ className }: { className?: string }) {
  return (
    <div
      aria-hidden="true"
      className={cn('relative size-[250px] shrink-0', className)}
    >
      <div className="absolute inset-0 rounded-full bg-cream/20" />
      <div className="absolute inset-3.5 rounded-full bg-cream" />

      <div className="absolute inset-6.5 animate-bob">
        <div
          className="absolute inset-0 rounded-full border-4 border-ink shadow-[0_12px_0_rgba(42,26,20,0.35)]"
          style={{
            background:
              'radial-gradient(circle at 32% 26%, #FF7A63, #E63329 62%, #B81E17)',
          }}
        />

        <div className="absolute top-[62px] left-[52px] h-9 w-7 rounded-full bg-ink" />
        <div className="absolute top-[62px] left-[120px] h-9 w-7 rounded-full bg-ink" />
        <div className="absolute top-[118px] left-[72px] h-5.5 w-14 rounded-b-[28px] bg-cream" />
      </div>

      <div className="absolute top-2.5 left-[88px] h-7.5 w-[74px] animate-bob rounded-t-[30px] rounded-b-[9px] border-4 border-ink bg-leaf" />
      <div className="absolute -top-2.5 left-[114px] h-7 w-4 animate-bob rounded-lg border-[3px] border-ink bg-leaf-dark" />

      <div className="absolute top-[62px] -left-1.5 size-11.5 -rotate-12 animate-floaty rounded-[14px] border-[3px] border-ink bg-coin" />
      <div className="absolute -right-3.5 bottom-11 size-13.5 animate-floaty2 rounded-full border-[3px] border-ink bg-sky" />
    </div>
  )
}
