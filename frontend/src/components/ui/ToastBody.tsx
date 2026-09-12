import toast, { type Toast } from 'react-hot-toast'

import { cn } from '@/lib/cn'


type Tone = 'error' | 'success'

const TONE_CLASSES: Record<Tone, string> = {
  
  error: 'border-danger bg-danger-bg text-danger-ink',
  success: 'border-ink bg-ink text-cream',
}

const MARK_CLASSES: Record<Tone, string> = {
  error: 'bg-danger text-white',
  success: 'bg-leaf text-ink',
}

export function ToastBody({
  t,
  tone,
  message,
}: {
  t: Toast
  tone: Tone
  message: string
}) {
  return (
    <div
      
      role={tone === 'error' ? 'alert' : 'status'}
      className={cn(
        'pointer-events-auto flex max-w-md items-center gap-3 rounded-2xl border-[2.5px] px-4 py-3',
        'text-[13px] font-bold shadow-hard',
        TONE_CLASSES[tone],
        t.visible ? 'animate-rise' : 'opacity-0 transition-opacity duration-150',
      )}
    >
      <span
        aria-hidden="true"
        className={cn(
          'grid size-5.5 shrink-0 place-items-center rounded-full',
          MARK_CLASSES[tone],
        )}
      >
        {tone === 'success' ? (
          <span className="mt-[-2px] block h-[5px] w-[9px] rotate-[-45deg] border-b-[2.5px] border-l-[2.5px] border-current" />
        ) : (
          <span className="block h-2.75 w-[2.5px] rounded-xs bg-current" />
        )}
      </span>

      <span className="min-w-0">{message}</span>

      <button
        type="button"
        onClick={() => toast.dismiss(t.id)}
        aria-label="Dismiss"
        className="-mr-1 ml-auto shrink-0 cursor-pointer rounded-full px-2 text-base leading-none font-extrabold opacity-60 hover:opacity-100"
      >
        <span aria-hidden="true">×</span>
      </button>
    </div>
  )
}

