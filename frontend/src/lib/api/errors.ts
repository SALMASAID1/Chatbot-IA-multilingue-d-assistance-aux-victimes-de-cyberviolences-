/**
 * Error taxonomy shared by the API layer and the UI.
 * Every kind maps to a localized message key: `errors.<kind>`.
 */
export type ApiErrorKind =
  | 'offline'
  | 'timeout'
  | 'aborted'
  | 'notFound'
  | 'validation'
  | 'rateLimited'
  | 'unavailable'
  | 'server'
  | 'malformed'
  | 'network'
  | 'unknown';

export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status?: number;
  /** Machine-readable code from the backend (e.g. RATE_LIMIT_EXCEEDED). */
  readonly code?: string;

  constructor(
    kind: ApiErrorKind,
    options: { status?: number; code?: string; message?: string } = {},
  ) {
    super(options.message ?? kind);
    this.name = 'ApiError';
    this.kind = kind;
    this.status = options.status;
    this.code = options.code;
  }

  /** True when the session the request referenced no longer exists. */
  get isMissingSession(): boolean {
    return this.kind === 'notFound';
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

export function toApiError(error: unknown): ApiError {
  if (isApiError(error)) return error;
  if (error instanceof DOMException && error.name === 'AbortError') {
    return new ApiError('aborted');
  }
  if (error instanceof TypeError) {
    // fetch() rejects with TypeError on DNS/connection failures.
    return new ApiError(
      typeof navigator !== 'undefined' && !navigator.onLine ? 'offline' : 'network',
    );
  }
  return new ApiError('unknown');
}

/** Kinds where showing a "try again" affordance makes sense. */
export function isRetryable(kind: ApiErrorKind): boolean {
  return kind !== 'validation' && kind !== 'aborted';
}
