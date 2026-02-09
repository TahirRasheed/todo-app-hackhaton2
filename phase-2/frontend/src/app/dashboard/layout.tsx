'use client'

/**
 * Dashboard Layout - Protected authenticated layout
 */
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { User } from '@/types/api'
import { getToken, clearToken } from '@/lib/api-client'
import SignoutButton from '@/components/SignoutButton'

interface DashboardLayoutProps {
  children: React.ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is authenticated
    const token = getToken()
    if (!token) {
      // Redirect to signin if no token
      router.push('/auth/signin')
      return
    }

    // TODO: Fetch current user from /auth/me endpoint
    // For now, we'll assume user is authenticated
    setLoading(false)
  }, [router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-lg text-gray-600">Loading...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Todo App</h1>
            {user && <p className="text-sm text-gray-600">Welcome, {user.email}</p>}
          </div>
          <SignoutButton />
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}
