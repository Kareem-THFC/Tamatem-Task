const gemFormatter = new Intl.NumberFormat('en-US', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
})

export function formatGems(amount: string): string {
  const value = Number(amount)

  return Number.isFinite(value) ? gemFormatter.format(value) : amount
}

const dateFormatter = new Intl.DateTimeFormat('en-GB', {
  dateStyle: 'medium',
  timeStyle: 'short',
})

export function formatDateTime(isoDate: string | null): string {
  if (!isoDate) {
    return '—'
  }

  const date = new Date(isoDate)

  return Number.isNaN(date.getTime()) ? '—' : dateFormatter.format(date)
}

const LOCATION_NAMES: Record<string, string> = {
  JO: 'Jordan',
  SA: 'Saudi Arabia',
}

export function formatLocation(code: string): string {
  return LOCATION_NAMES[code] ?? code
}
