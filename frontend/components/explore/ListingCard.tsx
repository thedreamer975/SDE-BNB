'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Heart, ChevronLeft, ChevronRight, Star } from 'lucide-react';
import { clsx } from 'clsx';
import type { ListingCard as ListingCardType } from '@/lib/api';
import { wishlist as wishlistApi } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { useToast } from '@/lib/toast-context';
import { formatMoney, formatRating } from '@/lib/format';

interface ListingCardProps {
  listing: ListingCardType;
  searchDates?: { checkIn: string; checkOut: string; nights: number } | null;
  onWishlistChange?: (id: string, saved: boolean) => void;
}

function PhotoCarousel({ photos, title }: { photos: string[]; title: string }) {
  const [idx, setIdx] = useState(0);
  const total = Math.min(photos.length, 5);
  if (total === 0) return <div className="w-full h-full bg-surface rounded-card" />;

  function prev(e: React.MouseEvent) {
    e.preventDefault();
    setIdx((i) => (i === 0 ? total - 1 : i - 1));
  }

  function next(e: React.MouseEvent) {
    e.preventDefault();
    setIdx((i) => (i === total - 1 ? 0 : i + 1));
  }

  return (
    <div
      className="relative w-full group overflow-hidden rounded-card"
      style={{ aspectRatio: '20/19' }}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={photos[idx]}
        alt={`${title} — photo ${idx + 1} of ${total}`}
        className="absolute inset-0 w-full h-full object-cover transition-opacity duration-300"
        loading="lazy"
      />

      {/* Prev/Next arrows — appear on hover */}
      {total > 1 && (
        <>
          <button
            onClick={prev}
            aria-label="Previous photo"
            className={clsx(
              'absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-white/90 flex items-center justify-center shadow transition-opacity duration-150',
              'opacity-0 group-hover:opacity-100',
              idx === 0 && 'pointer-events-none opacity-0',
            )}
          >
            <ChevronLeft size={16} className="text-text" />
          </button>
          <button
            onClick={next}
            aria-label="Next photo"
            className={clsx(
              'absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-white/90 flex items-center justify-center shadow transition-opacity duration-150',
              'opacity-0 group-hover:opacity-100',
              idx === total - 1 && 'pointer-events-none opacity-0',
            )}
          >
            <ChevronRight size={16} className="text-text" />
          </button>

          {/* Dot indicators */}
          <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1">
            {Array.from({ length: total }).map((_, i) => (
              <span
                key={i}
                className={clsx(
                  'w-[6px] h-[6px] rounded-full transition-all duration-150',
                  i === idx ? 'bg-white scale-125' : 'bg-white/60',
                )}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export function ListingCard({ listing, searchDates, onWishlistChange }: ListingCardProps) {
  const { user } = useAuth();
  const { addToast } = useToast();
  const [saved, setSaved] = useState(listing.is_saved);
  const [savePending, setSavePending] = useState(false);

  async function handleHeart(e: React.MouseEvent) {
    e.preventDefault();
    if (!user) {
      // Prompt to log in
      window.location.href = `/login?next=/`;
      return;
    }
    if (savePending) return;
    setSavePending(true);
    const newSaved = !saved;
    setSaved(newSaved); // optimistic
    try {
      if (newSaved) {
        await wishlistApi.save(listing.id);
      } else {
        await wishlistApi.remove(listing.id);
        addToast({
          message: 'Removed from wishlist',
        });
      }
      onWishlistChange?.(listing.id, newSaved);
    } catch {
      setSaved(!newSaved); // rollback
      addToast({ message: 'Could not update wishlist. Try again.', type: 'error' });
    } finally {
      setSavePending(false);
    }
  }

  const ratingText = formatRating(listing.rating_avg, listing.rating_count);

  return (
    <Link href={`/rooms/${listing.id}`} className="flex flex-col gap-3 group">
      {/* Photo carousel wrapper */}
      <div className="relative">
        <PhotoCarousel photos={listing.photos} title={listing.title} />

        {/* Guest favorite badge */}
        {listing.is_guest_favorite && (
          <div className="absolute top-3 left-3 bg-white rounded-full px-2.5 py-1 text-[11px] font-semibold text-text shadow">
            Guest favorite
          </div>
        )}

        {/* Heart button */}
        <button
          onClick={handleHeart}
          aria-pressed={saved}
          aria-label={`${saved ? 'Remove' : 'Save'} ${listing.title} to wishlist`}
          className="absolute top-3 right-3 p-1.5 text-white transition-transform active:scale-90"
        >
          <Heart
            size={24}
            strokeWidth={1.5}
            className={clsx(
              'drop-shadow-[0_1px_2px_rgba(0,0,0,0.4)] transition-colors',
              saved ? 'fill-brand text-brand' : 'fill-black/20',
            )}
          />
        </button>
      </div>

      {/* Text block */}
      <div className="flex flex-col gap-0.5">
        {/* Row 1: City + Rating */}
        <div className="flex items-center justify-between gap-2">
          <span className="text-[15px] font-semibold text-text truncate">
            {listing.city}, {listing.country}
          </span>
          {ratingText !== 'New' ? (
            <span className="flex items-center gap-1 text-sm text-text shrink-0">
              <Star size={14} className="fill-text text-text" />
              {ratingText}
            </span>
          ) : (
            <span className="text-sm text-text-muted shrink-0">New</span>
          )}
        </div>

        {/* Row 2: Property description */}
        <p className="text-sm text-text-muted truncate">
          {listing.room_type} · {listing.beds} bed{listing.beds !== 1 ? 's' : ''}
        </p>

        {/* Row 3: Dates if searching */}
        {searchDates && (
          <p className="text-sm text-text-muted">
            {searchDates.checkIn} – {searchDates.checkOut}
          </p>
        )}

        {/* Row 4: Price */}
        <p className="text-[15px] text-text mt-1">
          <span className="font-semibold">{formatMoney(listing.price_per_night)}</span>
          {searchDates ? (
            <span className="text-text-muted font-normal">
              {' '}
              for {searchDates.nights} night{searchDates.nights !== 1 ? 's' : ''}
            </span>
          ) : (
            <span className="text-text-muted font-normal"> / night</span>
          )}
        </p>
      </div>
    </Link>
  );
}
