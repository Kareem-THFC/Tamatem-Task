import { createContext, use } from 'react'

import type { AuthPayload, User } from '@/types/api'

export interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  signIn: (payload: AuthPayload) => void
  signOut: () => void
  setUser: (user: User) => void
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function useAuth(): AuthContextValue {
  const context = use(AuthContext)

  if (context === undefined) {
    throw new Error('useAuth must be used inside <AuthProvider>.')
  }

  return context
}
