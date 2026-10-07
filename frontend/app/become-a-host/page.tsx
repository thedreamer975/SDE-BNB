'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Home, Camera, Globe } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { Button } from '@/components/ui/Button';
import { users as usersApi } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { useToast } from '@/lib/toast-context';

const STEPS = [
  {
    icon: <Home size={32} className="text-brand" />,
    title: 'Describe your place',
    description:
      'Share what makes your space special — the type of space, location, and who can stay.',
  },
  {
    icon: <Camera size={32} className="text-brand" />,
    title: 'Add photos',
    description:
      'Show guests what your space looks like. Great photos lead to more bookings.',
  },
  {
    icon: <Globe size={32} className="text-brand" />,
    title: 'Publish and earn',
    description:
      'Set your price, publish your listing, and start welcoming guests from around the world.',
  },
];

export default function BecomeAHostPage() {
  const { user, setUser } = useAuth();
  const { addToast } = useToast();
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  // Already a host
  if (user?.role === 'host') {
    router.replace('/hosting');
    return null;
  }

  async function handleGetStarted() {
    setLoading(true);
    try {
      const updated = await usersApi.becomeHost();
      setUser(updated);
      addToast({ message: 'You are now a host! Create your first listing.' });
      router.push('/hosting/listings/new');
    } catch {
      addToast({ message: 'Something went wrong. Please try again.', type: 'error' });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 px-6 sm:px-10 lg:px-20 py-16">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-[32px] font-semibold text-text mb-4">
            Become a Scalar Host
          </h1>
          <p className="text-text-muted text-lg mb-12 max-w-xl">
            Join thousands of hosts earning extra income by sharing their spaces with travelers from
            around the world.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-10 mb-16">
            {STEPS.map((step, i) => (
              <div key={i} className="flex flex-col gap-4">
                <div className="w-14 h-14 rounded-full bg-brand/10 flex items-center justify-center">
                  {step.icon}
                </div>
                <div>
                  <p className="text-xs font-semibold text-text-muted uppercase tracking-wide mb-1">
                    Step {i + 1}
                  </p>
                  <h2 className="text-[18px] font-semibold text-text mb-1">{step.title}</h2>
                  <p className="text-sm text-text-muted leading-relaxed">{step.description}</p>
                </div>
              </div>
            ))}
          </div>

          <Button
            id="become-host-cta"
            variant="brand"
            size="lg"
            loading={loading}
            onClick={handleGetStarted}
          >
            Get started
          </Button>
        </div>
      </main>
      <Footer />
    </div>
  );
}
