import { useCallback, useMemo, useState, type ReactNode } from 'react'

import { AuthContext, type AuthContextValue } from '@/context/auth-context'
import { clearSession, readSession, writeSession } from '@/lib/storage'
import type { AuthPayload, User } from '@/types/api'


export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUserState] = useState<User | null>(() => readSession()?.user ?? null)

  const signIn = useCallback((payload: AuthPayload) => {
    writeSession({ token: payload.access_token, user: payload.user })
    setUserState(payload.user)
  }, [])

  const signOut = useCallback(() => {
    clearSession()
    setUserState(null)
  }, [])

  const setUser = useCallback((nextUser: User) => {
    const session = readSession()

    if (session) {
      writeSession({ ...session, user: nextUser })
    }

    setUserState(nextUser)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({ user, isAuthenticated: user !== null, signIn, signOut, setUser }),
    [user, signIn, signOut, setUser],
  )

  return <AuthContext value={value}>{children}</AuthContext>
}
