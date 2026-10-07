import React from 'react';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 px-6 sm:px-10 lg:px-20 py-8">
        {/* S5: CategoryBar + Explore grid will be inserted here */}
        <div className="flex items-center justify-center min-h-[40vh]">
          <p className="text-text-muted text-lg">Listings loading soon…</p>
        </div>
      </main>
      <Footer />
    </div>
  );
}
