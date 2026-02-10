// Root Layout with AuthProvider

import type { Metadata } from 'next';
import { AuthProvider } from '@/hooks/useAuth';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'Todo App - Task Management',
  description: 'Secure task management application with authentication',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
