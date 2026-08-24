/**
 * Minimal typed fetch wrapper.
 *
 * Responsibilities: base URL resolution, JSON encoding, timeouts layered on top
 * of a caller-supplied AbortSignal, HTTP status -> ApiError mapping, and Zod
 * validation of every response body.
 *
 * It deliberately does NOT retry: POST /api/chat is not idempotent and a retry
 * could duplicate a user's message (and burn LLM quota).
 */
import type { z } from 'zod';
import { ApiError, toApiError } from './errors';
import { errorResponseSchema } from './schemas';
import { logDebug } from '@/lib/logger';

const DEFAULT_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS ?? 45_000);
const HEALTH_TIMEOUT_MS = 8_000;

/** Empty base URL => same-origin "/api/..." (Vite proxy in dev, reverse proxy in prod). */
export function getApiBaseUrl(): string {
  const raw = (import.meta.env.VITE_API_BASE_URL ?? '').trim();
  return raw.replace(/\/+$/, '');
}

export function buildUrl(path: string): string {
  const base = getApiBaseUrl();
  const suffix = path.startsWith('/') ? path : `/${path}`;
  return `${base}${suffix}`;
}

function mapStatus(status: number, code?: string): ApiError {
  switch (status) {
    case 404:
      return new ApiError('notFound', { status, code });
    case 422:
      return new ApiError('validation', { status, code });
    case 429:
      return new ApiError('rateLimited', { status, code });
    case 503:
      return new ApiError('unavailable', { status, code });
    default:
      if (status >= 500) return new ApiError('server', { status, code });
      return new ApiError('unknown', { status, code });
  }
}

async function readErrorCode(response: Response): Promise<string | undefined> {
  try {
    const body: unknown = await response.json();
    const parsed = errorResponseSchema.safeParse(body);
    if (parsed.success && typeof parsed.data.error_code === 'string') {
      return parsed.data.error_code;
    }
  } catch {
    /* body was empty or not JSON — the status code is enough */
  }
  return undefined;
}

export interface RequestOptions<TSchema extends z.ZodType> {
  method?: 'GET' | 'POST' | 'DELETE';
  body?: unknown;
  schema: TSchema;
  signal?: AbortSignal;
  timeoutMs?: number;
}

export async function request<TSchema extends z.ZodType>(
  path: string,
  { method = 'GET', body, schema, signal, timeoutMs = DEFAULT_TIMEOUT_MS }: RequestOptions<TSchema>,
): Promise<z.output<TSchema>> {
  if (typeof navigator !== 'undefined' && navigator.onLine === false) {
    throw new ApiError('offline');
  }

  // One controller aborts the fetch; the timeout and the caller's signal both
  // feed into it. (AbortSignal.any is not available in every runtime we test in.)
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  if (signal) {
    if (signal.aborted) {
      controller.abort();
    } else {
      signal.addEventListener('abort', () => controller.abort(), { once: true });
    }
  }

  try {
    const response = await fetch(buildUrl(path), {
      method,
      headers: {
        Accept: 'application/json',
        ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: controller.signal,
      // No cookies are used; the backend is stateless per session id.
      credentials: 'omit',
      cache: 'no-store',
    });

    if (!response.ok) {
      throw mapStatus(response.status, await readErrorCode(response));
    }

    const json: unknown = await response.json();
    const parsed = schema.safeParse(json);
    if (!parsed.success) {
      // Never log the payload itself: it can contain the user's message.
      logDebug('Response failed schema validation', { path, issues: parsed.error.issues.length });
      throw new ApiError('malformed', { status: response.status });
    }
    return parsed.data;
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      // Distinguish "we timed out" from "the user cancelled".
      throw new ApiError(signal?.aborted ? 'aborted' : 'timeout');
    }
    throw toApiError(error);
  } finally {
    clearTimeout(timer);
  }
}

export const timeouts = {
  default: DEFAULT_TIMEOUT_MS,
  health: HEALTH_TIMEOUT_MS,
};
