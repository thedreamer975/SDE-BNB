'use client';

import React from 'react';
import useSWR from 'swr';
import Link from 'next/link';
import Image from 'next/image';
import { bookings, Booking } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { ListingGridSkeleton } from '@/components/explore/ListingCardSkeleton';
import { formatMoney } from '@/lib/format';

function statusBadge(booking: Booking) {
  const statusMap: Record<string, { label: string; cls: string }> = {
    confirmed: { label: 'Confirmed', cls: 'bg-emerald-100 text-emerald-800' },
    cancelled: { label: 'Cancelled', cls: 'bg-red-100 text-red-800' },
    completed: { label: 'Completed', cls: 'bg-gray-100 text-gray-700' },
  };
  const s = statusMap[booking.status] ?? { label: booking.status, cls: 'bg-gray-100 text-gray-700' };
  return (
    <span className={`inline-block px-2 py-0.5 text-xs font-medium rounded-full ${s.cls}`}>
      {s.label}
    </span>
  );
}

function TripCard({ booking }: { booking: Booking }) {
  const photo = booking.listing_photo;
  return (
    <Link
      href={`/rooms/${booking.listing_id}`}
      className="group block rounded-card overflow-hidden border border-border hover:shadow-md transition-shadow"
    >
      <div className="aspect-[16/10] relative bg-bg-muted">
        {photo ? (
          <Image
            src={photo}
            alt={booking.listing_title}
            className="w-full h-full object-cover"
            fill
            sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, 25vw"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-text-muted text-sm">
            No photo
          </div>
        )}
        <div className="absolute top-2 right-2">{statusBadge(booking)}</div>
      </div>
      <div className="p-4 space-y-1">
        <h3 className="font-semibold text-text truncate">{booking.listing_title}</h3>
        <p className="text-sm text-text-muted">
          {booking.listing_city}, {booking.listing_country}
        </p>
        <p className="text-sm text-text-muted">
          {booking.check_in} → {booking.check_out}
        </p>
        <p className="text-sm font-medium text-text">{formatMoney(booking.total_price)}</p>
        <p className="text-xs text-text-muted">Code: {booking.confirmation_code}</p>
      </div>
    </Link>
  );
}

type Tab = 'all' | 'upcoming' | 'past';

export default function TripsPage() {
  const [tab, setTab] = React.useState<Tab>('all');
  const { data, error } = useSWR(['trips', tab], () => bookings.getAll());

  const filtered = React.useMemo(() => {
    if (!data) return [];
    if (tab === 'upcoming') return data.filter((b) => b.status === 'confirmed');
    if (tab === 'past') return data.filter((b) => b.status !== 'confirmed');
    return data;
  }, [data, tab]);

  const tabs: { key: Tab; label: string }[] = [
    { key: 'all', label: 'All' },
    { key: 'upcoming', label: 'Upcoming' },
    { key: 'past', label: 'Past' },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-bg">
      <Header />
      <main className="flex-1 max-w-7xl mx-auto w-full px-6 sm:px-10 lg:px-20 py-12">
        <h1 className="text-3xl font-bold text-text mb-6">Trips</h1>

        {/* Tabs */}
        <div className="flex gap-2 mb-8 border-b border-border pb-2">
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`px-4 py-2 text-sm font-medium rounded-full transition-colors ${
                tab === t.key
                  ? 'bg-text text-bg'
                  : 'text-text-muted hover:bg-bg-muted'
              }`}
            >
              {t.label}
              {data && (
                <span className="ml-1 text-xs">
                  ({tab === t.key ? filtered.length : ''})
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Content */}
        {error ? (
          <div className="text-error bg-error/10 p-4 rounded-card">
            Failed to load your trips. Please try again.
          </div>
        ) : !data ? (
          <ListingGridSkeleton count={4} />
        ) : filtered.length === 0 ? (
          <div className="py-20 text-center">
            <h2 className="text-xl font-semibold mb-2">No trips yet</h2>
            <p className="text-text-muted mb-6">
              When you book a place, your trips will show up here.
            </p>
            <Link
              href="/"
              className="inline-flex px-6 py-3 bg-brand text-white rounded-card font-medium hover:opacity-90 transition-opacity"
            >
              Start exploring
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-x-6 gap-y-10">
            {filtered.map((booking) => (
              <TripCard key={booking.id} booking={booking} />
            ))}
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
