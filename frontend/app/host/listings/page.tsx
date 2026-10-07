'use client';

import React from 'react';
import useSWR from 'swr';
import { Trash2, Edit2, Plus } from 'lucide-react';
import { host, HostListing } from '@/lib/api';
import { formatMoney, formatRating } from '@/lib/format';
import { Button } from '@/components/ui/Button';
import { useToast } from '@/lib/toast-context';

export default function HostListingsPage() {
  const { data, error, mutate } = useSWR('host.listings', host.listings);
  const { addToast } = useToast();
  const [deletingId, setDeletingId] = React.useState<string | null>(null);

  async function handleDelete(id: string) {
    if (!confirm('Are you sure you want to delete this listing? This cannot be undone.')) return;
    setDeletingId(id);
    try {
      await host.deleteListing(id);
      addToast({ message: 'Listing deleted successfully' });
      mutate();
    } catch (err) {
      addToast({ message: 'Failed to delete listing', type: 'error' });
    } finally {
      setDeletingId(null);
    }
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-12 text-error">
        Failed to load listings.
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-20 py-12">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-text">Your Listings</h1>
        <Button variant="brand" href="/host/create" className="flex items-center gap-2">
          <Plus size={16} /> Create new
        </Button>
      </div>

      {!data ? (
        <div className="animate-pulse flex flex-col gap-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-24 bg-surface rounded-card" />
          ))}
        </div>
      ) : data.length === 0 ? (
        <div className="bg-bg border border-border p-12 rounded-card text-center flex flex-col items-center">
          <h3 className="text-xl font-semibold mb-2">No listings yet</h3>
          <p className="text-text-muted mb-6">Create your first listing to start hosting guests.</p>
          <Button variant="primary" href="/host/create">Get Started</Button>
        </div>
      ) : (
        <div className="bg-bg border border-border rounded-card overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-surface/50 border-b border-border">
                <th className="p-4 font-semibold text-text text-sm">Listing</th>
                <th className="p-4 font-semibold text-text text-sm">Status</th>
                <th className="p-4 font-semibold text-text text-sm">Price</th>
                <th className="p-4 font-semibold text-text text-sm">Rating</th>
                <th className="p-4 font-semibold text-text text-sm">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.map((listing: HostListing) => (
                <tr key={listing.id} className="hover:bg-surface/30 transition-colors">
                  <td className="p-4">
                    <div className="flex items-center gap-4">
                      <div className="w-16 h-12 bg-surface rounded overflow-hidden shrink-0">
                        {listing.photos?.[0] && (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img src={listing.photos[0]} alt={listing.title} className="w-full h-full object-cover" />
                        )}
                      </div>
                      <div>
                        <a href={`/rooms/${listing.id}`} className="font-semibold text-text hover:underline line-clamp-1">
                          {listing.title}
                        </a>
                        <p className="text-xs text-text-muted">{listing.city}, {listing.country}</p>
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="inline-flex items-center px-2 py-1 rounded-full bg-green-100 text-green-800 text-xs font-semibold">
                      Active
                    </span>
                  </td>
                  <td className="p-4 text-text">{formatMoney(listing.price_per_night)}</td>
                  <td className="p-4 text-text">
                    {listing.rating_count > 0 ? (
                      <span className="flex items-center gap-1">★ {formatRating(listing.rating_avg, listing.rating_count)}</span>
                    ) : (
                      <span className="text-text-muted text-sm">No ratings</span>
                    )}
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <Button variant="secondary" size="sm" className="px-2" title="Edit">
                        <Edit2 size={16} className="text-text-muted" />
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        className="px-2 hover:bg-error/10 hover:border-error hover:text-error"
                        title="Delete"
                        onClick={() => handleDelete(listing.id)}
                        loading={deletingId === listing.id}
                      >
                        <Trash2 size={16} className="text-error" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
