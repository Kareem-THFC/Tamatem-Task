import type { HTMLAttributes, ReactNode } from 'react'

import { cn } from '@/lib/cn'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  interactive?: boolean
  children: ReactNode
}

export function Card({ interactive = false, className, children, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-[26px] border-[3px] border-ink bg-surface shadow-hard',
        interactive &&
          cn(
            'transition-[transform,box-shadow] duration-[180ms] ease-[cubic-bezier(.34,1.56,.64,1)]',
            'hover:-translate-y-2 hover:shadow-hard-xl',
          ),
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardBody({ className, children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('p-6', className)} {...props}>
      {children}
    </div>
  )
}
