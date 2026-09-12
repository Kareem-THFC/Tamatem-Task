import { request } from '@/api/client'
import type { LoginInput, RegisterInput } from '@/schemas/auth'
import type { ApiResponse, AuthPayload } from '@/types/api'

export async function login(input: LoginInput): Promise<AuthPayload> {
  const response = await request<ApiResponse<AuthPayload>>('/api/auth/login', {
    method: 'POST',
    body: input,
  })

  return response.data
}

export async function register(input: RegisterInput): Promise<AuthPayload> {
  const response = await request<ApiResponse<AuthPayload>>('/api/auth/register', {
    method: 'POST',
    body: input,
  })

  return response.data
}

export type { LoginInput, RegisterInput }
