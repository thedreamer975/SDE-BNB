/**
 * Typed API client — all calls go through `/api/*` (same-origin rewrite).
 * Error shape mirrors the backend standard envelope:
 * { code, message, field_errors?, request_id }
 */

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly fieldErrors?: Record<string, string[]>,
    public readonly requestId?: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', ...(options?.headers ?? {}) },
    ...options,
  });

  if (res.status === 204) return undefined as T;

  let body: unknown;
  try {
    body = await res.json();
  } catch {
    throw new ApiError(res.status, 'UNKNOWN', `HTTP ${res.status}`);
  }

  if (!res.ok) {
    const err = body as {
      code?: string;
      message?: string;
      field_errors?: Record<string, string[]>;
      request_id?: string;
    };
    throw new ApiError(
      res.status,
      err.code ?? 'UNKNOWN',
      err.message ?? `HTTP ${res.status}`,
      err.field_errors,
      err.request_id,
    );
  }

  return body as T;
}

function get<T>(path: string, init?: RequestInit) {
  return request<T>(path, { method: 'GET', ...init });
}

function post<T>(path: string, body?: unknown, init?: RequestInit) {
  return request<T>(path, {
    method: 'POST',
    body: body !== undefined ? JSON.stringify(body) : undefined,
    ...init,
  });
}

function patch<T>(path: string, body?: unknown, init?: RequestInit) {
  return request<T>(path, {
    method: 'PATCH',
    body: body !== undefined ? JSON.stringify(body) : undefined,
    ...init,
  });
}

function put<T>(path: string, body?: unknown, init?: RequestInit) {
  return request<T>(path, {
    method: 'PUT',
    body: body !== undefined ? JSON.stringify(body) : undefined,
    ...init,
  });
}

function del<T>(path: string, init?: RequestInit) {
  return request<T>(path, { method: 'DELETE', ...init });
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export interface UserResponse {
  id: string;
  email: string;
  name: string;
  role: 'guest' | 'host';
  avatar_url: string | null;
  bio: string | null;
  joined_year: number;
  listing_count: number;
  is_superhost: boolean;
  created_at: string;
}

export const auth = {
  me: () => get<UserResponse>('/auth/me'),
  register: (body: { name: string; email: string; password: string }) =>
    post<UserResponse>('/auth/register', body),
  login: (body: { email: string; password: string }) =>
    post<UserResponse>('/auth/login', body),
  logout: () => post<void>('/auth/logout'),
};

export const users = {
  updateMe: (body: { name?: string; bio?: string; avatar_url?: string }) =>
    patch<UserResponse>('/users/me', body),
  becomeHost: () => post<UserResponse>('/users/me/become-host'),
};

// ─── Meta ─────────────────────────────────────────────────────────────────────

export interface MetaCategory {
  slug: string;
  label: string;
  icon: string;
}

export interface MetaAmenity {
  id: number;
  name: string;
  icon: string;
  category: string;
}

export interface MetaResponse {
  categories: MetaCategory[];
  amenities: MetaAmenity[];
  limits: Record<string, number>;
  today: string;
}

export const meta = {
  get: () => get<MetaResponse>('/meta'),
};

// ─── Listings ─────────────────────────────────────────────────────────────────

export interface ListingCard {
  id: string;
  title: string;
  city: string;
  country: string;
  state: string | null;
  property_type: string;
  room_type: string;
  beds: number;
  bedrooms: number;
  baths: number;
  max_guests: number;
  price_per_night: number;
  rating_avg: number;
  rating_count: number;
  is_superhost: boolean;
  is_guest_favorite: boolean;
  photos: string[];
  is_saved: boolean;
}

export interface ListingDetail extends ListingCard {
  description: string;
  address: string;
  latitude: number;
  longitude: number;
  pets_allowed: boolean;
  cleaning_fee: number;
  service_fee: number;
  min_nights: number;
  max_nights: number;
  check_in_time: string;
  check_out_time: string;
  house_rules: string | null;
  amenities: MetaAmenity[];
  host: UserResponse;
  created_year: number;
}

export interface SearchParams {
  location?: string;
  check_in?: string;
  check_out?: string;
  adults?: number;
  children?: number;
  infants?: number;
  pets?: number;
  category?: string;
  min_price?: number;
  max_price?: number;
  room_type?: string;
  property_type?: string;
  bedrooms?: number;
  beds?: number;
  baths?: number;
  amenities?: number[];
  superhost?: boolean;
  guest_favorite?: boolean;
  page?: number;
  page_size?: number;
}

function buildQuery(params: Record<string, unknown>): string {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === '') continue;
    if (Array.isArray(v)) {
      v.forEach((item) => q.append(k, String(item)));
    } else {
      q.set(k, String(v));
    }
  }
  const s = q.toString();
  return s ? `?${s}` : '';
}

export interface PaginatedListings {
  items: ListingCard[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface AvailabilityResponse {
  booked_ranges: { start: string; end: string }[];
  min_nights: number;
  max_nights: number;
}

export interface Review {
  id: string;
  guest_name: string;
  guest_avatar: string | null;
  guest_joined_year: number;
  rating: number;
  comment: string;
  created_at: string;
}

export interface ReviewsResponse {
  items: Review[];
  total: number;
  avg: number;
}

export interface Suggestion {
  label: string;
  description: string | null;
  type: 'destination' | 'entry_point';
}

export interface FacetsResponse {
  price_histogram: { min: number; max: number; count: number }[];
  min_price: number;
  max_price: number;
}

export const listings = {
  search: (params: SearchParams) =>
    get<PaginatedListings>(`/listings${buildQuery(params as Record<string, unknown>)}`),
  count: (params: SearchParams) =>
    get<{ count: number }>(`/listings/count${buildQuery(params as Record<string, unknown>)}`),
  facets: (params?: SearchParams) =>
    get<FacetsResponse>(
      `/listings/facets${params ? buildQuery(params as Record<string, unknown>) : ''}`,
    ),
  get: (id: string) => get<ListingDetail>(`/listings/${id}`),
  availability: (id: string) => get<AvailabilityResponse>(`/listings/${id}/availability`),
  reviews: (id: string, page = 1, pageSize = 6) =>
    get<ReviewsResponse>(`/listings/${id}/reviews?page=${page}&page_size=${pageSize}`),
  suggestions: (q: string) =>
    get<Suggestion[]>(`/search/suggestions?q=${encodeURIComponent(q)}`),
};

// ─── Wishlist ──────────────────────────────────────────────────────────────────

export const wishlist = {
  getAll: () => get<ListingCard[]>('/wishlist'),
  getIds: () => get<string[]>('/wishlist/ids'),
  save: (listingId: string) => put<void>(`/wishlist/${listingId}`),
  remove: (listingId: string) => del<void>(`/wishlist/${listingId}`),
};

// ─── Bookings ─────────────────────────────────────────────────────────────────

export interface BookingQuote {
  nightly_total: number;
  nights: number;
  cleaning_fee: number;
  service_fee: number;
  total: number;
  price_per_night: number;
}

export interface Booking {
  id: string;
  listing_id: string;
  listing_title: string;
  listing_city: string;
  listing_country: string;
  listing_photo: string | null;
  check_in: string;
  check_out: string;
  adults: number;
  children: number;
  infants: number;
  pets: number;
  total_price: number;
  status: 'confirmed' | 'cancelled' | 'completed';
  confirmation_code: string;
  created_at: string;
}

export interface CreateBookingBody {
  listing_id: string;
  check_in: string;
  check_out: string;
  adults: number;
  children: number;
  infants: number;
  pets: number;
  card_token: string;
}

export const bookings = {
  quote: (params: {
    listing_id: string;
    check_in: string;
    check_out: string;
    adults: number;
    children: number;
    infants: number;
    pets: number;
  }) => get<BookingQuote>(`/bookings/quote${buildQuery(params as Record<string, unknown>)}`),
  create: (body: CreateBookingBody) => post<Booking>('/bookings', body),
  getAll: () => get<Booking[]>('/bookings'),
  get: (id: string) => get<Booking>(`/bookings/${id}`),
  cancel: (id: string) => post<Booking>(`/bookings/${id}/cancel`),
};

// ─── Host ─────────────────────────────────────────────────────────────────────

export interface HostListing {
  id: string;
  title: string;
  city: string;
  country: string;
  price_per_night: number;
  rating_avg: number;
  rating_count: number;
  photos: string[];
  upcoming_bookings: number;
  is_active: boolean;
}

export interface CreateListingBody {
  title: string;
  description: string;
  category: string;
  property_type: string;
  room_type: string;
  address: string;
  city: string;
  state?: string;
  country: string;
  latitude: number;
  longitude: number;
  max_guests: number;
  bedrooms: number;
  beds: number;
  baths: number;
  pets_allowed: boolean;
  photos: string[];
  amenity_ids: number[];
  price_per_night: number;
  cleaning_fee: number;
  min_nights?: number;
  max_nights?: number;
  check_in_time?: string;
  check_out_time?: string;
  house_rules?: string;
}

export const host = {
  listings: () => get<HostListing[]>('/host/listings'),
  createListing: (body: CreateListingBody) => post<ListingDetail>('/host/listings', body),
  updateListing: (id: string, body: Partial<CreateListingBody>) =>
    patch<ListingDetail>(`/host/listings/${id}`, body),
  deleteListing: (id: string) => del<void>(`/host/listings/${id}`),
  reservations: () => get<Booking[]>('/host/reservations'),
  dashboard: () =>
    get<{
      checking_out: number;
      currently_hosting: number;
      arriving_soon: number;
      upcoming: number;
      total_listings: number;
      upcoming_bookings: number;
      revenue_30d: number;
      avg_rating: number;
    }>('/host/dashboard'),
};

// ─── Reviews ──────────────────────────────────────────────────────────────────

export const reviews = {
  create: (bookingId: string, body: { rating: number; comment: string }) =>
    post<Review>(`/bookings/${bookingId}/review`, body),
};
