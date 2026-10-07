import React from 'react';
import Link from 'next/link';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';

function slugToTitle(slug: string): string {
  return slug
    .split('-')
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(' ');
}

interface Props {
  params: { slug: string };
}

export function generateMetadata({ params }: Props) {
  return { title: `${slugToTitle(params.slug)} — Scalar` };
}

export default function ComingSoonPage({ params }: Props) {
  const title = slugToTitle(params.slug);
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 flex flex-col items-center justify-center gap-4 px-6 text-center">
        <div className="w-16 h-16 rounded-full bg-surface flex items-center justify-center text-3xl">
          🚧
        </div>
        <h1 className="text-[32px] font-semibold text-text">{title}</h1>
        <p className="text-text-muted max-w-sm">
          This feature is coming soon. In the meantime, explore available listings on the home
          page.
        </p>
        <Link
          href="/"
          className="mt-2 inline-flex items-center justify-center h-12 px-6 bg-text text-white rounded-btn font-medium hover:opacity-90 transition-opacity"
        >
          Back to explore
        </Link>
      </main>
      <Footer />
    </div>
  );
}
