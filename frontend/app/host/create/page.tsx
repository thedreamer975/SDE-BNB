'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import useSWR from 'swr';
import { host, meta, CreateListingBody } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { useToast } from '@/lib/toast-context';

export default function CreateListingPage() {
  const router = useRouter();
  const { addToast } = useToast();
  const { data: metaData } = useSWR('meta', meta.get);
  
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState<Partial<CreateListingBody>>({
    title: '',
    description: '',
    category: '',
    property_type: 'House',
    room_type: 'Entire home/apt',
    address: '',
    city: '',
    state: '',
    country: '',
    latitude: 0,
    longitude: 0,
    max_guests: 1,
    bedrooms: 1,
    beds: 1,
    baths: 1,
    pets_allowed: false,
    photos: [],
    amenity_ids: [],
    price_per_night: 10000, // cents
    cleaning_fee: 0,
    min_nights: 1,
    max_nights: 30,
  });

  const [photoUrl, setPhotoUrl] = useState('');

  const updateForm = (key: keyof CreateListingBody, value: any) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  const handleNext = () => setStep((s) => s + 1);
  const handleBack = () => setStep((s) => s - 1);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const listing = await host.createListing(formData as CreateListingBody);
      addToast({ message: 'Listing created successfully!' });
      router.push(`/rooms/${listing.id}`);
    } catch (err: any) {
      addToast({ message: err.message || 'Failed to create listing', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  if (!metaData) return <div className="p-10 animate-pulse bg-surface h-32 max-w-2xl mx-auto mt-10 rounded-card" />;

  const isStep1Valid = formData.title && formData.description && formData.category && formData.property_type && formData.room_type;
  const isStep2Valid = formData.address && formData.city && formData.country;
  const isStep3Valid = formData.max_guests! > 0 && formData.bedrooms! > 0 && formData.beds! > 0 && formData.baths! > 0;
  const isStep4Valid = formData.price_per_night! > 0;
  const isStep5Valid = formData.photos && formData.photos.length > 0;

  return (
    <div className="max-w-2xl mx-auto px-6 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text mb-2">Create a new listing</h1>
        <p className="text-text-muted">Step {step} of 5</p>
        <div className="w-full bg-border h-2 rounded-full mt-4 overflow-hidden">
          <div className="bg-brand h-full transition-all duration-300" style={{ width: `${(step / 5) * 100}%` }} />
        </div>
      </div>

      <div className="bg-bg border border-border rounded-card p-6 shadow-sm">
        {step === 1 && (
          <div className="flex flex-col gap-6">
            <h2 className="text-xl font-semibold">Basic Information</h2>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-semibold">Title</label>
              <input
                type="text"
                placeholder="Cozy cabin in the woods..."
                className="input-field"
                value={formData.title}
                onChange={(e) => updateForm('title', e.target.value)}
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-semibold">Description</label>
              <textarea
                rows={4}
                placeholder="Tell guests what makes your place special."
                className="input-field"
                value={formData.description}
                onChange={(e) => updateForm('description', e.target.value)}
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-semibold">Category</label>
              <select className="input-field" value={formData.category} onChange={(e) => updateForm('category', e.target.value)}>
                <option value="">Select a category</option>
                {metaData.categories.map((c) => (
                  <option key={c.slug} value={c.slug}>{c.label}</option>
                ))}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-2">
                <label className="text-sm font-semibold">Property Type</label>
                <select className="input-field" value={formData.property_type} onChange={(e) => updateForm('property_type', e.target.value)}>
                  <option value="House">House</option>
                  <option value="Apartment">Apartment</option>
                  <option value="Cabin">Cabin</option>
                  <option value="Villa">Villa</option>
                </select>
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-sm font-semibold">Room Type</label>
                <select className="input-field" value={formData.room_type} onChange={(e) => updateForm('room_type', e.target.value)}>
                  <option value="Entire home/apt">Entire home/apt</option>
                  <option value="Private room">Private room</option>
                  <option value="Shared room">Shared room</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="flex flex-col gap-6">
            <h2 className="text-xl font-semibold">Location</h2>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-semibold">Street Address</label>
              <input type="text" className="input-field" value={formData.address} onChange={(e) => updateForm('address', e.target.value)} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-2">
                <label className="text-sm font-semibold">City</label>
                <input type="text" className="input-field" value={formData.city} onChange={(e) => updateForm('city', e.target.value)} />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-sm font-semibold">State / Province</label>
                <input type="text" className="input-field" value={formData.state} onChange={(e) => updateForm('state', e.target.value)} />
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-semibold">Country</label>
              <input type="text" className="input-field" value={formData.country} onChange={(e) => updateForm('country', e.target.value)} />
            </div>
            <p className="text-xs text-text-muted">Lat/Lng will be geocoded automatically (mocked for now).</p>
          </div>
        )}

        {step === 3 && (
          <div className="flex flex-col gap-6">
            <h2 className="text-xl font-semibold">Details & Amenities</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-2">
                <label className="text-sm font-semibold">Max Guests</label>
                <input type="number" min={1} className="input-field" value={formData.max_guests} onChange={(e) => updateForm('max_guests', Number(e.target.value))} />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-sm font-semibold">Bedrooms</label>
                <input type="number" min={1} className="input-field" value={formData.bedrooms} onChange={(e) => updateForm('bedrooms', Number(e.target.value))} />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-sm font-semibold">Beds</label>
                <input type="number" min={1} className="input-field" value={formData.beds} onChange={(e) => updateForm('beds', Number(e.target.value))} />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-sm font-semibold">Baths</label>
                <input type="number" min={1} className="input-field" value={formData.baths} onChange={(e) => updateForm('baths', Number(e.target.value))} />
              </div>
            </div>
            <label className="flex items-center gap-2 mt-2">
              <input type="checkbox" checked={formData.pets_allowed} onChange={(e) => updateForm('pets_allowed', e.target.checked)} />
              <span className="text-sm font-semibold">Pets allowed</span>
            </label>

            <div className="mt-4">
              <label className="text-sm font-semibold mb-2 block">Amenities</label>
              <div className="grid grid-cols-2 gap-2 h-48 overflow-y-auto p-2 border border-border rounded">
                {metaData.amenities.map((a) => (
                  <label key={a.id} className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={formData.amenity_ids?.includes(a.id)}
                      onChange={(e) => {
                        const ids = new Set(formData.amenity_ids);
                        if (e.target.checked) ids.add(a.id);
                        else ids.delete(a.id);
                        updateForm('amenity_ids', Array.from(ids));
                      }}
                    />
                    {a.name}
                  </label>
                ))}
              </div>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="flex flex-col gap-6">
            <h2 className="text-xl font-semibold">Pricing & Policies</h2>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-semibold">Price per night ($)</label>
              <input
                type="number"
                min={10}
                className="input-field"
                value={(formData.price_per_night || 0) / 100}
                onChange={(e) => updateForm('price_per_night', Number(e.target.value) * 100)}
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-semibold">Cleaning Fee ($)</label>
              <input
                type="number"
                min={0}
                className="input-field"
                value={(formData.cleaning_fee || 0) / 100}
                onChange={(e) => updateForm('cleaning_fee', Number(e.target.value) * 100)}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-2">
                <label className="text-sm font-semibold">Min Nights</label>
                <input type="number" min={1} className="input-field" value={formData.min_nights} onChange={(e) => updateForm('min_nights', Number(e.target.value))} />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-sm font-semibold">Max Nights</label>
                <input type="number" min={1} className="input-field" value={formData.max_nights} onChange={(e) => updateForm('max_nights', Number(e.target.value))} />
              </div>
            </div>
          </div>
        )}

        {step === 5 && (
          <div className="flex flex-col gap-6">
            <h2 className="text-xl font-semibold">Photos</h2>
            <p className="text-sm text-text-muted">Add at least one photo URL to publish your listing.</p>
            
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="https://example.com/photo.jpg"
                className="input-field flex-1"
                value={photoUrl}
                onChange={(e) => setPhotoUrl(e.target.value)}
              />
              <Button
                variant="secondary"
                onClick={() => {
                  if (photoUrl) {
                    updateForm('photos', [...(formData.photos || []), photoUrl]);
                    setPhotoUrl('');
                  }
                }}
              >
                Add
              </Button>
            </div>

            <div className="grid grid-cols-3 gap-2 mt-4">
              {formData.photos?.map((url, i) => (
                <div key={i} className="relative group rounded overflow-hidden aspect-video bg-surface">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={url} alt={`Photo ${i}`} className="w-full h-full object-cover" />
                  <button
                    className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={() => updateForm('photos', formData.photos?.filter((_, idx) => idx !== i))}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex justify-between items-center mt-10 pt-6 border-t border-border">
          <Button variant="secondary" onClick={handleBack} disabled={step === 1 || loading}>
            Back
          </Button>
          {step < 5 ? (
            <Button
              variant="brand"
              onClick={handleNext}
              disabled={
                (step === 1 && !isStep1Valid) ||
                (step === 2 && !isStep2Valid) ||
                (step === 3 && !isStep3Valid) ||
                (step === 4 && !isStep4Valid)
              }
            >
              Next
            </Button>
          ) : (
            <Button variant="brand" onClick={handleSubmit} loading={loading} disabled={!isStep5Valid}>
              Publish Listing
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
