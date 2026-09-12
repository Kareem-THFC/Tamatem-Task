import * as z from 'zod'

// Mirrors the backend's own limits.
const MIN_USERNAME_LENGTH = 3
const MAX_USERNAME_LENGTH = 80
const MAX_EMAIL_LENGTH = 255

export const MIN_PASSWORD_LENGTH = 8
const MAX_PASSWORD_LENGTH = 128

const password = z
  .string()
  .min(MIN_PASSWORD_LENGTH, {
    error: `At least ${MIN_PASSWORD_LENGTH} characters.`,
  })
  .max(MAX_PASSWORD_LENGTH, {
    error: `At most ${MAX_PASSWORD_LENGTH} characters.`,
  })

export const loginSchema = z.object({
  identifier: z
    .string()
    .trim()
    .min(1, { error: 'Enter your username or email.' })
    .max(255, { error: 'That is too long to be a username or email.' }),

  password: z.string().min(1, { error: 'Enter your password.' }),
})

export const registerSchema = z.object({
  username: z
    .string()
    .trim()
    .min(MIN_USERNAME_LENGTH, {
      error: `At least ${MIN_USERNAME_LENGTH} characters.`,
    })
    .max(MAX_USERNAME_LENGTH, {
      error: `At most ${MAX_USERNAME_LENGTH} characters.`,
    })
    .regex(/^[A-Za-z0-9._-]+$/, {
      error: 'Letters, digits, dots, dashes and underscores only.',
    }),

  email: z
    .string()
    .trim()
    .toLowerCase()
    .pipe(
      z
        .email({ error: 'Enter a valid email address.' })
        .max(MAX_EMAIL_LENGTH, { error: 'That email address is too long.' }),
    ),

  password,
})

export type LoginInput = z.infer<typeof loginSchema>
export type RegisterInput = z.infer<typeof registerSchema>
