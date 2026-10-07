import React from 'react';
import Link from 'next/link';

const COLUMNS = [
  {
    title: 'Support',
    links: [
      { label: 'Help Center', href: '/coming-soon/help' },
      { label: 'AirCover', href: '/coming-soon/aircover' },
      { label: 'Anti-discrimination', href: '/coming-soon/anti-discrimination' },
      { label: 'Disability support', href: '/coming-soon/accessibility' },
      { label: 'Cancellation options', href: '/coming-soon/cancellation' },
      { label: 'Report neighborhood concern', href: '/coming-soon/neighborhood' },
    ],
  },
  {
    title: 'Hosting',
    links: [
      { label: 'Airbnb your home', href: '/become-a-host' },
      { label: 'AirCover for Hosts', href: '/coming-soon/aircover-hosts' },
      { label: 'Hosting resources', href: '/coming-soon/resources' },
      { label: 'Community forum', href: '/coming-soon/forum' },
      { label: 'Hosting responsibly', href: '/coming-soon/responsible-hosting' },
      { label: 'Airbnb-friendly apartments', href: '/coming-soon/friendly-apartments' },
    ],
  },
  {
    title: 'Airbnb',
    links: [
      { label: 'Newsroom', href: '/coming-soon/newsroom' },
      { label: 'New features', href: '/coming-soon/features' },
      { label: 'Careers', href: '/coming-soon/careers' },
      { label: 'Investors', href: '/coming-soon/investors' },
      { label: 'Gift cards', href: '/coming-soon/gift-cards' },
      { label: 'Emergencies', href: '/coming-soon/emergencies' },
    ],
  },
];

export function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="bg-surface border-t border-border">
      <div className="px-6 sm:px-10 lg:px-20 py-10">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
          {COLUMNS.map((col) => (
            <div key={col.title}>
              <h3 className="text-xs font-semibold text-text mb-3 tracking-wide uppercase">
                {col.title}
              </h3>
              <ul className="space-y-2">
                {col.links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-text-muted hover:text-text transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
      <div className="border-t border-border px-6 sm:px-10 lg:px-20 py-4 flex flex-wrap items-center gap-4 text-sm text-text-muted">
        <span>© {year} Scalar, Inc.</span>
        <span className="w-px h-4 bg-border" aria-hidden="true" />
        <Link href="/coming-soon/privacy" className="hover:text-text transition-colors">
          Privacy
        </Link>
        <span className="w-px h-4 bg-border" aria-hidden="true" />
        <Link href="/coming-soon/terms" className="hover:text-text transition-colors">
          Terms
        </Link>
        <span className="w-px h-4 bg-border" aria-hidden="true" />
        <Link href="/coming-soon/sitemap" className="hover:text-text transition-colors">
          Sitemap
        </Link>
      </div>
    </footer>
  );
}
