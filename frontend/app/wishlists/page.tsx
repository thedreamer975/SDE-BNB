'use client';

import React from 'react';
import useSWR from 'swr';
import { wishlist, ListingCard as ListingCardType } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { ListingCard } from '@/components/explore/ListingCard';
import { ListingGridSkeleton } from '@/components/explore/ListingCardSkeleton';

export default function WishlistsPage() {
  const { data, error } = useSWR('wishlist.getAll', wishlist.getAll, {
    revalidateOnFocus: true,
  });

  return (
    <div className="min-h-screen flex flex-col bg-bg">
      <Header />
      <main className="flex-1 max-w-7xl mx-auto w-full px-6 sm:px-10 lg:px-20 py-12">
        <h1 className="text-3xl font-bold text-text mb-8">Wishlists</h1>

        {error ? (
          <div className="text-error bg-error/10 p-4 rounded-card">
            Failed to load your wishlists. Please try again.
          </div>
        ) : !data ? (
          <ListingGridSkeleton count={4} />
        ) : data.length === 0 ? (
          <div className="py-20 text-center">
            <h2 className="text-xl font-semibold mb-2">Create your first wishlist</h2>
            <p className="text-text-muted mb-6">As you search, click the heart icon to save your favorite places.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-x-6 gap-y-10">
            {data.map((listing: ListingCardType) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
