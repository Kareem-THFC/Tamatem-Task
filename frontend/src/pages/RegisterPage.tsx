import { useState, type SubmitEvent } from 'react'
import { useNavigate } from 'react-router-dom'

import { register } from '@/api/auth'
import { ApiError } from '@/api/client'
import { Button } from '@/components/ui/Button'
import { FormInput } from '@/components/ui/FormInput'
import { useAuth } from '@/context/auth-context'
import { toastError } from '@/lib/toast'
import { validateForm } from '@/lib/validate-form'
import { MIN_PASSWORD_LENGTH, registerSchema } from '@/schemas/auth'

export function RegisterPage() {
  const { signIn } = useAuth()
  const navigate = useNavigate()

  const [values, setValues] = useState({
    username: '',
    email: '',
    password: '',
  })
  const [clientErrors, setClientErrors] = useState<Record<string, string>>({})
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)

  function updateField(field: keyof typeof values, value: string) {
    setValues((current) => ({ ...current, [field]: value }))
  }

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()

    const result = validateForm(registerSchema, values)

    if (!result.success) {
      setClientErrors(result.fieldErrors)
      return
    }

    setClientErrors({})
    setSubmitting(true)
    setError(null)

    try {
      const payload = await register(result.data)

      signIn(payload)
      navigate('/products', { replace: true })
    } catch (caught) {
      const apiError =
        caught instanceof ApiError
          ? caught
          : new ApiError('UNEXPECTED_ERROR', 'Something went wrong.', 0)

      setError(apiError)

      // An error that names a field is rendered under that input, so toasting
      // it too would say the same thing twice. Everything else has nowhere to
      // appear in the form and is toasted instead.
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
        label="Username"
        name="username"
        value={values.username}
        onChange={(event) => updateField('username', event.target.value)}
        error={fieldErrors.username}
        hint="Letters, digits, dots, dashes and underscores."
        autoComplete="username"
        autoFocus
        required
      />

      <FormInput
        label="Email"
        name="email"
        type="email"
        value={values.email}
        onChange={(event) => updateField('email', event.target.value)}
        error={fieldErrors.email}
        autoComplete="email"
        required
      />

      <FormInput
        label="Password"
        name="password"
        type="password"
        value={values.password}
        onChange={(event) => updateField('password', event.target.value)}
        error={fieldErrors.password}
        hint={`At least ${MIN_PASSWORD_LENGTH} characters.`}
        autoComplete="new-password"
        required
      />

      <Button type="submit" size="lg" fullWidth loading={submitting}>
        Create account
      </Button>
    </form>
  )
}
