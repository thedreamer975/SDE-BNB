'use client';

import React, { useEffect } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { auth as authApi, ApiError } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { useToast } from '@/lib/toast-context';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

const schema = z.object({
  name: z
    .string()
    .min(2, 'Name must be at least 2 characters.')
    .max(60, 'Name must be 60 characters or fewer.'),
  email: z.string().email('Please enter a valid email address.'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters.')
    .max(128, 'Password must be 128 characters or fewer.')
    .regex(/[a-zA-Z]/, 'Password must contain at least 1 letter.')
    .regex(/[0-9]/, 'Password must contain at least 1 number.'),
});

type FormValues = z.infer<typeof schema>;

export default function SignupPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, setUser } = useAuth();
  const { addToast } = useToast();
  const next = searchParams.get('next') ?? '/';

  useEffect(() => {
    if (user) router.replace(next);
  }, [user, router, next]);

  const {
    register,
    handleSubmit,
    setError,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const passwordValue = watch('password') ?? '';
  const hasLetter = /[a-zA-Z]/.test(passwordValue);
  const hasNumber = /[0-9]/.test(passwordValue);
  const longEnough = passwordValue.length >= 8;

  async function onSubmit(data: FormValues) {
    try {
      const me = await authApi.register(data);
      setUser(me);
      addToast({ message: `Welcome to Scalar, ${me.name.split(' ')[0]}!` });
      router.push(next);
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 409 && err.fieldErrors?.email) {
          setError('email', { message: err.fieldErrors.email[0] });
        } else if (err.status === 429) {
          setError('root', { message: 'Too many attempts. Try again in a minute.' });
        } else if (err.fieldErrors) {
          for (const [field, msgs] of Object.entries(err.fieldErrors)) {
            setError(field as keyof FormValues, { message: msgs[0] });
          }
        } else {
          setError('root', { message: err.message });
        }
      }
    }
  }

  return (
    <div className="w-full max-w-[568px] border border-border rounded-card p-8 shadow-lg">
      <h1 className="text-[22px] font-semibold text-text mb-6">Log in or sign up</h1>
      <div className="w-full h-px bg-border mb-6" />

      <h2 className="text-[26px] font-semibold text-text mb-6">Welcome to Scalar</h2>

      <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-4">
        <Input
          id="signup-name"
          label="Full name"
          type="text"
          autoComplete="name"
          placeholder="Your name"
          error={errors.name?.message}
          {...register('name')}
        />
        <Input
          id="signup-email"
          label="Email address"
          type="email"
          autoComplete="email"
          placeholder="you@example.com"
          error={errors.email?.message}
          {...register('email')}
        />
        <div className="flex flex-col gap-2">
          <Input
            id="signup-password"
            label="Password"
            type="password"
            autoComplete="new-password"
            placeholder="Create a password"
            error={errors.password?.message}
            {...register('password')}
          />
          {/* Password strength hints */}
          {passwordValue && (
            <ul className="flex flex-col gap-1">
              <StrengthHint met={longEnough} label="At least 8 characters" />
              <StrengthHint met={hasLetter} label="At least 1 letter" />
              <StrengthHint met={hasNumber} label="At least 1 number" />
            </ul>
          )}
        </div>

        {errors.root && (
          <p role="alert" className="text-sm text-error">
            {errors.root.message}
          </p>
        )}

        <Button
          id="signup-submit"
          type="submit"
          variant="primary"
          size="lg"
          loading={isSubmitting}
          fullWidth
          className="mt-2"
        >
          Agree and continue
        </Button>

        <p className="text-xs text-text-muted text-center">
          By selecting <strong>Agree and continue</strong>, I agree to Scalar&apos;s{' '}
          <Link href="/coming-soon/terms" className="underline">
            Terms of Service
          </Link>{' '}
          and{' '}
          <Link href="/coming-soon/privacy" className="underline">
            Privacy Policy
          </Link>
          .
        </p>
      </form>

      <p className="text-sm text-text-muted text-center mt-6">
        Already have an account?{' '}
        <Link
          href={`/login${next !== '/' ? `?next=${encodeURIComponent(next)}` : ''}`}
          className="text-text underline underline-offset-2 hover:text-text-muted"
        >
          Log in
        </Link>
      </p>
    </div>
  );
}

function StrengthHint({ met, label }: { met: boolean; label: string }) {
  return (
    <li className={`flex items-center gap-2 text-xs ${met ? 'text-success' : 'text-text-muted'}`}>
      <span className={`w-3 h-3 rounded-full border ${met ? 'bg-success border-success' : 'border-border-strong'}`} />
      {label}
    </li>
  );
}
