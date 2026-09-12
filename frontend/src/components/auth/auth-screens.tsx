import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

/**
 * The copy that differs between the two auth screens. Hoisted out of the pages
 * so `AuthLayout` renders one shell and swaps the words, which is what stops
 * the card blinking on the login/register switch.
 */
export interface AuthScreen {
  eyebrow: string
  title: string
  subtitle: string
  panelTitle: string
  panelText: string
  footer: ReactNode
}

const login: AuthScreen = {
  eyebrow: 'Player login',
  title: 'Welcome back!',
  subtitle: 'Enter your credentials to open the market.',
  panelTitle: 'Your stash is waiting',
  panelText:
    'Sign in to browse regional drops and spend the gems in your balance.',
  footer: (
    <>
      No account yet?{' '}
      <Link to="/register" className="font-extrabold text-tomato hover:underline">
        Create one
      </Link>
    </>
  ),
}

const register: AuthScreen = {
  eyebrow: 'New player',
  title: 'Create your account',
  subtitle: 'New accounts start with 500 gems to spend.',
  panelTitle: 'Start with 500 gems',
  panelText:
    'Create an account and the market opens straight away — no verification step, no waiting.',
  footer: (
    <>
      Already registered?{' '}
      <Link to="/login" className="font-extrabold text-tomato hover:underline">
        Sign in
      </Link>
    </>
  ),
}

const BY_PATH: Record<string, AuthScreen> = {
  '/login': login,
  '/register': register,
}

/** Pick the copy for the current path; the fallback is purely defensive. */
export function authScreenFor(pathname: string): AuthScreen {
  return BY_PATH[pathname] ?? login
}
