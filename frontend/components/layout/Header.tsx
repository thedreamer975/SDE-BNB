'use client';

import React, { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  Search,
  Menu,
  Bell,
  Globe,
  User,
  LogOut,
  Home,
  Map,
  Heart,
  Luggage,
} from 'lucide-react';
import { clsx } from 'clsx';
import { useAuth } from '@/lib/auth-context';
import { useToast } from '@/lib/toast-context';

// ─── Brand Logo ───────────────────────────────────────────────────────────────

function Logo() {
  return (
    <Link href="/" className="flex items-center gap-1 text-brand shrink-0" aria-label="Scalar home">
      <svg width="32" height="32" viewBox="0 0 32 32" fill="none" aria-hidden="true">
        <path
          d="M16 4C9.373 4 4 9.373 4 16s5.373 12 12 12 12-5.373 12-12S22.627 4 16 4zm0 2.4c5.302 0 9.6 4.298 9.6 9.6 0 5.303-4.298 9.6-9.6 9.6-5.303 0-9.6-4.297-9.6-9.6 0-5.302 4.297-9.6 9.6-9.6z"
          fill="currentColor"
          opacity="0.3"
        />
        <path
          d="M16 7C11.029 7 7 11.029 7 16s4.029 9 9 9 9-4.029 9-9-4.029-9-9-9zm0 2c3.866 0 7 3.134 7 7s-3.134 7-7 7-7-3.134-7-7 3.134-7 7-7z"
          fill="currentColor"
        />
        <circle cx="16" cy="16" r="3" fill="currentColor" />
      </svg>
      <span className="font-bold text-xl tracking-tight hidden sm:block">scalar</span>
    </Link>
  );
}

// ─── Collapsed Search Pill ─────────────────────────────────────────────────────

function CollapsedSearchPill({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      id="header-search-pill"
      className="flex items-center gap-2 border border-border rounded-full px-4 py-2 shadow-sm hover:shadow-md transition-shadow text-sm font-medium text-text"
    >
      <span className="border-r border-border pr-3">Anywhere</span>
      <span className="border-r border-border pr-3">Any week</span>
      <span className="text-text-muted pr-3">Add guests</span>
      <span className="bg-brand text-white rounded-full p-[6px]">
        <Search size={14} />
      </span>
    </button>
  );
}

// ─── Expanded Search Bar ───────────────────────────────────────────────────────

function ExpandedSearchBar({ onClose }: { onClose: () => void }) {
  const router = useRouter();
  const [where, setWhere] = useState('');

  function handleSearch() {
    const params = new URLSearchParams();
    if (where) params.set('location', where);
    router.push(`/?${params.toString()}`);
    onClose();
  }

  return (
    <div className="flex items-center bg-white border border-border rounded-full shadow-lg overflow-hidden divide-x divide-border h-[56px] flex-1 max-w-2xl">
      <div className="flex-1 px-6 flex flex-col justify-center min-w-0">
        <span className="text-[11px] font-semibold">Where</span>
        <input
          autoFocus
          type="text"
          placeholder="Search destinations"
          value={where}
          onChange={(e) => setWhere(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          className="text-sm bg-transparent outline-none placeholder:text-text-muted w-full"
        />
      </div>
      <div className="flex-1 px-6 flex flex-col justify-center">
        <span className="text-[11px] font-semibold">Check in</span>
        <span className="text-sm text-text-muted">Add dates</span>
      </div>
      <div className="flex-1 px-6 flex flex-col justify-center">
        <span className="text-[11px] font-semibold">Check out</span>
        <span className="text-sm text-text-muted">Add dates</span>
      </div>
      <div className="flex-shrink-0 pr-2 pl-6 flex items-center gap-3">
        <div className="flex flex-col">
          <span className="text-[11px] font-semibold">Who</span>
          <span className="text-sm text-text-muted">Add guests</span>
        </div>
        <button
          onClick={handleSearch}
          className="bg-brand text-white rounded-full w-12 h-12 flex items-center justify-center hover:bg-brand/90 transition-colors shrink-0"
          aria-label="Search"
        >
          <Search size={18} />
        </button>
      </div>
    </div>
  );
}

// ─── Avatar Menu ──────────────────────────────────────────────────────────────

function AvatarMenu() {
  const { user, logout } = useAuth();
  const { addToast } = useToast();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  async function handleLogout() {
    await logout();
    addToast({ message: 'You have been logged out.' });
    router.push('/');
    setOpen(false);
  }

  const initials = user?.name
    ? user.name
        .split(' ')
        .slice(0, 2)
        .map((n) => n[0])
        .join('')
        .toUpperCase()
    : null;

  return (
    <div className="relative" ref={menuRef}>
      {/* Trigger */}
      <button
        id="avatar-menu-trigger"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-haspopup="menu"
        aria-label="Account menu"
        className={clsx(
          'flex items-center gap-2 border border-border rounded-full pl-3 pr-1 py-1 hover:shadow-md transition-all duration-150',
          open && 'shadow-md',
        )}
      >
        <Menu size={16} className="text-text" />
        {user ? (
          <div className="w-8 h-8 rounded-full bg-text text-white flex items-center justify-center text-xs font-semibold shrink-0">
            {user.avatar_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={user.avatar_url} alt={user.name} className="w-full h-full rounded-full object-cover" />
            ) : (
              initials
            )}
          </div>
        ) : (
          <div className="w-8 h-8 rounded-full bg-text-muted text-white flex items-center justify-center">
            <User size={16} />
          </div>
        )}
      </button>

      {/* Dropdown */}
      {open && (
        <div
          role="menu"
          className="absolute right-0 top-[calc(100%+8px)] w-60 bg-bg border border-border rounded-card shadow-lg py-1 z-50"
        >
          {user ? (
            <>
              <MenuLink href="/messages" icon={<Globe size={16} />} label="Messages" onClick={() => setOpen(false)} />
              <MenuLink href="/trips" icon={<Luggage size={16} />} label="Trips" onClick={() => setOpen(false)} />
              <MenuLink href="/wishlists" icon={<Heart size={16} />} label="Wishlists" onClick={() => setOpen(false)} />
              <div className="border-t border-border my-1" />
              {user.role === 'host' ? (
                <MenuLink href="/hosting" icon={<Home size={16} />} label="Manage listings" onClick={() => setOpen(false)} />
              ) : (
                <MenuLink href="/become-a-host" icon={<Home size={16} />} label="Airbnb your home" onClick={() => setOpen(false)} />
              )}
              <MenuLink href="/account" icon={<User size={16} />} label="Account" onClick={() => setOpen(false)} />
              <div className="border-t border-border my-1" />
              <button
                role="menuitem"
                onClick={handleLogout}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-text hover:bg-surface"
              >
                <LogOut size={16} className="text-text-muted" />
                Log out
              </button>
            </>
          ) : (
            <>
              <MenuLink href="/signup" label="Sign up" onClick={() => setOpen(false)} bold />
              <MenuLink href="/login" label="Log in" onClick={() => setOpen(false)} />
              <div className="border-t border-border my-1" />
              <MenuLink href="/become-a-host" label="Airbnb your home" onClick={() => setOpen(false)} />
              <MenuLink href="/coming-soon/help" label="Help Center" onClick={() => setOpen(false)} />
            </>
          )}
        </div>
      )}
    </div>
  );
}

function MenuLink({
  href,
  label,
  icon,
  onClick,
  bold,
}: {
  href: string;
  label: string;
  icon?: React.ReactNode;
  onClick: () => void;
  bold?: boolean;
}) {
  return (
    <Link
      href={href}
      role="menuitem"
      onClick={onClick}
      className={clsx(
        'flex items-center gap-3 px-4 py-2.5 text-sm text-text hover:bg-surface',
        bold && 'font-semibold',
      )}
    >
      {icon && <span className="text-text-muted">{icon}</span>}
      {label}
    </Link>
  );
}

// ─── Main Header ──────────────────────────────────────────────────────────────

export function Header() {
  const { user } = useAuth();
  const [scrolled, setScrolled] = useState(false);
  const [searchExpanded, setSearchExpanded] = useState(false);

  useEffect(() => {
    function onScroll() {
      setScrolled(window.scrollY > 0);
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <header
      className={clsx(
        'sticky top-0 z-40 bg-bg transition-shadow duration-200',
        scrolled ? 'shadow-sm border-b border-border' : 'border-b border-transparent',
      )}
    >
      <div className="h-20 px-6 md:px-10 lg:px-20 flex items-center justify-between gap-4">
        {/* Left: Logo */}
        <Logo />

        {/* Center: Search */}
        <div className="flex-1 flex justify-center">
          {searchExpanded ? (
            <ExpandedSearchBar onClose={() => setSearchExpanded(false)} />
          ) : (
            <CollapsedSearchPill onClick={() => setSearchExpanded(true)} />
          )}
        </div>

        {/* Right: Become a host + bell + avatar */}
        <div className="flex items-center gap-2 shrink-0">
          {user?.role === 'host' ? (
            <Link
              href="/hosting"
              className="hidden sm:block text-sm font-medium text-text px-3 py-2 rounded-full hover:bg-surface transition-colors"
            >
              Switch to hosting
            </Link>
          ) : (
            <Link
              href="/become-a-host"
              className="hidden sm:block text-sm font-medium text-text px-3 py-2 rounded-full hover:bg-surface transition-colors"
            >
              Airbnb your home
            </Link>
          )}
          {user && (
            <Link
              href="/notifications"
              aria-label="Notifications"
              className="p-2 rounded-full hover:bg-surface transition-colors"
            >
              <Bell size={20} className="text-text" />
            </Link>
          )}
          <AvatarMenu />
        </div>
      </div>
    </header>
  );
}
