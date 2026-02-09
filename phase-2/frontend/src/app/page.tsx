import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Todo App - Phase II</h1>
        <p className="text-xl text-gray-600 mb-8">Full-Stack Web Application</p>
        <div className="space-x-4">
          <Link
            href="/auth/signin"
            className="inline-block px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            Sign In
          </Link>
          <Link
            href="/auth/signup"
            className="inline-block px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600"
          >
            Sign Up
          </Link>
        </div>
      </div>
    </main>
  );
}
