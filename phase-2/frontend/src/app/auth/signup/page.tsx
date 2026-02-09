/**
 * Signup Page
 */
import AuthForm from '@/components/AuthForm'

export const metadata = {
  title: 'Sign Up | Todo App',
  description: 'Create a new account',
}

export default function SignupPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <AuthForm mode="signup" />
    </div>
  )
}
