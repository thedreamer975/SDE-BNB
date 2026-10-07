'use client';

import React, { useState, useEffect } from 'react';
import useSWR from 'swr';
import { clsx } from 'clsx';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { listings, meta, SearchParams } from '@/lib/api';

interface FilterModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentParams: SearchParams;
  onApply: (params: Partial<SearchParams>) => void;
}

export function FilterModal({ isOpen, onClose, currentParams, onApply }: FilterModalProps) {
  // Local state for all filters
  const [minPrice, setMinPrice] = useState<number | ''>(currentParams.min_price ?? '');
  const [maxPrice, setMaxPrice] = useState<number | ''>(currentParams.max_price ?? '');
  const [roomType, setRoomType] = useState<string>(currentParams.room_type ?? '');
  const [bedrooms, setBedrooms] = useState<number>(currentParams.bedrooms ?? 0);
  const [beds, setBeds] = useState<number>(currentParams.beds ?? 0);
  const [baths, setBaths] = useState<number>(currentParams.baths ?? 0);
  const [propertyTypes, setPropertyTypes] = useState<string[]>(
    currentParams.property_type ? currentParams.property_type.split(',') : []
  );
  const [amenities, setAmenities] = useState<number[]>(currentParams.amenities ?? []);
  const [superhost, setSuperhost] = useState<boolean>(currentParams.superhost ?? false);
  const [guestFav, setGuestFav] = useState<boolean>(currentParams.guest_favorite ?? false);

  const [showAllAmenities, setShowAllAmenities] = useState(false);

  // Load Meta Data (cached by SWR)
  const { data: metaData } = useSWR('meta', meta.get, { revalidateOnFocus: false });

  // Build the current filter state as SearchParams
  const activeParams: SearchParams = React.useMemo(() => ({
    ...currentParams,
    min_price: minPrice !== '' ? minPrice : undefined,
    max_price: maxPrice !== '' ? maxPrice : undefined,
    room_type: roomType || undefined,
    bedrooms: bedrooms > 0 ? bedrooms : undefined,
    beds: beds > 0 ? beds : undefined,
    baths: baths > 0 ? baths : undefined,
    property_type: propertyTypes.length > 0 ? propertyTypes.join(',') : undefined,
    amenities: amenities.length > 0 ? amenities : undefined,
    superhost: superhost || undefined,
    guest_favorite: guestFav || undefined,
  }), [
    currentParams, minPrice, maxPrice, roomType, bedrooms, beds, baths,
    propertyTypes, amenities, superhost, guestFav
  ]);

  // Debounce the count lookup
  const [debouncedParams, setDebouncedParams] = useState(activeParams);
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedParams(activeParams), 300);
    return () => clearTimeout(handler);
  }, [activeParams]);

  // Fetch count
  const { data: countData } = useSWR(
    isOpen ? ['listings.count', debouncedParams] : null,
    ([, params]) => listings.count(params as SearchParams),
    { keepPreviousData: true }
  );

  function handleClear() {
    setMinPrice('');
    setMaxPrice('');
    setRoomType('');
    setBedrooms(0);
    setBeds(0);
    setBaths(0);
    setPropertyTypes([]);
    setAmenities([]);
    setSuperhost(false);
    setGuestFav(false);
  }

  function handleApply() {
    onApply({
      min_price: minPrice !== '' ? minPrice : undefined,
      max_price: maxPrice !== '' ? maxPrice : undefined,
      room_type: roomType || undefined,
      bedrooms: bedrooms > 0 ? bedrooms : undefined,
      beds: beds > 0 ? beds : undefined,
      baths: baths > 0 ? baths : undefined,
      property_type: propertyTypes.length > 0 ? propertyTypes.join(',') : undefined,
      amenities: amenities.length > 0 ? amenities : undefined,
      superhost: superhost || undefined,
      guest_favorite: guestFav || undefined,
      page: 1, // reset pagination on filter apply
    });
    onClose();
  }

  function togglePropertyType(pt: string) {
    setPropertyTypes((prev) =>
      prev.includes(pt) ? prev.filter((p) => p !== pt) : [...prev, pt]
    );
  }

  function toggleAmenity(id: number) {
    setAmenities((prev) =>
      prev.includes(id) ? prev.filter((a) => a !== id) : [...prev, id]
    );
  }

  const roomTypes = [
    { label: 'Any type', value: '' },
    { label: 'Room', value: 'Room' },
    { label: 'Entire home', value: 'Entire home' },
  ];

  const propTypes = [
    { label: 'House', value: 'House', icon: '🏠' },
    { label: 'Apartment', value: 'Apartment', icon: '🏢' },
    { label: 'Guesthouse', value: 'Guesthouse', icon: '🏡' },
    { label: 'Hotel', value: 'Hotel', icon: '🏨' },
  ];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Filters"
      footer={
        <>
          <button
            onClick={handleClear}
            className="underline font-medium text-text hover:text-text-muted transition-colors"
          >
            Clear all
          </button>
          <Button variant="primary" onClick={handleApply}>
            Show {countData?.count !== undefined ? countData.count : '...'} places
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-8 divide-y divide-border -mx-6 px-6">
        {/* Price range */}
        <section className="pt-2">
          <h3 className="text-xl font-semibold mb-4">Price range</h3>
          <div className="flex items-center gap-4">
            <div className="flex-1 flex flex-col gap-1 border border-border rounded-btn p-2 focus-within:border-text">
              <span className="text-xs text-text-muted px-1">Minimum</span>
              <div className="flex items-center px-1">
                <span className="text-text mr-1">$</span>
                <input
                  type="number"
                  min={0}
                  className="w-full outline-none bg-transparent"
                  value={minPrice}
                  onChange={(e) => setMinPrice(e.target.value ? Number(e.target.value) : '')}
                />
              </div>
            </div>
            <span className="text-text-muted">–</span>
            <div className="flex-1 flex flex-col gap-1 border border-border rounded-btn p-2 focus-within:border-text">
              <span className="text-xs text-text-muted px-1">Maximum</span>
              <div className="flex items-center px-1">
                <span className="text-text mr-1">$</span>
                <input
                  type="number"
                  min={0}
                  className="w-full outline-none bg-transparent"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(e.target.value ? Number(e.target.value) : '')}
                />
              </div>
            </div>
          </div>
        </section>

        {/* Room type */}
        <section className="pt-8">
          <h3 className="text-xl font-semibold mb-4">Type of place</h3>
          <div className="flex gap-4">
            {roomTypes.map((rt) => (
              <button
                key={rt.value}
                onClick={() => setRoomType(rt.value)}
                className={clsx(
                  'flex-1 border rounded-[12px] py-4 text-sm font-medium transition-colors hover:border-text',
                  roomType === rt.value ? 'border-text bg-surface' : 'border-border bg-transparent',
                )}
              >
                {rt.label}
              </button>
            ))}
          </div>
        </section>

        {/* Rooms and beds */}
        <section className="pt-8 flex flex-col gap-6">
          <h3 className="text-xl font-semibold mb-2">Rooms and beds</h3>
          <Stepper label="Bedrooms" value={bedrooms} onChange={setBedrooms} />
          <Stepper label="Beds" value={beds} onChange={setBeds} />
          <Stepper label="Bathrooms" value={baths} onChange={setBaths} />
        </section>

        {/* Property type */}
        <section className="pt-8">
          <h3 className="text-xl font-semibold mb-4">Property type</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {propTypes.map((pt) => {
              const selected = propertyTypes.includes(pt.value);
              return (
                <button
                  key={pt.value}
                  onClick={() => togglePropertyType(pt.value)}
                  className={clsx(
                    'flex flex-col items-start p-4 border rounded-[12px] transition-colors hover:border-text',
                    selected ? 'border-text bg-surface border-2' : 'border-border bg-transparent',
                  )}
                >
                  <span className="text-2xl mb-6">{pt.icon}</span>
                  <span className="font-medium text-sm">{pt.label}</span>
                </button>
              );
            })}
          </div>
        </section>

        {/* Amenities */}
        <section className="pt-8">
          <h3 className="text-xl font-semibold mb-4">Amenities</h3>
          <div className="grid grid-cols-2 gap-y-4 gap-x-2">
            {(metaData?.amenities ?? []).slice(0, showAllAmenities ? undefined : 6).map((a) => {
              const selected = amenities.includes(a.id);
              return (
                <label key={a.id} className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative flex items-center justify-center w-6 h-6 border rounded-[4px] border-border group-hover:border-text transition-colors">
                    <input
                      type="checkbox"
                      className="peer sr-only"
                      checked={selected}
                      onChange={() => toggleAmenity(a.id)}
                    />
                    {selected && (
                      <div className="absolute inset-0 bg-text rounded-[4px] flex items-center justify-center">
                        <svg className="w-3.5 h-3.5 text-white" viewBox="0 0 14 14" fill="none">
                          <path d="M11.666 3.5L5.25 9.916 2.333 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      </div>
                    )}
                  </div>
                  <span className="text-sm text-text">{a.name}</span>
                </label>
              );
            })}
          </div>
          {(metaData?.amenities.length ?? 0) > 6 && !showAllAmenities && (
            <button
              onClick={() => setShowAllAmenities(true)}
              className="mt-6 font-semibold underline text-text"
            >
              Show more
            </button>
          )}
        </section>

        {/* Badges */}
        <section className="pt-8 flex flex-col gap-6">
          <h3 className="text-xl font-semibold mb-2">Host language & badges</h3>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-base font-medium">Guest favorite</p>
              <p className="text-sm text-text-muted">The most loved homes on Scalar</p>
            </div>
            <Toggle checked={guestFav} onChange={setGuestFav} />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-base font-medium">Superhost</p>
              <p className="text-sm text-text-muted">Stay with recognized hosts</p>
            </div>
            <Toggle checked={superhost} onChange={setSuperhost} />
          </div>
        </section>
      </div>
    </Modal>
  );
}

// ─── Helpers ───────────────────────────────────────────────────────────────────

function Stepper({ label, value, onChange }: { label: string; value: number; onChange: (v: number) => void }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-base text-text font-normal">{label}</span>
      <div className="flex items-center gap-4">
        <button
          onClick={() => onChange(Math.max(0, value - 1))}
          disabled={value === 0}
          className="w-8 h-8 rounded-full border border-border flex items-center justify-center text-text-muted hover:border-text hover:text-text disabled:opacity-30 disabled:hover:border-border transition-colors"
          aria-label={`Decrease ${label}`}
        >
          <svg viewBox="0 0 12 12" className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 6h10" /></svg>
        </button>
        <span className="w-4 text-center text-base">{value === 0 ? 'Any' : value + (value === 8 ? '+' : '')}</span>
        <button
          onClick={() => onChange(Math.min(8, value + 1))}
          disabled={value === 8}
          className="w-8 h-8 rounded-full border border-border flex items-center justify-center text-text-muted hover:border-text hover:text-text disabled:opacity-30 transition-colors"
          aria-label={`Increase ${label}`}
        >
          <svg viewBox="0 0 12 12" className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 6h10M6 1v10" /></svg>
        </button>
      </div>
    </div>
  );
}

function Toggle({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={clsx(
        'relative inline-flex h-8 w-12 items-center rounded-full transition-colors',
        checked ? 'bg-text' : 'bg-border-strong',
      )}
    >
      <span
        className={clsx(
          'inline-block h-7 w-7 transform rounded-full bg-white transition-transform border border-border',
          checked ? 'translate-x-4 border-transparent' : 'translate-x-0.5',
        )}
      />
    </button>
  );
}
