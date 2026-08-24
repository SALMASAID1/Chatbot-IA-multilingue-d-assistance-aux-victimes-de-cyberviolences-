import { describe, expect, it } from 'vitest';
import { isExternalHttpUrl, isSafeUrl, safeHref, telHref } from './url';

describe('URL scheme allow-list', () => {
  it.each([
    'https://www.cyberconfiance.ma',
    'http://example.ma/page',
    'mailto:contact@cyberconfiance.ma',
    'tel:19',
  ])('allows %s', (url) => {
    expect(isSafeUrl(url)).toBe(true);
    expect(safeHref(url)).toBe(url);
  });

  it.each([
    'javascript:alert(1)',
    'data:text/html,<script>alert(1)</script>',
    'vbscript:msgbox(1)',
    'file:///etc/passwd',
    '',
  ])('rejects %s', (url) => {
    expect(isSafeUrl(url)).toBe(false);
    expect(safeHref(url)).toBeUndefined();
  });

  it('rejects null and undefined', () => {
    expect(isSafeUrl(null)).toBe(false);
    expect(isSafeUrl(undefined)).toBe(false);
  });

  it('detects external http(s) links for rel/target handling', () => {
    expect(isExternalHttpUrl('https://evigilance.ma/fr/signaler')).toBe(true);
    expect(isExternalHttpUrl('tel:19')).toBe(false);
  });

  it('builds tel: hrefs with digits only', () => {
    expect(telHref('2511')).toBe('tel:2511');
    expect(telHref('+212 5 22 00 00 00')).toBe('tel:+212522000000');
  });
});
