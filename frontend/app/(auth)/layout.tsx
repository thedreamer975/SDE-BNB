import React from 'react';
import Link from 'next/link';

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-bg flex flex-col">
      {/* Simple header */}
      <header className="border-b border-border px-6 h-16 flex items-center">
        <Link href="/" className="text-brand font-bold text-xl tracking-tight">
          scalar
        </Link>
      </header>
      <main className="flex-1 flex items-center justify-center p-6">{children}</main>
    </div>
  );
}
