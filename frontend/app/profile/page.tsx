'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { users } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { Button } from '@/components/ui/Button';
import { useToast } from '@/lib/toast-context';

export default function ProfilePage() {
  const { user, setUser } = useAuth();
  const { addToast } = useToast();
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    bio: '',
    avatar_url: '',
  });

  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || '',
        bio: user.bio || '',
        avatar_url: user.avatar_url || '',
      });
    }
  }, [user]);

  if (!user) {
    return (
      <div className="min-h-screen flex flex-col bg-bg">
        <Header />
        <main className="flex-1 flex items-center justify-center p-6 text-center">
          <div>
            <h1 className="text-2xl font-bold mb-4">Please log in to view your profile</h1>
            <Button variant="brand" href="/login">Log In</Button>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const updatedUser = await users.updateMe({
        name: formData.name,
        bio: formData.bio,
        avatar_url: formData.avatar_url,
      });
      setUser(updatedUser);
      addToast({ message: 'Profile updated successfully!' });
    } catch (err: any) {
      addToast({ message: err.message || 'Failed to update profile', type: 'error' });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-bg">
      <Header />
      <main className="flex-1 max-w-3xl mx-auto w-full px-6 py-12">
        <h1 className="text-3xl font-bold text-text mb-8">Personal info</h1>
        
        <form onSubmit={handleSubmit} className="flex flex-col gap-6">
          <div className="flex flex-col gap-2">
            <label className="text-sm font-semibold text-text">Legal name</label>
            <input
              type="text"
              className="input-field"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
            <p className="text-xs text-text-muted">This is the name on your travel document, which could be a license or a passport.</p>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm font-semibold text-text">Email address</label>
            <input
              type="email"
              className="input-field bg-surface text-text-muted cursor-not-allowed"
              value={user.email}
              disabled
            />
            <p className="text-xs text-text-muted">Use this address to log in to your account. (Cannot be changed)</p>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm font-semibold text-text">Avatar URL</label>
            <input
              type="url"
              className="input-field"
              value={formData.avatar_url}
              onChange={(e) => setFormData({ ...formData, avatar_url: e.target.value })}
              placeholder="https://example.com/avatar.jpg"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm font-semibold text-text">Bio</label>
            <textarea
              className="input-field"
              rows={4}
              value={formData.bio}
              onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
              placeholder="Tell us a little bit about yourself..."
            />
          </div>

          <div className="pt-6 border-t border-border flex justify-end">
            <Button variant="brand" type="submit" loading={loading} disabled={!formData.name}>
              Save
            </Button>
          </div>
        </form>
      </main>
      <Footer />
    </div>
  );
}
