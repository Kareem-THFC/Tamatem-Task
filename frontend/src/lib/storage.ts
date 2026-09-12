import type { User } from '@/types/api'

const TOKEN_KEY = 'tamatem.token'
const USER_KEY = 'tamatem.user'

export interface StoredSession {
  token: string
  user: User
}

export function readSession(): StoredSession | null {
  try {
    const token = localStorage.getItem(TOKEN_KEY)
    const rawUser = localStorage.getItem(USER_KEY)

    if (!token || !rawUser) {
      return null
    }

    return { token, user: JSON.parse(rawUser) as User }
  } catch {
    // Unreadable or corrupted storage reads as "not signed in".
    return null
  }
}

export function writeSession(session: StoredSession): void {
  try {
    localStorage.setItem(TOKEN_KEY, session.token)
    localStorage.setItem(USER_KEY, JSON.stringify(session.user))
  } catch {
    // Persisting is a convenience; the session still works for this tab.
  }
}

export function clearSession(): void {
  try {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  } catch {
    // The caller clears the in-memory state regardless.
  }
}
