'use client';

import React, { useState, useMemo } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import useSWR from 'swr';
import { meta, SearchParams } from '@/lib/api';
import { CategoryBar } from './CategoryBar';
import { FilterModal } from './FilterModal';
import { ListingGrid } from './ListingGrid';

export function ExploreContainer() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  // Read meta
  const { data: metaData } = useSWR('meta', meta.get, { revalidateOnFocus: false });

  // Convert URLSearchParams to SearchParams object
  const currentParams = useMemo(() => {
    const params: Partial<SearchParams> = {};
    const loc = searchParams.get('location');
    if (loc) params.location = loc;
    const cat = searchParams.get('category');
    if (cat) params.category = cat;
    
    // Numeric and boolean params
    const minP = searchParams.get('min_price');
    if (minP) params.min_price = Number(minP);
    const maxP = searchParams.get('max_price');
    if (maxP) params.max_price = Number(maxP);
    
    const rt = searchParams.get('room_type');
    if (rt) params.room_type = rt;
    
    const beds = searchParams.get('beds');
    if (beds) params.beds = Number(beds);
    const baths = searchParams.get('baths');
    if (baths) params.baths = Number(baths);
    const bedrooms = searchParams.get('bedrooms');
    if (bedrooms) params.bedrooms = Number(bedrooms);
    
    const pt = searchParams.get('property_type');
    if (pt) params.property_type = pt;
    
    const amenities = searchParams.get('amenities');
    if (amenities) params.amenities = amenities.split(',').map(Number);
    
    const sh = searchParams.get('superhost');
    if (sh === 'true') params.superhost = true;
    const gf = searchParams.get('guest_favorite');
    if (gf === 'true') params.guest_favorite = true;

    // Dates
    const ci = searchParams.get('check_in');
    if (ci) params.check_in = ci;
    const co = searchParams.get('check_out');
    if (co) params.check_out = co;

    // Capacity
    const adults = searchParams.get('adults');
    if (adults) params.adults = Number(adults);
    const children = searchParams.get('children');
    if (children) params.children = Number(children);
    const infants = searchParams.get('infants');
    if (infants) params.infants = Number(infants);
    const pets = searchParams.get('pets');
    if (pets) params.pets = Number(pets);

    return params as SearchParams;
  }, [searchParams]);

  // Compute active filters count (excluding q, category, dates, capacity)
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (currentParams.min_price || currentParams.max_price) count++;
    if (currentParams.room_type) count++;
    if (currentParams.beds) count++;
    if (currentParams.baths) count++;
    if (currentParams.bedrooms) count++;
    if (currentParams.property_type) count++;
    if (currentParams.amenities?.length) count++;
    if (currentParams.superhost) count++;
    if (currentParams.guest_favorite) count++;
    return count;
  }, [currentParams]);

  function applyFilters(newParams: Partial<SearchParams>) {
    const nextUrl = new URLSearchParams(searchParams.toString());
    
    // Clear old filter-specific ones
    const keysToClear = [
      'min_price', 'max_price', 'room_type', 'beds', 'baths', 'bedrooms',
      'property_type', 'amenities', 'superhost', 'guest_favorite', 'page'
    ];
    for (const key of keysToClear) nextUrl.delete(key);

    // Apply new
    for (const [key, value] of Object.entries(newParams)) {
      if (value !== undefined && value !== null && value !== '') {
        if (Array.isArray(value)) {
          if (value.length > 0) nextUrl.set(key, value.join(','));
        } else {
          nextUrl.set(key, String(value));
        }
      }
    }

    router.push(`/?${nextUrl.toString()}`, { scroll: false });
  }

  function handleCategoryChange(slug: string | null) {
    const nextUrl = new URLSearchParams(searchParams.toString());
    nextUrl.delete('page');
    if (slug) {
      nextUrl.set('category', slug);
    } else {
      nextUrl.delete('category');
    }
    router.push(`/?${nextUrl.toString()}`, { scroll: false });
  }

  return (
    <>
      <CategoryBar
        categories={metaData?.categories ?? []}
        activeCategory={currentParams.category ?? null}
        onCategoryChange={handleCategoryChange}
        onFiltersClick={() => setIsFilterOpen(true)}
        activeFilterCount={activeFilterCount}
      />
      <main className="flex-1 px-6 sm:px-10 lg:px-20 py-8">
        <ListingGrid searchParams={currentParams} />
      </main>
      <FilterModal
        isOpen={isFilterOpen}
        onClose={() => setIsFilterOpen(false)}
        currentParams={currentParams}
        onApply={applyFilters}
      />
    </>
  );
}
