import * as z from 'zod'

export type FormResult<T> =
  | { success: true; data: T }
  | { success: false; fieldErrors: Record<string, string> }

export function validateForm<S extends z.ZodType<Record<string, unknown>>>(
  schema: S,
  input: unknown,
): FormResult<z.infer<S>> {
  const result = schema.safeParse(input)

  if (result.success) {
    return { success: true, data: result.data }
  }

  return { success: false, fieldErrors: toFieldErrors(result.error) }
}

function toFieldErrors(error: z.ZodError<Record<string, unknown>>): Record<string, string> {
  const { fieldErrors } = z.flattenError(error)
  const firstPerField: Record<string, string> = {}

  for (const [field, messages] of Object.entries(fieldErrors)) {
    const [first] = messages ?? []

    if (first !== undefined) {
      firstPerField[field] = first
    }
  }

  return firstPerField
}
