import { useState, type SubmitEvent } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { login } from '@/api/auth'
import { ApiError } from '@/api/client'
import { Button } from '@/components/ui/Button'
import { FormInput } from '@/components/ui/FormInput'
import { useAuth } from '@/context/auth-context'
import { toastError } from '@/lib/toast'
import { validateForm } from '@/lib/validate-form'
import { loginSchema } from '@/schemas/auth'

export function LoginPage() {
  const { signIn } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [clientErrors, setClientErrors] = useState<Record<string, string>>({})
  const [error, setError] = useState<ApiError | null>(null)

  const redirectTo = (location.state as { from?: string } | null)?.from ?? '/products'

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()

    const result = validateForm(loginSchema, { identifier, password })

    if (!result.success) {
      setClientErrors(result.fieldErrors)
      return
    }

    setClientErrors({})
    setSubmitting(true)
    setError(null)

    try {
      const payload = await login(result.data)

      signIn(payload)
      navigate(redirectTo, { replace: true })
    } catch (caught) {
      const apiError =
        caught instanceof ApiError
          ? caught
          : new ApiError('UNEXPECTED_ERROR', 'Something went wrong.', 0)

      setError(apiError)

      if (Object.keys(apiError.fieldErrors()).length === 0) {
        toastError(apiError.message)
      }

      setSubmitting(false)
    }
  }

  const fieldErrors = { ...(error?.fieldErrors() ?? {}), ...clientErrors }

  return (
    <form onSubmit={handleSubmit} className="space-y-5" noValidate>
      <FormInput
        label="Username or email"
        name="identifier"
        value={identifier}
        onChange={(event) => setIdentifier(event.target.value)}
        error={fieldErrors.identifier}
        autoComplete="username"
        autoFocus
        required
      />

      <FormInput
        label="Password"
        name="password"
        type="password"
        value={password}
        onChange={(event) => setPassword(event.target.value)}
        error={fieldErrors.password}
        autoComplete="current-password"
        required
      />

      <Button
        type="submit"
        size="lg"
        fullWidth
        loading={submitting}
        disabled={!identifier || !password}
      >
        Enter the market
      </Button>
    </form>
  )
}
