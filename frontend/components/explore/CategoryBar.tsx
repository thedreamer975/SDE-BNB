'use client';

import React, { useEffect, useRef, useState } from 'react';
import { ChevronLeft, ChevronRight, SlidersHorizontal } from 'lucide-react';
import { clsx } from 'clsx';
import { useRouter, useSearchParams } from 'next/navigation';
import type { MetaCategory } from '@/lib/api';

// Category icons mapped by slug (using emoji as fallback to lucide)
const CATEGORY_ICONS: Record<string, string> = {
  beach: '🏖️',
  mountain: '⛰️',
  city: '🏙️',
  countryside: '🌾',
  tropical: '🌴',
  historic: '🏛️',
  lake: '🏞️',
  skiing: '⛷️',
  camping: '⛺',
  luxury: '💎',
  unique: '🦄',
  island: '🏝️',
  desert: '🏜️',
  farm: '🐄',
};

function getCategoryIcon(slug: string): string {
  return CATEGORY_ICONS[slug] ?? '🏠';
}

interface CategoryBarProps {
  categories: MetaCategory[];
  activeCategory: string | null;
  onCategoryChange: (slug: string | null) => void;
  onFiltersClick: () => void;
  activeFilterCount: number;
}

export function CategoryBar({
  categories,
  activeCategory,
  onCategoryChange,
  onFiltersClick,
  activeFilterCount,
}: CategoryBarProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  function checkScroll() {
    const el = scrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 0);
    setCanScrollRight(el.scrollLeft < el.scrollWidth - el.clientWidth - 1);
  }

  useEffect(() => {
    checkScroll();
    const el = scrollRef.current;
    el?.addEventListener('scroll', checkScroll, { passive: true });
    window.addEventListener('resize', checkScroll);
    return () => {
      el?.removeEventListener('scroll', checkScroll);
      window.removeEventListener('resize', checkScroll);
    };
  }, [categories]);

  function scrollBy(amount: number) {
    scrollRef.current?.scrollBy({ left: amount, behavior: 'smooth' });
  }

  return (
    <div className="sticky top-20 z-30 bg-bg border-b border-border">
      <div className="px-6 sm:px-10 lg:px-20 flex items-center gap-3 h-20">
        {/* Left arrow */}
        {canScrollLeft && (
          <button
            onClick={() => scrollBy(-200)}
            aria-label="Scroll categories left"
            className="shrink-0 w-8 h-8 rounded-full border border-border bg-bg flex items-center justify-center shadow-sm hover:shadow-md transition-shadow"
          >
            <ChevronLeft size={16} />
          </button>
        )}

        {/* Category scroll container */}
        <div
          ref={scrollRef}
          className="flex-1 flex items-center gap-8 overflow-x-auto scrollbar-hide"
          style={{ scrollbarWidth: 'none' }}
        >
          {categories.map((cat) => {
            const isActive = activeCategory === cat.slug;
            return (
              <button
                key={cat.slug}
                id={`cat-${cat.slug}`}
                onClick={() => onCategoryChange(isActive ? null : cat.slug)}
                aria-pressed={isActive}
                className={clsx(
                  'flex flex-col items-center gap-1 shrink-0 pb-1 border-b-2 transition-all duration-150',
                  isActive
                    ? 'border-text opacity-100'
                    : 'border-transparent opacity-60 hover:opacity-80 hover:border-border',
                )}
              >
                <span className="text-2xl" aria-hidden="true">
                  {getCategoryIcon(cat.slug)}
                </span>
                <span className="text-[12px] font-semibold whitespace-nowrap">{cat.label}</span>
              </button>
            );
          })}
        </div>

        {/* Right arrow */}
        {canScrollRight && (
          <button
            onClick={() => scrollBy(200)}
            aria-label="Scroll categories right"
            className="shrink-0 w-8 h-8 rounded-full border border-border bg-bg flex items-center justify-center shadow-sm hover:shadow-md transition-shadow"
          >
            <ChevronRight size={16} />
          </button>
        )}

        {/* Filters button */}
        <button
          id="open-filters"
          onClick={onFiltersClick}
          className="shrink-0 flex items-center gap-2 border border-border rounded-[12px] px-4 h-12 text-sm font-medium hover:border-border-strong transition-colors"
        >
          <SlidersHorizontal size={16} />
          <span>Filters</span>
          {activeFilterCount > 0 && (
            <span className="w-5 h-5 bg-text text-white text-[11px] font-bold rounded-full flex items-center justify-center">
              {activeFilterCount}
            </span>
          )}
        </button>
      </div>
    </div>
  );
}
