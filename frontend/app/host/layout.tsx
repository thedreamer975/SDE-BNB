'use client';

import React from 'react';
import { useAuth } from '@/lib/auth-context';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { Button } from '@/components/ui/Button';
import { users } from '@/lib/api';

export default function HostLayout({ children }: { children: React.ReactNode }) {
  const { user, setUser } = useAuth();
  const [loading, setLoading] = React.useState(false);

  if (!user) {
    return (
      <div className="min-h-screen flex flex-col bg-bg">
        <Header />
        <main className="flex-1 flex items-center justify-center p-6">
          <p className="text-xl">Please log in to access the host dashboard.</p>
        </main>
        <Footer />
      </div>
    );
  }

  async function handleBecomeHost() {
    setLoading(true);
    try {
      const updatedUser = await users.becomeHost();
      setUser(updatedUser);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  if (user.role !== 'host') {
    return (
      <div className="min-h-screen flex flex-col bg-bg">
        <Header />
        <main className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-lg mx-auto">
          <h1 className="text-3xl font-bold mb-4">Ready to earn?</h1>
          <p className="text-text-muted mb-8">
            Join thousands of hosts opening their doors to guests from all over the world.
          </p>
          <Button variant="brand" size="lg" loading={loading} onClick={handleBecomeHost}>
            Become a Host
          </Button>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-bg">
      <Header />
      <div className="border-b border-border bg-surface/50">
        <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-20 py-4 flex gap-6 overflow-x-auto whitespace-nowrap hide-scrollbar">
          <a href="/host/dashboard" className="font-semibold text-sm hover:text-brand transition-colors">Dashboard</a>
          <a href="/host/listings" className="font-semibold text-sm hover:text-brand transition-colors">Listings</a>
          <a href="/host/create" className="font-semibold text-sm hover:text-brand transition-colors">Create new listing</a>
        </div>
      </div>
      <main className="flex-1 bg-surface/30">
        {children}
      </main>
      <Footer />
    </div>
  );
}
