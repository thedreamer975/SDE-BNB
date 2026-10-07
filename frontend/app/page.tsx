export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 text-center">
      <div className="max-w-xl space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 text-sm font-semibold text-brand bg-brand/10 rounded-full">
          Airbnb Clone
        </div>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          Welcome to Vacation Rentals
        </h1>
        <p className="text-text-muted text-base">
          Scaffold initialized. Explore categories, listings, search, and bookings coming up.
        </p>
      </div>
    </main>
  );
}
