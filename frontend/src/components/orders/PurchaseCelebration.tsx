import { type ReactNode } from 'react'

const CONFETTI = [
  { left: '8%', color: 'bg-coin', size: 'h-5 w-3.5 rounded-[3px]', duration: 3.4, delay: 0 },
  { left: '17%', color: 'bg-cream', size: 'size-3 rounded-full', duration: 4, delay: 0.4 },
  { left: '26%', color: 'bg-sky', size: 'size-4 rounded', duration: 3.1, delay: 0.9 },
  { left: '34%', color: 'bg-leaf', size: 'h-5.5 w-2.5 rounded-[3px]', duration: 3.8, delay: 0.2 },
  { left: '44%', color: 'bg-cream', size: 'size-3.5 rounded-full', duration: 4.4, delay: 1.2 },
  { left: '56%', color: 'bg-coin', size: 'h-5 w-4 rounded-[3px]', duration: 3.3, delay: 0.7 },
  { left: '64%', color: 'bg-coin', size: 'size-3 rounded', duration: 4.1, delay: 0.1 },
  { left: '73%', color: 'bg-sky', size: 'size-4.5 rounded-full', duration: 3.6, delay: 1.5 },
  { left: '82%', color: 'bg-cream', size: 'h-5 w-3 rounded-[3px]', duration: 4.2, delay: 0.5 },
  { left: '91%', color: 'bg-leaf', size: 'size-3.5 rounded', duration: 3.5, delay: 1 },
]

/**
 * The celebration wrapper shown once, right after a purchase. Whatever it is
 * given — in practice the receipt — sits below the banner.
 */
export function PurchaseCelebration({
  productTitle,
  children,
}: {
  productTitle: string
  children: ReactNode
}) {
  return (
    <div className="relative overflow-hidden rounded-4xl border-[3px] border-ink bg-linear-[165deg,var(--color-tomato-dark)_0%,var(--color-tomato)_52%,var(--color-tomato-light)_100%] px-5 py-12 shadow-hard-lg sm:px-10">
      <Confetti />

      <div aria-hidden="true" className="pointer-events-none absolute inset-0">
        <div className="absolute -top-16 -left-14 size-70 rounded-full bg-white/8" />
        <div className="absolute -right-14 -bottom-24 size-80 rotate-20 rounded-[110px] bg-sky/18" />
      </div>

      <div className="relative mx-auto flex max-w-2xl flex-col items-center gap-6">
        <SuccessBadge />

        <div className="text-center">
          <span className="mb-4 inline-flex items-center gap-2.5 rounded-full border-[3px] border-ink bg-coin px-4.5 py-1.5 shadow-[0_5px_0_rgba(42,26,20,0.3)]">
            <span aria-hidden="true" className="block size-3.5 rotate-45 rounded bg-ink" />
            <span className="text-xs font-extrabold tracking-[0.16em] text-ink uppercase">
              Achievement unlocked
            </span>
          </span>

          <h1 className="font-display text-5xl leading-none font-semibold tracking-tight text-white sm:text-[62px]">
            Purchase complete!
          </h1>

          <p className="mt-3 text-[17px] text-white/85">
            {productTitle} is already sitting in your inventory.
          </p>
        </div>

        <div className="w-full">{children}</div>
      </div>
    </div>
  )
}

/** The bouncing tick, with its two orbiting shapes. */
function SuccessBadge() {
  return (
    <div className="relative grid size-48 animate-pop place-items-center">
      <div className="absolute inset-0 animate-ringpulse rounded-full bg-white/20" />

      <div className="relative grid size-38 animate-bob place-items-center rounded-full border-[5px] border-ink bg-leaf shadow-[0_12px_0_rgba(42,26,20,0.35)]">
        <span
          aria-hidden="true"
          className="-mt-2 block h-7.5 w-14 -rotate-45 rounded-[3px] border-b-11 border-l-11 border-cream"
        />
      </div>

      <div className="absolute top-6 -left-2.5 size-8.5 rotate-45 animate-floaty rounded-xl border-[3px] border-ink bg-coin" />
      <div className="absolute -right-1 bottom-4 size-7 animate-floaty2 rounded-full border-[3px] border-ink bg-sky" />
    </div>
  )
}

function Confetti() {
  return (
    <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden">
      {CONFETTI.map((piece) => (
        <span
          key={piece.left}
          className={`absolute top-0 animate-confetti ${piece.color} ${piece.size}`}
          style={{
            left: piece.left,
            animationDuration: `${piece.duration}s`,
            animationDelay: `${piece.delay}s`,
          }}
        />
      ))}
    </div>
  )
}
