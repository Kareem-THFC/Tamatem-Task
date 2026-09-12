import { Navigate, Outlet } from 'react-router-dom'

import { useAuth } from '@/context/auth-context'

/** Keeps a signed-in user off the login and registration pages. */
export function RedirectIfAuthenticated() {
  const { isAuthenticated } = useAuth()

  return isAuthenticated ? <Navigate to="/products" replace /> : <Outlet />
}
