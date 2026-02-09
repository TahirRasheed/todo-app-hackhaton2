/**
 * Signin Page
 */
import AuthForm from '@/components/AuthForm'

export const metadata = {
  title: 'Sign In | Todo App',
  description: 'Sign in to your account',
}

export default function SigninPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <AuthForm mode="signin" />
    </div>
  )
}
