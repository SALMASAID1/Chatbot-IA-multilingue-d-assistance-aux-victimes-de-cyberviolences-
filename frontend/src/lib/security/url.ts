/**
 * URL scheme allow-list. Only these schemes may ever be opened from
 * assistant-rendered content or resource lists.
 */
const ALLOWED_PROTOCOLS = new Set(['http:', 'https:', 'mailto:', 'tel:']);

export function isSafeUrl(value: string | undefined | null): boolean {
  if (!value) return false;
  const trimmed = value.trim();
  if (trimmed === '') return false;
  try {
    // A base is required so protocol-relative and relative values resolve.
    const url = new URL(trimmed, 'https://emc-helpline.invalid');
    return ALLOWED_PROTOCOLS.has(url.protocol);
  } catch {
    return false;
  }
}

/** Returns the href only when the scheme is allowed, otherwise undefined. */
export function safeHref(value: string | undefined | null): string | undefined {
  return isSafeUrl(value) ? (value as string).trim() : undefined;
}

export function isExternalHttpUrl(value: string): boolean {
  return /^https?:\/\//i.test(value.trim());
}

/** Digits-only tel: target — never dialled automatically, only linked. */
export function telHref(phone: string): string {
  return `tel:${phone.replace(/[^\d+]/g, '')}`;
}
