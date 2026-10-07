import React from 'react';
import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = { title: 'Page not found — Scalar' };

export default function NotFoundPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-6 px-6 text-center">
      <p className="text-[80px] leading-none">🔍</p>
      <h1 className="text-[32px] font-semibold text-text">Page not found</h1>
      <p className="text-text-muted max-w-sm">
        Sorry, we can&apos;t find that page. It may have been moved or deleted.
      </p>
      <Link
        href="/"
        className="inline-flex items-center justify-center h-12 px-6 bg-text text-white rounded-btn font-medium hover:opacity-90 transition-opacity"
      >
        Back to explore
      </Link>
    </div>
  );
}
