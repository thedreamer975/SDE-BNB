/**
 * Formatting utilities. Money stored as integer cents (PRD D2); currency is USD.
 */

const USD = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

/**
 * Formats integer cents as a USD string, e.g. `formatMoney(14200)` → `"$142"`.
 */
export function formatMoney(cents: number): string {
  return USD.format(cents / 100);
}

/**
 * Formats a nightly rate: `formatNightly(14200)` → `"$142 / night"`.
 */
export function formatNightly(cents: number): string {
  return `${USD.format(cents / 100)} / night`;
}

/**
 * Formats a full price for N nights: `formatTotal(71000, 5)` → `"$710 for 5 nights"`.
 */
export function formatTotal(cents: number, nights: number): string {
  return `${USD.format(cents / 100)} for ${nights} night${nights === 1 ? '' : 's'}`;
}

/**
 * Formats a date string `YYYY-MM-DD` to a human-friendly string.
 * e.g. `"2026-07-08"` → `"Jul 8, 2026"`
 */
export function formatDate(dateStr: string): string {
  const [year, month, day] = dateStr.split('-').map(Number);
  const d = new Date(year, month - 1, day);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

/**
 * Short date format: `"Jul 8"`.
 */
export function formatDateShort(dateStr: string): string {
  const [year, month, day] = dateStr.split('-').map(Number);
  const d = new Date(year, month - 1, day);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

/**
 * Format a date range for display: `"Jul 8 – 13, 2026"` or `"Jul 8 – Aug 2, 2026"`.
 */
export function formatDateRange(checkIn: string, checkOut: string): string {
  const [y1, m1, d1] = checkIn.split('-').map(Number);
  const [y2, m2, d2] = checkOut.split('-').map(Number);
  const inDate = new Date(y1, m1 - 1, d1);
  const outDate = new Date(y2, m2 - 1, d2);

  const month1 = inDate.toLocaleDateString('en-US', { month: 'short' });
  const month2 = outDate.toLocaleDateString('en-US', { month: 'short' });

  if (m1 === m2 && y1 === y2) {
    return `${month1} ${d1} – ${d2}, ${y1}`;
  }
  if (y1 === y2) {
    return `${month1} ${d1} – ${month2} ${d2}, ${y1}`;
  }
  return `${month1} ${d1}, ${y1} – ${month2} ${d2}, ${y2}`;
}

/**
 * Count the number of nights between two date strings.
 */
export function countNights(checkIn: string, checkOut: string): number {
  const [y1, m1, d1] = checkIn.split('-').map(Number);
  const [y2, m2, d2] = checkOut.split('-').map(Number);
  const ms = new Date(y2, m2 - 1, d2).getTime() - new Date(y1, m1 - 1, d1).getTime();
  return Math.round(ms / 86_400_000);
}

/**
 * Format an ISO datetime string as `"Oct 7, 2026"`.
 */
export function formatIsoDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

/**
 * Format a rating number: `"4.92"` or `""` if 0 / undefined.
 */
export function formatRating(avg: number, count: number): string {
  if (!count) return 'New';
  return avg.toFixed(2).replace(/\.?0+$/, '');
}
