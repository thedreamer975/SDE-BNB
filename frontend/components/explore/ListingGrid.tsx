'use client';

import React from 'react';
import useSWRInfinite from 'swr/infinite';
import { listings, SearchParams, PaginatedListings } from '@/lib/api';
import { ListingCard } from './ListingCard';
import { ListingGridSkeleton } from './ListingCardSkeleton';
import { Button } from '@/components/ui/Button';

interface ListingGridProps {
  searchParams: SearchParams;
}

export function ListingGrid({ searchParams }: ListingGridProps) {
  const getKey = (pageIndex: number, previousPageData: PaginatedListings | null) => {
    // Reached the end
    if (previousPageData && !previousPageData.items.length) return null;

    // Add the page to the key
    return ['listings.search', { ...searchParams, page: pageIndex + 1, page_size: 20 }];
  };

  const { data, error, size, setSize, isValidating } = useSWRInfinite<PaginatedListings>(
    getKey,
    ([, params]) => listings.search(params as SearchParams),
    { revalidateOnFocus: false }
  );

  const isLoadingInitialData = !data && !error;
  const isLoadingMore = isLoadingInitialData || (size > 0 && data && typeof data[size - 1] === 'undefined');
  const isEmpty = data?.[0]?.items.length === 0;
  const isReachingEnd = isEmpty || (data && data[data.length - 1]?.items.length < 20);

  const allItems = data ? data.flatMap((page) => page.items) : [];

  // Extract dates for display in ListingCard
  const searchDates =
    searchParams.check_in && searchParams.check_out
      ? {
          checkIn: searchParams.check_in,
          checkOut: searchParams.check_out,
          nights: Math.round(
            (new Date(searchParams.check_out).getTime() - new Date(searchParams.check_in).getTime()) /
              86_400_000
          ),
        }
      : null;

  if (isLoadingInitialData) {
    return <ListingGridSkeleton count={12} />;
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-20 text-center">
        <h3 className="text-xl font-semibold">Something went wrong</h3>
        <p className="text-text-muted">We couldn&apos;t load the listings right now.</p>
        <Button onClick={() => setSize(1)} variant="secondary">
          Try again
        </Button>
      </div>
    );
  }

  if (isEmpty) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-20 text-center">
        <h3 className="text-xl font-semibold">No exact matches</h3>
        <p className="text-text-muted">Try changing or removing some of your filters.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-10">
      <div className="grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-x-6 gap-y-10">
        {allItems.map((listing) => (
          <ListingCard
            key={listing.id}
            listing={listing}
            searchDates={searchDates}
          />
        ))}
      </div>

      {!isReachingEnd && (
        <div className="flex justify-center mt-4">
          <Button
            variant="primary"
            onClick={() => setSize(size + 1)}
            loading={isValidating || isLoadingMore}
          >
            Show more
          </Button>
        </div>
      )}
    </div>
  );
}
