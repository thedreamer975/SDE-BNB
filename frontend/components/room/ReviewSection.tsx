'use client';

import React, { useState } from 'react';
import useSWR from 'swr';
import { Star, User } from 'lucide-react';
import { listings, ReviewsResponse, Review } from '@/lib/api';
import { formatRating } from '@/lib/format';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';

interface ReviewSectionProps {
  listingId: string;
}

export function ReviewSection({ listingId }: ReviewSectionProps) {
  const [showModal, setShowModal] = useState(false);
  const [page, setPage] = useState(1);

  // Initial load for summary and top 6 reviews
  const { data, error } = useSWR<ReviewsResponse>(
    ['listings.reviews', listingId, 1],
    () => listings.reviews(listingId, 1, 6),
    { revalidateOnFocus: false }
  );

  // Load more data for the modal
  const { data: modalData, isValidating: loadingMore } = useSWR<ReviewsResponse>(
    showModal ? ['listings.reviews', listingId, page] : null,
    () => listings.reviews(listingId, page, 20),
    { keepPreviousData: true, revalidateOnFocus: false }
  );

  if (error) return null;
  if (!data || data.total === 0) {
    return (
      <div className="py-12 border-t border-border">
        <h2 className="text-[22px] font-semibold text-text mb-4">No reviews (yet)</h2>
        <p className="text-text-muted">This host has some listings, but this one doesn&apos;t have any reviews.</p>
      </div>
    );
  }

  const ratingText = formatRating(data.avg, data.total);

  return (
    <>
      <div className="py-12 border-t border-border">
        <div className="flex items-center gap-2 mb-8">
          <Star size={24} className="fill-text text-text" />
          <h2 className="text-[22px] font-semibold text-text">{ratingText}</h2>
        </div>

        {/* Top 6 reviews grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-10 mb-10">
          {data.items.map((r) => (
            <ReviewCard key={r.id} review={r} />
          ))}
        </div>

        {data.total > 6 && (
          <button
            onClick={() => {
              setPage(1);
              setShowModal(true);
            }}
            className="px-6 py-3 border border-text rounded-btn font-semibold text-text hover:bg-surface transition-colors"
          >
            Show all {data.total} reviews
          </button>
        )}
      </div>

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="All reviews">
        <div className="flex flex-col max-w-2xl mx-auto py-6">
          <div className="flex items-center gap-2 mb-10">
            <Star size={32} className="fill-text text-text" />
            <h2 className="text-[32px] font-semibold text-text">{ratingText}</h2>
          </div>

          <div className="flex flex-col gap-10">
            {modalData?.items.map((r) => (
              <ReviewCard key={r.id} review={r} />
            ))}
          </div>

          {modalData?.items && modalData.items.length < modalData.total && (
            <div className="mt-10 flex justify-center">
              <Button
                variant="secondary"
                loading={loadingMore}
                onClick={() => setPage((p) => p + 1)}
              >
                Load more
              </Button>
            </div>
          )}
        </div>
      </Modal>
    </>
  );
}

function ReviewCard({ review }: { review: Review }) {
  const date = new Date(review.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 rounded-full bg-surface overflow-hidden flex items-center justify-center shrink-0">
          {review.guest_avatar ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={review.guest_avatar} alt={review.guest_name} className="w-full h-full object-cover" />
          ) : (
            <User size={24} className="text-text-muted" />
          )}
        </div>
        <div>
          <h4 className="font-semibold text-text">{review.guest_name.split(' ')[0]}</h4>
          <p className="text-sm text-text-muted">{date}</p>
        </div>
      </div>
      <p className="text-text leading-relaxed whitespace-pre-wrap line-clamp-4">{review.comment}</p>
    </div>
  );
}
