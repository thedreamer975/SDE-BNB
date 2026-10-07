'use client';

import React, { useState } from 'react';
import { clsx } from 'clsx';
import { Eye, EyeOff } from 'lucide-react';

interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'id'> {
  id: string;
  label: string;
  error?: string;
}

export function Input({ id, label, error, className, type, ...rest }: InputProps) {
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = type === 'password';
  const inputType = isPassword ? (showPassword ? 'text' : 'password') : type;
  const errorId = error ? `${id}-error` : undefined;

  return (
    <div className="flex flex-col gap-1 w-full">
      <label htmlFor={id} className="text-sm font-medium text-text">
        {label}
      </label>
      <div className="relative">
        <input
          id={id}
          type={inputType}
          aria-invalid={!!error}
          aria-describedby={errorId}
          className={clsx(
            'w-full h-14 px-4 text-base rounded-btn border transition-colors duration-150 bg-bg text-text placeholder:text-text-muted',
            'focus:outline-none focus:border-text focus:ring-1 focus:ring-text',
            error
              ? 'border-error focus:border-error focus:ring-error'
              : 'border-border hover:border-border-strong',
            isPassword && 'pr-12',
            className,
          )}
          {...rest}
        />
        {isPassword && (
          <button
            type="button"
            tabIndex={-1}
            onClick={() => setShowPassword((v) => !v)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text p-1"
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        )}
      </div>
      {error && (
        <span id={errorId} role="alert" className="text-sm text-error">
          {error}
        </span>
      )}
    </div>
  );
}
