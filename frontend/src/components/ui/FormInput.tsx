import { useId, useState, type InputHTMLAttributes } from 'react'

import { cn } from '@/lib/cn'

interface FormInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'id'> {
  label: string
  error?: string
  hint?: string
}

export function FormInput({
  label,
  error,
  hint,
  className,
  type = 'text',
  ...props
}: FormInputProps) {
  const id = useId()
  const messageId = `${id}-message`
  const message = error ?? hint

  const isPassword = type === 'password'
  const [revealed, setRevealed] = useState(false)

  return (
    <div className="space-y-2">
      <label
        htmlFor={id}
        className="block text-xs font-extrabold tracking-[0.08em] text-ink-soft uppercase"
      >
        {label}
      </label>

      <div
        className={cn(
          'flex items-center gap-2.5 rounded-2xl border-[2.5px] px-4 py-3',
          'transition-shadow',
          error
            ? 'border-danger bg-danger-bg shadow-[0_4px_0_rgba(196,35,27,0.28)]'
            : cn(
                'border-ink bg-cream shadow-hard-xs',
                'focus-within:border-violet focus-within:shadow-[0_0_0_4px_rgba(123,92,255,0.22),0_4px_0_rgba(42,26,20,0.12)]',
              ),
        )}
      >
        <input
          id={id}
          type={isPassword && revealed ? 'text' : type}
          className={cn(
            'w-full bg-transparent text-base font-semibold text-ink',
            'placeholder:font-semibold placeholder:text-muted',
            'focus:outline-none',
            'disabled:opacity-50',
            className,
          )}
          {...props}
        />

        {isPassword && (
          <button
            type="button"
            onClick={() => setRevealed((current) => !current)}
            className="shrink-0 cursor-pointer text-xs font-extrabold text-ink-muted hover:text-ink"
          >
            {revealed ? 'HIDE' : 'SHOW'}
          </button>
        )}
      </div>

      {message && (
        <p
          id={messageId}
          className={cn(
            'flex items-center gap-2 text-[13px] font-bold',
            error ? 'text-danger' : 'text-ink-muted',
          )}
        >
          {error && (
            <span
              aria-hidden="true"
              className="grid size-4.5 shrink-0 place-items-center rounded-full bg-danger"
            >
              <span className="block h-2.25 w-[2.5px] rounded-xs bg-white" />
            </span>
          )}
          {message}
        </p>
      )}
    </div>
  )
}
