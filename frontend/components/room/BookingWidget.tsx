'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { bookings, ApiError } from '@/lib/api';
import { formatMoney } from '@/lib/format';
import { Button } from '@/components/ui/Button';

interface BookingWidgetProps {
  listingId: string;
  pricePerNight: number;
}

export function BookingWidget({ listingId, pricePerNight }: BookingWidgetProps) {
  const router = useRouter();

  const [checkIn, setCheckIn] = useState('');
  const [checkOut, setCheckOut] = useState('');
  const [adults, setAdults] = useState(1);
  const [children, setChildren] = useState(0);
  const [infants, setInfants] = useState(0);
  const [pets, setPets] = useState(0);

  const [quote, setQuote] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Re-run quote whenever inputs change and are valid
  useEffect(() => {
    if (!checkIn || !checkOut || checkIn >= checkOut) {
      setQuote(null);
      setError(null);
      return;
    }

    const cancelController = new AbortController();

    async function getQuote() {
      setLoading(true);
      setError(null);
      try {
        const data = await bookings.quote({
          listing_id: listingId,
          check_in: checkIn,
          check_out: checkOut,
          adults,
          children,
          infants,
          pets,
        });
        setQuote(data);
      } catch (err) {
        setQuote(null);
        if (err instanceof ApiError) {
          setError(err.message || 'Dates unavailable');
        } else {
          setError('Could not calculate quote.');
        }
      } finally {
        setLoading(false);
      }
    }

    // debounce quote calculation
    const timer = setTimeout(getQuote, 500);
    return () => {
      clearTimeout(timer);
      cancelController.abort();
    };
  }, [listingId, checkIn, checkOut, adults, children, infants, pets]);

  function handleReserve() {
    if (!quote) return;
    const url = new URLSearchParams({
      check_in: checkIn,
      check_out: checkOut,
      adults: String(adults),
      children: String(children),
      infants: String(infants),
      pets: String(pets),
    });
    router.push(`/book/${listingId}?${url.toString()}`);
  }

  // Calculate minimum check-in date (today)
  const today = new Date().toISOString().split('T')[0];
  const minCheckOut = checkIn ? new Date(new Date(checkIn).getTime() + 86400000).toISOString().split('T')[0] : today;

  return (
    <div className="sticky top-28 bg-bg border border-border rounded-card p-6 shadow-xl w-full max-w-[400px]">
      <div className="flex items-end gap-1 mb-6">
        <span className="text-2xl font-semibold text-text">{formatMoney(pricePerNight)}</span>
        <span className="text-base text-text-muted pb-1">night</span>
      </div>

      <div className="flex flex-col border border-border rounded-[8px] overflow-hidden mb-4 focus-within:border-text">
        <div className="flex divide-x divide-border border-b border-border">
          <div className="flex-1 p-3 flex flex-col relative">
            <label htmlFor="check_in" className="text-[10px] font-extrabold uppercase text-text mb-1">
              Check-in
            </label>
            <input
              id="check_in"
              type="date"
              min={today}
              value={checkIn}
              onChange={(e) => setCheckIn(e.target.value)}
              className="text-sm outline-none bg-transparent w-full cursor-pointer"
            />
          </div>
          <div className="flex-1 p-3 flex flex-col relative">
            <label htmlFor="check_out" className="text-[10px] font-extrabold uppercase text-text mb-1">
              Check-out
            </label>
            <input
              id="check_out"
              type="date"
              min={minCheckOut}
              value={checkOut}
              onChange={(e) => setCheckOut(e.target.value)}
              className="text-sm outline-none bg-transparent w-full cursor-pointer"
            />
          </div>
        </div>
        <div className="p-3 flex flex-col relative">
          <label htmlFor="guests" className="text-[10px] font-extrabold uppercase text-text mb-1">
            Guests
          </label>
          <div className="flex items-center gap-2">
            <select
              id="guests"
              value={adults}
              onChange={(e) => setAdults(Number(e.target.value))}
              className="text-sm outline-none bg-transparent flex-1 cursor-pointer"
            >
              {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
                <option key={n} value={n}>{n} {n === 1 ? 'Adult' : 'Adults'}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-4 text-sm text-error bg-error/10 p-3 rounded-[8px]">
          {error}
        </div>
      )}

      <Button
        variant="brand"
        size="lg"
        fullWidth
        disabled={!checkIn || !checkOut || !!error}
        loading={loading}
        onClick={handleReserve}
      >
        Reserve
      </Button>

      {quote && !error && (
        <>
          <p className="text-sm text-text-muted text-center mt-4 mb-6">
            You won&apos;t be charged yet
          </p>
          <div className="flex flex-col gap-4 text-[15px] text-text border-b border-border pb-6 mb-6">
            <div className="flex justify-between">
              <span className="underline">{formatMoney(pricePerNight)} x {quote.nights} nights</span>
              <span>{formatMoney(quote.subtotal_cents)}</span>
            </div>
            {quote.cleaning_cents > 0 && (
              <div className="flex justify-between">
                <span className="underline">Cleaning fee</span>
                <span>{formatMoney(quote.cleaning_cents)}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="underline">Scalar service fee</span>
              <span>{formatMoney(quote.service_cents)}</span>
            </div>
          </div>
          <div className="flex justify-between font-semibold text-text">
            <span>Total before taxes</span>
            <span>{formatMoney(quote.total_cents)}</span>
          </div>
        </>
      )}
    </div>
  );
}
