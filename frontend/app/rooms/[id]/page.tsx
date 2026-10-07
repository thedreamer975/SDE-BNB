import React, { Suspense } from 'react';
import type { Metadata } from 'next';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { RoomDetailClient } from './RoomDetailClient';

interface Props {
  params: { id: string };
}

// Generate metadata by calling the backend directly (SSR bypasses the frontend proxy)
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/listings/${params.id}`);
    if (res.ok) {
      const listing = await res.json();
      return {
        title: `${listing.title} — Scalar`,
        description: `${listing.room_type} in ${listing.city}. ${listing.description?.substring(0, 150)}...`,
      };
    }
  } catch {
    // ignore
  }
  return { title: 'Room Details — Scalar' };
}

export default function RoomPage({ params }: Props) {
  if (!params.id) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <h1 className="text-2xl font-bold mb-4">Invalid Room ID</h1>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-bg">
      <Header />
      <main className="flex-1">
        <Suspense fallback={<div className="h-[50vh] flex items-center justify-center">Loading...</div>}>
          <RoomDetailClient listingId={params.id} />
        </Suspense>
      </main>
      <Footer />
    </div>
  );
}
