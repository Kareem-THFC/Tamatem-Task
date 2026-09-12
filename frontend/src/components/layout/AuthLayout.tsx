import { Outlet, useLocation } from 'react-router-dom'

import { authScreenFor } from '@/components/auth/auth-screens'
import { AuthShell } from '@/components/auth/AuthShell'

export function AuthLayout() {
  const { pathname } = useLocation()

  return (
    <div className="min-h-screen bg-canvas">
      <AuthShell {...authScreenFor(pathname)}>
        <Outlet />
      </AuthShell>
    </div>
  )
}
