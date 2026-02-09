'use client'

/**
 * AuthForm Component - Signup and Signin forms
 */
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { apiClient } from '@/lib/api-client'
import { User } from '@/types/api'

type AuthFormMode = 'signup' | 'signin'

interface AuthFormProps {
  mode: AuthFormMode
}

interface PasswordStrength {
  isValid: boolean
  errors: string[]
}

function validatePasswordStrength(password: string): PasswordStrength {
  const errors: string[] = []

  if (password.length < 8) {
    errors.push('At least 8 characters')
  }
  if (!/[A-Z]/.test(password)) {
    errors.push('One uppercase letter')
  }
  if (!/[a-z]/.test(password)) {
    errors.push('One lowercase letter')
  }
  if (!/\d/.test(password)) {
    errors.push('One digit')
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

export default function AuthForm({ mode }: AuthFormProps) {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)

  const isSignup = mode === 'signup'
  const passwordStrength = isSignup ? validatePasswordStrength(password) : { isValid: true, errors: [] }
  const isPasswordWeak = password.length > 0 && !passwordStrength.isValid

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const { signupUser, signinUser } = await import('@/lib/api')

      if (isSignup) {
        const userData = await signupUser(email, password, name)

        // Store token in localStorage (in production, consider httpOnly cookie via Next.js middleware)
        localStorage.setItem('token', userData.token)
        localStorage.setItem('user', JSON.stringify({
          id: userData.id,
          email: userData.email,
          name: userData.name
        }))
      } else {
        const userData = await signinUser(email, password)

        // Store token in localStorage
        localStorage.setItem('token', userData.token)
        localStorage.setItem('user', JSON.stringify({
          id: userData.id,
          email: userData.email,
          name: userData.name
        }))
      }

      // Redirect to dashboard on success
      router.push('/dashboard')
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || `${isSignup ? 'Signup' : 'Signin'} failed`
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h1 className="text-2xl font-bold mb-6 text-center">
        {isSignup ? 'Create Account' : 'Sign In'}
      </h1>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Email input */}
      <div className="mb-4">
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
          Email Address
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          placeholder="your@example.com"
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Password input */}
      <div className="mb-4">
        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
          Password
        </label>
        <div className="relative">
          <input
            id="password"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="••••••••"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-3 text-gray-500 text-sm"
          >
            {showPassword ? 'Hide' : 'Show'}
          </button>
        </div>
        {isSignup && password.length > 0 && (
          <div className="mt-2 space-y-1">
            {passwordStrength.isValid ? (
              <p className="text-xs text-green-600 font-medium">
                ✓ Password meets all requirements
              </p>
            ) : (
              <>
                <p className="text-xs text-gray-700 font-medium">Password requirements:</p>
                <ul className="text-xs space-y-0.5 pl-4">
                  {passwordStrength.errors.map((error, index) => (
                    <li key={index} className="text-red-600">
                      ✗ {error}
                    </li>
                  ))}
                  {password.length >= 8 && (
                    <li className="text-green-600">✓ At least 8 characters</li>
                  )}
                  {/[A-Z]/.test(password) && (
                    <li className="text-green-600">✓ One uppercase letter</li>
                  )}
                  {/[a-z]/.test(password) && (
                    <li className="text-green-600">✓ One lowercase letter</li>
                  )}
                  {/\d/.test(password) && (
                    <li className="text-green-600">✓ One digit</li>
                  )}
                </ul>
              </>
            )}
          </div>
        )}
      </div>

      {/* Name input (signup only) */}
      {isSignup && (
        <div className="mb-4">
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Full Name
          </label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="John Doe"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      )}

      {/* Submit button */}
      <button
        type="submit"
        disabled={loading || (isSignup && isPasswordWeak)}
        className="w-full py-2 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        {loading ? 'Loading...' : (isSignup ? 'Create Account' : 'Sign In')}
      </button>

      {/* Toggle signup/signin link */}
      <p className="text-center text-sm text-gray-600 mt-4">
        {isSignup ? 'Already have an account? ' : "Don't have an account? "}
        <Link
          href={isSignup ? '/auth/signin' : '/auth/signup'}
          className="text-blue-600 hover:text-blue-800 font-semibold"
        >
          {isSignup ? 'Sign In' : 'Sign Up'}
        </Link>
      </p>
    </form>
  )
}
