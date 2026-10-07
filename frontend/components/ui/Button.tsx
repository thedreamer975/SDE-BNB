import React from 'react';
import { clsx } from 'clsx';
import { Loader2 } from 'lucide-react';

export type ButtonVariant = 'primary' | 'brand' | 'secondary' | 'tertiary' | 'ghost';
export type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  fullWidth?: boolean;
  as?: 'button' | 'a';
  href?: string;
}

const variants: Record<ButtonVariant, string> = {
  primary: 'bg-text text-white hover:opacity-90 active:opacity-75',
  brand: 'bg-brand-grad text-white hover:opacity-90 active:opacity-80',
  secondary: 'bg-white text-text border border-text hover:bg-surface active:opacity-80',
  tertiary: 'underline underline-offset-2 text-text hover:text-text-muted bg-transparent',
  ghost: 'text-text bg-transparent hover:bg-surface active:bg-border',
};

const sizes: Record<ButtonSize, string> = {
  sm: 'h-10 px-4 text-sm',
  md: 'h-12 px-6 text-base',
  lg: 'h-14 px-8 text-base',
};

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  fullWidth = false,
  className,
  disabled,
  children,
  ...rest
}: ButtonProps) {
  return (
    <button
      {...rest}
      disabled={disabled || loading}
      aria-disabled={disabled || loading}
      className={clsx(
        'inline-flex items-center justify-center gap-2 font-medium rounded-btn transition-all duration-150 focus-visible:outline-2 focus-visible:outline-focus focus-visible:outline-offset-2',
        'disabled:opacity-40 disabled:cursor-not-allowed select-none',
        variants[variant],
        sizes[size],
        fullWidth && 'w-full',
        className,
      )}
    >
      {loading && <Loader2 size={16} className="animate-spin shrink-0" />}
      {children}
    </button>
  );
}
