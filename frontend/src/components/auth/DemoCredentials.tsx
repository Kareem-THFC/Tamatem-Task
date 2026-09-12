import { Button } from '@/components/ui/Button'

/**
 * The deployed demo seeds a throwaway account so a reviewer can sign in without
 * registering first. The credentials come from the build environment rather
 * than a literal, so a build without them -- any local one -- renders nothing
 * and the login screen is exactly what a real user would see.
 */
const username = import.meta.env.VITE_DEMO_USERNAME
const password = import.meta.env.VITE_DEMO_PASSWORD

export const demoCredentials =
  username && password ? { identifier: username, password } : null

interface DemoCredentialsProps {
  onFill: () => void
  disabled?: boolean
}

export function DemoCredentials({ onFill, disabled }: DemoCredentialsProps) {
  if (demoCredentials === null) {
    return null
  }

  return (
    <div className="rounded-2xl border-[3px] border-dashed border-ink/25 bg-canvas px-4 py-3.5">
      <p className="font-display text-[15px] leading-none text-ink">
        Reviewing this project?
      </p>

      <dl className="mt-2.5 space-y-1 text-[14px] text-muted-ink">
        <div className="flex items-baseline gap-2">
          <dt className="w-[74px] shrink-0">Username</dt>
          <dd className="font-mono text-ink">{demoCredentials.identifier}</dd>
        </div>
        <div className="flex items-baseline gap-2">
          <dt className="w-[74px] shrink-0">Password</dt>
          <dd className="font-mono text-ink">{demoCredentials.password}</dd>
        </div>
      </dl>

      <Button
        type="button"
        variant="secondary"
        size="sm"
        fullWidth
        onClick={onFill}
        disabled={disabled}
        className="mt-3"
      >
        Fill demo credentials
      </Button>
    </div>
  )
}
