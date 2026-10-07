import React from 'react';

export function ListingCardSkeleton() {
  return (
    <div className="flex flex-col gap-3 animate-pulse" aria-hidden="true">
      {/* Image */}
      <div
        className="w-full rounded-card bg-surface"
        style={{ aspectRatio: '20 / 19' }}
      />
      {/* Text rows */}
      <div className="flex flex-col gap-2">
        <div className="flex justify-between gap-4">
          <div className="h-4 bg-surface rounded w-2/3" />
          <div className="h-4 bg-surface rounded w-12" />
        </div>
        <div className="h-3.5 bg-surface rounded w-1/2" />
        <div className="h-3.5 bg-surface rounded w-1/3" />
        <div className="h-4 bg-surface rounded w-1/4 mt-1" />
      </div>
    </div>
  );
}

export function ListingGridSkeleton({ count = 12 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-x-6 gap-y-10">
      {Array.from({ length: count }).map((_, i) => (
        <ListingCardSkeleton key={i} />
      ))}
    </div>
  );
}
