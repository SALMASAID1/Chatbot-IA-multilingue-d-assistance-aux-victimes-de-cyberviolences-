import { describe, expect, it } from 'vitest';
import { formatTime, parseBackendDate } from './datetime';

describe('backend timestamp parsing', () => {
  it('reads naive FastAPI timestamps as UTC, not local time', () => {
    // datetime.utcnow() serialises without a timezone designator.
    const parsed = parseBackendDate('2026-08-24T10:00:00.000000');
    expect(parsed?.toISOString()).toBe('2026-08-24T10:00:00.000Z');
  });

  it('respects an explicit timezone when present', () => {
    expect(parseBackendDate('2026-08-24T10:00:00Z')?.toISOString()).toBe(
      '2026-08-24T10:00:00.000Z',
    );
    expect(parseBackendDate('2026-08-24T11:00:00+01:00')?.toISOString()).toBe(
      '2026-08-24T10:00:00.000Z',
    );
  });

  it('returns null for missing or unparsable values', () => {
    expect(parseBackendDate(null)).toBeNull();
    expect(parseBackendDate('not-a-date')).toBeNull();
    expect(formatTime(undefined, 'fr')).toBe('');
  });

  it('formats times with Latin digits so they stay readable in RTL', () => {
    const formatted = formatTime('2026-08-24T10:05:00.000000', 'ar');
    expect(formatted).toMatch(/\d/);
    expect(formatted).not.toMatch(/[٠-٩]/);
  });
});
