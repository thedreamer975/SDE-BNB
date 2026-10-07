import React, { Suspense } from 'react';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { ExploreContainer } from '@/components/explore/ExploreContainer';
import { ListingGridSkeleton } from '@/components/explore/ListingCardSkeleton';

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <Suspense fallback={<div className="flex-1 px-6 sm:px-10 lg:px-20 py-8"><ListingGridSkeleton count={12} /></div>}>
        <ExploreContainer />
      </Suspense>
      <Footer />
    </div>
  );
}
