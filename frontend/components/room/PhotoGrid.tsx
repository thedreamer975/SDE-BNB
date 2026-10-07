'use client';

import React, { useState } from 'react';
import { Grip } from 'lucide-react';
import { Modal } from '@/components/ui/Modal';
import { clsx } from 'clsx';

interface PhotoGridProps {
  photos: string[];
  title: string;
}

export function PhotoGrid({ photos, title }: PhotoGridProps) {
  const [showAll, setShowAll] = useState(false);

  if (!photos || photos.length === 0) {
    return <div className="w-full h-[60vh] bg-surface rounded-[16px]" />;
  }

  const hero = photos[0];
  const others = photos.slice(1, 5); // up to 4

  return (
    <>
      <div className="relative w-full h-[40vh] md:h-[60vh] rounded-[16px] overflow-hidden group">
        <div className={clsx('w-full h-full gap-2', photos.length > 1 ? 'grid grid-cols-4' : 'flex')}>
          {/* Hero image - half width if others exist, full if not */}
          <div className={clsx('relative h-full overflow-hidden', photos.length > 1 ? 'col-span-2' : 'w-full')}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={hero}
              alt={title}
              className="w-full h-full object-cover hover:scale-105 transition-transform duration-500 cursor-pointer"
              onClick={() => setShowAll(true)}
            />
          </div>

          {/* 2x2 grid for remaining 4 photos */}
          {photos.length > 1 && (
            <div className="col-span-2 grid grid-cols-2 grid-rows-2 gap-2 h-full">
              {others.map((p, i) => (
                <div key={i} className="relative h-full overflow-hidden">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={p}
                    alt={`${title} - Photo ${i + 2}`}
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-500 cursor-pointer"
                    onClick={() => setShowAll(true)}
                  />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Show all button */}
        <button
          onClick={() => setShowAll(true)}
          className="absolute bottom-6 right-6 flex items-center gap-2 bg-white px-4 py-1.5 rounded-btn border border-text text-sm font-semibold shadow-sm hover:bg-surface transition-colors active:scale-95"
        >
          <Grip size={16} />
          Show all photos
        </button>
      </div>

      <Modal isOpen={showAll} onClose={() => setShowAll(false)} title="All photos">
        <div className="flex flex-col gap-4 max-w-3xl mx-auto py-4">
          {photos.map((p, i) => (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              key={i}
              src={p}
              alt={`${title} - Photo ${i + 1}`}
              className="w-full h-auto rounded-card object-cover"
              loading="lazy"
            />
          ))}
        </div>
      </Modal>
    </>
  );
}
