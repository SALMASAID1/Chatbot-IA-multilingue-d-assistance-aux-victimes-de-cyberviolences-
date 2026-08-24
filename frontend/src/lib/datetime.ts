/**
 * The backend builds timestamps with `datetime.utcnow()`, which serialises to a
 * naive ISO string ("2026-08-24T18:30:00.123456") with no timezone designator.
 * `new Date()` would read that as *local* time and shift it by the UTC offset,
 * so we append "Z" when no offset is present.
 */
export function parseBackendDate(value: string | undefined | null): Date | null {
  if (!value) return null;
  const hasZone = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(value);
  const normalised = hasZone ? value : `${value}Z`;
  const date = new Date(normalised);
  return Number.isNaN(date.getTime()) ? null : date;
}

/** Short, locale-aware clock label. Latin digits keep timestamps readable in RTL. */
export function formatTime(value: string | undefined | null, locale: string): string {
  const date = parseBackendDate(value);
  if (!date) return '';
  try {
    return new Intl.DateTimeFormat(locale === 'ary' ? 'ar-MA' : locale, {
      hour: '2-digit',
      minute: '2-digit',
      numberingSystem: 'latn',
    }).format(date);
  } catch {
    return '';
  }
}
