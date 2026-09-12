import toast from 'react-hot-toast'

import { ToastBody } from '@/components/ui/ToastBody'

export function toastError(message: string): void {
  toast.custom((t) => <ToastBody t={t} tone="error" message={message} />, {
    id: message,
    duration: 6000,
  })
}

export function toastSuccess(message: string): void {
  toast.custom((t) => <ToastBody t={t} tone="success" message={message} />, {
    id: message,
    duration: 4000,
  })
}
