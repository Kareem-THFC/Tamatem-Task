import { useNavigate } from 'react-router-dom'

import { StatePanel } from '@/components/ui/StatePanel'

/** Rendered by the catch-all `*` route when no other path matches. */
export function NotFoundPage() {
  const navigate = useNavigate()

  return (
    <StatePanel
      title="Page not found"
      description="That URL does not exist in the market."
      action={{ label: 'Back to store', onClick: () => navigate('/products') }}
    />
  )
}
