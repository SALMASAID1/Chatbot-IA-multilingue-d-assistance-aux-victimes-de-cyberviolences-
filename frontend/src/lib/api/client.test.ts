import { describe, expect, it, vi } from 'vitest';
import { http, HttpResponse, delay } from 'msw';
import { z } from 'zod';
import { server } from '@/mocks/server';
import { request } from './client';
import { ApiError } from './errors';
import { getHealth } from './endpoints';

const schema = z.object({ ok: z.boolean() });

describe('API client error mapping', () => {
  it.each([
    [404, 'notFound'],
    [422, 'validation'],
    [429, 'rateLimited'],
    [503, 'unavailable'],
    [500, 'server'],
  ])('maps HTTP %i to "%s"', async (status, kind) => {
    server.use(http.get('*/api/probe', () => new HttpResponse(null, { status })));
    await expect(request('/api/probe', { schema })).rejects.toMatchObject({ kind });
  });

  it('rejects payloads that do not match the schema', async () => {
    server.use(http.get('*/api/probe', () => HttpResponse.json({ ok: 'yes' })));
    await expect(request('/api/probe', { schema })).rejects.toMatchObject({ kind: 'malformed' });
  });

  it('reports a timeout when the backend is too slow', async () => {
    server.use(
      http.get('*/api/probe', async () => {
        await delay(200);
        return HttpResponse.json({ ok: true });
      }),
    );
    await expect(request('/api/probe', { schema, timeoutMs: 20 })).rejects.toMatchObject({
      kind: 'timeout',
    });
  });

  it('distinguishes caller cancellation from a timeout', async () => {
    server.use(
      http.get('*/api/probe', async () => {
        await delay(200);
        return HttpResponse.json({ ok: true });
      }),
    );
    const controller = new AbortController();
    const pending = request('/api/probe', { schema, signal: controller.signal });
    controller.abort();
    await expect(pending).rejects.toMatchObject({ kind: 'aborted' });
  });

  it('fails fast when the browser reports being offline', async () => {
    const spy = vi.spyOn(navigator, 'onLine', 'get').mockReturnValue(false);
    await expect(getHealth()).rejects.toMatchObject({ kind: 'offline' });
    spy.mockRestore();
  });

  it('surfaces the backend error_code when present', async () => {
    server.use(
      http.get('*/api/probe', () =>
        HttpResponse.json(
          { detail: 'Trop de requêtes.', error_code: 'RATE_LIMIT_EXCEEDED' },
          { status: 429 },
        ),
      ),
    );
    await expect(request('/api/probe', { schema })).rejects.toMatchObject({
      kind: 'rateLimited',
      code: 'RATE_LIMIT_EXCEEDED',
    });
  });

  it('never retries: one call means one request', async () => {
    const seen = vi.fn();
    server.use(
      http.post('*/api/chat', () => {
        seen();
        return new HttpResponse(null, { status: 500 });
      }),
    );
    await expect(
      request('/api/chat', { method: 'POST', body: { message: 'hi' }, schema }),
    ).rejects.toBeInstanceOf(ApiError);
    expect(seen).toHaveBeenCalledTimes(1);
  });
});

describe('health endpoint validation', () => {
  it('accepts a payload that omits defaulted fields', async () => {
    server.use(
      http.get('*/api/health', () =>
        HttpResponse.json({ status: 'healthy', version: '1.0.0', rag_status: 'healthy' }),
      ),
    );
    const health = await getHealth();
    expect(health.llm_status).toBe('unknown');
    expect(health.active_sessions).toBe(0);
  });
});
