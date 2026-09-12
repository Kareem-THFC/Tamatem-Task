import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

import { TomatoMark, TomatoMascot } from '@/components/brand/TomatoMark'
import { Chip } from '@/components/ui/Chip'

export function AuthShell({
  eyebrow,
  title,
  subtitle,
  panelTitle,
  panelText,
  children,
  footer,
}: {
  eyebrow: string
  title: string
  subtitle: string
  panelTitle: string
  panelText: string
  children: ReactNode
  footer: ReactNode
}) {
  return (
   
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="relative hidden flex-col justify-between overflow-hidden border-r-[3px] border-ink bg-linear-[160deg,var(--color-tomato-dark)_0%,var(--color-tomato)_50%,var(--color-tomato-light)_100%] p-12 lg:flex">
        <div aria-hidden="true" className="pointer-events-none absolute inset-0">
          <div className="absolute -top-22 -left-18 size-75 rounded-full bg-white/9" />
          <div className="absolute -right-22 -bottom-30 size-85 rotate-18 rounded-[120px] bg-sky/22" />
          <div className="absolute top-30 right-18 size-11 rotate-45 animate-floaty rounded-xl bg-coin" />
          <div className="absolute top-70 left-15 size-6.5 animate-floaty2 rounded-full bg-coin" />
          <div className="absolute right-38 bottom-48 size-8 animate-floaty rounded-lg bg-sky" />
        </div>

        {/* These pages have no header, so the logo is the only way back. */}
        <Link to="/products" className="relative flex w-fit items-center gap-3">
          <TomatoMark size={44} />
          <span className="font-display text-2xl font-semibold text-white">
            Loot Market
          </span>
        </Link>

        <div className="relative flex flex-col items-center gap-8">
          <TomatoMascot />

          <div className="max-w-md text-center">
            <p className="font-display text-[34px] leading-tight font-semibold text-white">
              {panelTitle}
            </p>
            <p className="mt-2.5 text-base leading-relaxed text-white/82">{panelText}</p>
          </div>
        </div>

        <div aria-hidden="true" className="relative flex items-center gap-2.5">
          <span className="block h-2 w-7 rounded-full bg-coin" />
          <span className="block size-2 rounded-full bg-white/40" />
          <span className="block size-2 rounded-full bg-white/40" />
        </div>
      </div>

      <div className="grid place-items-center bg-[radial-gradient(circle_at_80%_10%,var(--color-sand)_0%,var(--color-cream)_60%)] px-5 py-12 sm:px-12">
        <div className="w-full max-w-113">
          {/* Repeated for the narrow layout, where the red panel that
              normally carries the mark is not rendered. */}
          <Link
            to="/products"
            className="mb-6 flex items-center justify-center gap-2.5 lg:hidden"
          >
            <TomatoMark size={36} />
            <span className="font-display text-xl font-semibold text-ink">
              Loot Market
            </span>
          </Link>

          <div className="rounded-[30px] border-[3px] border-ink bg-surface p-8 shadow-hard-lg sm:p-10">
            <Chip tone="violet-soft" className="mb-5">
              <span aria-hidden="true" className="block size-2.5 rounded-full bg-violet" />
              <span className="tracking-widest uppercase">{eyebrow}</span>
            </Chip>

            <h1 className="font-display text-4xl leading-none font-semibold tracking-tight text-ink">
              {title}
            </h1>

            <p className="mt-2 mb-7 text-[15px] text-ink-muted">{subtitle}</p>

            {children}
          </div>

          <p className="mt-5 text-center text-sm font-semibold text-ink-muted">{footer}</p>

          <p className="mt-3 text-center text-sm font-semibold text-ink-muted">
            <Link to="/products" className="hover:text-ink hover:underline">
              &larr; Back to the store
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
