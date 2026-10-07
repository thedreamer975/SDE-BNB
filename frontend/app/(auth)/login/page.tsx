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
import type { Metadata } from 'next';

const schema = z.object({
  email: z.string().email('Please enter a valid email address.'),
  password: z.string().min(1, 'Password is required.'),
});

type FormValues = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, setUser } = useAuth();
  const { addToast } = useToast();
  const next = searchParams.get('next') ?? '/';

  // Redirect if already logged in
  useEffect(() => {
    if (user) router.replace(next);
  }, [user, router, next]);

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(data: FormValues) {
    try {
      const me = await authApi.login(data);
      setUser(me);
      addToast({ message: `Welcome back, ${me.name.split(' ')[0]}!` });
      router.push(next);
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 429) {
          setError('root', { message: 'Too many attempts. Try again in a minute.' });
        } else if (err.status === 401 || err.status === 422) {
          setError('root', { message: 'Incorrect email or password.' });
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
          id="login-email"
          label="Email address"
          type="email"
          autoComplete="email"
          placeholder="you@example.com"
          error={errors.email?.message}
          {...register('email')}
        />
        <Input
          id="login-password"
          label="Password"
          type="password"
          autoComplete="current-password"
          placeholder="Enter your password"
          error={errors.password?.message}
          {...register('password')}
        />

        {errors.root && (
          <p role="alert" className="text-sm text-error">
            {errors.root.message}
          </p>
        )}

        <Button
          id="login-submit"
          type="submit"
          variant="primary"
          size="lg"
          loading={isSubmitting}
          fullWidth
          className="mt-2"
        >
          Log in
        </Button>
      </form>

      <p className="text-sm text-text-muted text-center mt-6">
        Don&apos;t have an account?{' '}
        <Link
          href={`/signup${next !== '/' ? `?next=${encodeURIComponent(next)}` : ''}`}
          className="text-text underline underline-offset-2 hover:text-text-muted"
        >
          Sign up
        </Link>
      </p>
    </div>
  );
}
