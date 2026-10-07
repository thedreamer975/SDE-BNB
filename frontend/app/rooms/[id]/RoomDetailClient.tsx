'use client';

import React, { useState } from 'react';
import useSWR from 'swr';
import { Share, Heart, Medal, User } from 'lucide-react';
import { clsx } from 'clsx';
import { listings, wishlist as wishlistApi } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { useToast } from '@/lib/toast-context';
import { PhotoGrid } from '@/components/room/PhotoGrid';
import { BookingWidget } from '@/components/room/BookingWidget';
import { ReviewSection } from '@/components/room/ReviewSection';
import { Modal } from '@/components/ui/Modal';
import { formatRating } from '@/lib/format';

export function RoomDetailClient({ listingId }: { listingId: string }) {
  const { user } = useAuth();
  const { addToast } = useToast();
  
  const { data: listing, error } = useSWR(
    ['listings.get', listingId],
    () => listings.get(listingId),
    { revalidateOnFocus: false }
  );

  const [saved, setSaved] = useState<boolean | null>(null);
  const [savePending, setSavePending] = useState(false);
  const [showAmenities, setShowAmenities] = useState(false);

  // Sync initial saved state
  if (listing && saved === null) {
    setSaved(listing.is_saved);
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-20 py-20 text-center">
        <h1 className="text-2xl font-bold mb-4">Room not found</h1>
        <p className="text-text-muted">The listing you are looking for may have been removed.</p>
      </div>
    );
  }

  if (!listing) {
    return (
      <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-20 py-8 animate-pulse">
        <div className="h-8 bg-surface w-1/3 rounded mb-4" />
        <div className="w-full h-[60vh] bg-surface rounded-[16px]" />
      </div>
    );
  }

  const isSaved = saved ?? false;

  async function handleHeart() {
    if (!user) {
      window.location.href = `/login?next=/rooms/${listingId}`;
      return;
    }
    if (savePending) return;
    setSavePending(true);
    const newSaved = !isSaved;
    setSaved(newSaved);
    try {
      if (newSaved) {
        await wishlistApi.save(listingId);
      } else {
        await wishlistApi.remove(listingId);
        addToast({ message: 'Removed from wishlist' });
      }
    } catch {
      setSaved(!newSaved);
      addToast({ message: 'Could not update wishlist', type: 'error' });
    } finally {
      setSavePending(false);
    }
  }

  function handleShare() {
    navigator.clipboard.writeText(window.location.href);
    addToast({ message: 'Link copied to clipboard' });
  }

  return (
    <div className="max-w-[1120px] mx-auto px-6 sm:px-10 py-6">
      {/* Title & Actions */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-6">
        <div>
          <h1 className="text-[26px] sm:text-[32px] font-semibold text-text mb-1">{listing.title}</h1>
        </div>
        <div className="flex items-center gap-4 shrink-0">
          <button onClick={handleShare} className="flex items-center gap-2 text-sm font-semibold underline hover:bg-surface px-3 py-2 rounded-[8px] transition-colors">
            <Share size={16} /> Share
          </button>
          <button onClick={handleHeart} className="flex items-center gap-2 text-sm font-semibold underline hover:bg-surface px-3 py-2 rounded-[8px] transition-colors">
            <Heart size={16} className={clsx(isSaved && 'fill-brand text-brand border-brand')} />
            {isSaved ? 'Saved' : 'Save'}
          </button>
        </div>
      </div>

      <PhotoGrid photos={listing.photos} title={listing.title} />

      <div className="flex flex-col lg:flex-row gap-12 mt-12">
        {/* Left column (Info) */}
        <div className="flex-1 min-w-0">
          {/* Subtitle */}
          <div className="mb-6 pb-6 border-b border-border">
            <h2 className="text-[22px] font-semibold text-text mb-1">
              {listing.room_type} in {listing.city}, {listing.country}
            </h2>
            <p className="text-text-muted">
              {listing.max_guests} guests · {listing.bedrooms} bedroom{listing.bedrooms !== 1 ? 's' : ''} · {listing.beds} bed{listing.beds !== 1 ? 's' : ''} · {listing.baths} bath{listing.baths !== 1 ? 's' : ''}
            </p>
            {formatRating(listing.rating_avg, listing.rating_count) !== 'New' && (
              <p className="font-semibold mt-2">
                ★ {formatRating(listing.rating_avg, listing.rating_count)}
              </p>
            )}
          </div>

          {/* Host snippet */}
          <div className="flex items-center gap-4 mb-8 pb-8 border-b border-border">
            <div className="relative w-14 h-14 rounded-full bg-surface overflow-hidden flex items-center justify-center shrink-0">
              {listing.host.avatar_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={listing.host.avatar_url} alt={listing.host.name} className="w-full h-full object-cover" />
              ) : (
                <User size={32} className="text-text-muted" />
              )}
              {listing.host.is_superhost && (
                <div className="absolute bottom-0 right-0 bg-brand text-white rounded-full p-0.5">
                  <Medal size={12} />
                </div>
              )}
            </div>
            <div>
              <h3 className="text-base font-semibold text-text">Hosted by {listing.host.name.split(' ')[0]}</h3>
              <p className="text-sm text-text-muted">
                {listing.host.is_superhost ? 'Superhost · ' : ''}Joined {new Date(listing.host.created_at).getFullYear()}
              </p>
            </div>
          </div>

          {/* Description */}
          <div className="mb-10 pb-10 border-b border-border">
            <p className="text-text leading-relaxed whitespace-pre-wrap">
              {listing.description}
            </p>
          </div>

          {/* Amenities snippet */}
          <div className="mb-10 pb-10 border-b border-border">
            <h2 className="text-[22px] font-semibold text-text mb-6">What this place offers</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-y-4 gap-x-2 mb-8">
              {listing.amenities.slice(0, 10).map((a) => (
                <div key={a.id} className="flex items-center gap-4 text-text">
                  {/* Since we don't have SVGs for every amenity icon_key, we use a generic check or emoji if possible */}
                  <span className="w-6 text-center text-text-muted">✓</span>
                  <span>{a.name}</span>
                </div>
              ))}
            </div>
            {listing.amenities.length > 10 && (
              <button
                onClick={() => setShowAmenities(true)}
                className="px-6 py-3 border border-text rounded-btn font-semibold text-text hover:bg-surface transition-colors"
              >
                Show all {listing.amenities.length} amenities
              </button>
            )}
          </div>
        </div>

        {/* Right column (Widget) */}
        <div className="w-full lg:w-[33.333%] lg:pl-[8%] shrink-0">
          <BookingWidget listingId={listing.id} pricePerNight={listing.price_per_night} />
        </div>
      </div>

      <ReviewSection listingId={listingId} />

      <Modal isOpen={showAmenities} onClose={() => setShowAmenities(false)} title="What this place offers">
        <div className="flex flex-col gap-8 max-w-2xl mx-auto py-4">
          <h2 className="text-2xl font-semibold mb-2">Amenities</h2>
          <div className="flex flex-col gap-4">
            {listing.amenities.map((a) => (
              <div key={a.id} className="flex items-center gap-4 text-text border-b border-border pb-4">
                <span className="w-6 text-center text-text-muted">✓</span>
                <span>{a.name}</span>
              </div>
            ))}
          </div>
        </div>
      </Modal>
    </div>
  );
}
