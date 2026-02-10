// T028: Signin Page

import { SigninForm } from '@/components/auth/SigninForm'

export const metadata = {
  title: 'Sign In | Todo App',
  description: 'Sign in to your account',
}

export default function SigninPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4">
      <SigninForm />
    </div>
  )
}
