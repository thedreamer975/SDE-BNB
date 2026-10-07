'use client';

import React from 'react';
import useSWR from 'swr';
import { host } from '@/lib/api';
import { formatMoney, formatRating } from '@/lib/format';

export default function HostDashboardPage() {
  const { data, error } = useSWR('host.dashboard', host.dashboard, {
    revalidateOnFocus: true,
  });

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="bg-error/10 text-error p-4 rounded-card">
          Failed to load dashboard metrics.
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-12 animate-pulse grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-32 bg-surface rounded-card" />
        ))}
      </div>
    );
  }

  const metrics = [
    { label: '30-Day Revenue', value: formatMoney(data.revenue_30d) },
    { label: 'Upcoming Bookings', value: data.upcoming_bookings },
    { label: 'Currently Hosting', value: data.currently_hosting },
    { label: 'Checking Out Soon', value: data.checking_out },
    { label: 'Average Rating', value: data.avg_rating > 0 ? formatRating(data.avg_rating, 1) : 'No ratings' },
    { label: 'Total Listings', value: data.total_listings },
  ];

  return (
    <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-20 py-12">
      <h1 className="text-3xl font-bold text-text mb-8">Welcome back, Host!</h1>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {metrics.map((m, i) => (
          <div key={i} className="bg-bg border border-border p-6 rounded-card shadow-sm flex flex-col justify-center">
            <p className="text-sm text-text-muted mb-2 font-semibold uppercase tracking-wider">{m.label}</p>
            <p className="text-3xl font-bold text-text">{m.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
