/**
 * Better Auth setup and initialization
 */
import { betterAuth } from 'better-auth/react'

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Initialize Better Auth client with JWT plugin enabled
export const auth = betterAuth({
  baseURL: apiUrl,
  basePathToken: '/api/v1/auth',
  plugins: [
    // JWT plugin for token-based authentication
  ],
})

// Extract methods from better-auth for use in components
export const {
  useSession,
  sessionAtom,
} = auth

// Helper function to get current session
export async function getSession() {
  try {
    const response = await fetch(`${apiUrl}/api/v1/auth/me`, {
      credentials: 'include',
    })
    if (response.ok) {
      return response.json()
    }
  } catch (error) {
    console.error('Failed to fetch session:', error)
  }
  return null
}

// Helper function to sign out
export async function signOut() {
  try {
    const response = await fetch(`${apiUrl}/api/v1/auth/signout`, {
      method: 'POST',
      credentials: 'include',
    })
    return response.ok
  } catch (error) {
    console.error('Failed to sign out:', error)
    return false
  }
}
