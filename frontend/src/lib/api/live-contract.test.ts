/**
 * Contract test against a *running* FastAPI backend.
 *
 * Skipped unless EMC_LIVE_API=1, so normal runs stay offline and deterministic.
 * It deliberately never calls POST /api/chat: that would spend Gemini quota.
 * Everything it does exercise is validated with the same Zod schemas the
 * application uses, so a backend contract drift fails here first.
 *
 *   EMC_LIVE_API=1 EMC_API_URL=http://127.0.0.1:8000 npx vitest run src/lib/api/live-contract.test.ts
 */
import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import { server } from '@/mocks/server';
import {
  chatHistorySchema,
  errorResponseSchema,
  healthResponseSchema,
  sessionResponseSchema,
} from './schemas';

const live = process.env.EMC_LIVE_API === '1';
const baseUrl = process.env.EMC_API_URL ?? 'http://127.0.0.1:8000';

describe.skipIf(!live)('live backend contract', () => {
  // Let real requests through: MSW otherwise intercepts everything.
  beforeAll(() => server.close());
  afterAll(() => server.listen({ onUnhandledRequest: 'error' }));

  it('GET /api/health matches the health schema', async () => {
    const response = await fetch(`${baseUrl}/api/health`);
    expect(response.status).toBe(200);

    const parsed = healthResponseSchema.safeParse(await response.json());
    expect(parsed.success, JSON.stringify(parsed.error?.issues)).toBe(true);
    if (parsed.success) {
      expect(['healthy', 'degraded']).toContain(parsed.data.status);
    }
  });

  it('POST /api/chat/session creates a session matching the schema', async () => {
    const response = await fetch(`${baseUrl}/api/chat/session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ langue: 'fr' }),
    });
    expect(response.status).toBe(200);

    const parsed = sessionResponseSchema.safeParse(await response.json());
    expect(parsed.success, JSON.stringify(parsed.error?.issues)).toBe(true);
  });

  it('GET /api/chat/history returns the history schema for a fresh session', async () => {
    const created = await fetch(`${baseUrl}/api/chat/session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ langue: 'fr' }),
    });
    const session = sessionResponseSchema.parse(await created.json());

    const response = await fetch(`${baseUrl}/api/chat/history/${session.session_id}`);
    expect(response.status).toBe(200);

    const parsed = chatHistorySchema.safeParse(await response.json());
    expect(parsed.success, JSON.stringify(parsed.error?.issues)).toBe(true);
    if (parsed.success) expect(parsed.data.messages).toEqual([]);
  });

  it('GET /api/chat/history returns 404 with an error envelope for an unknown session', async () => {
    const response = await fetch(`${baseUrl}/api/chat/history/does-not-exist`);
    expect(response.status).toBe(404);
    expect(errorResponseSchema.safeParse(await response.json()).success).toBe(true);
  });

  it('POST /api/chat/feedback rejects an unknown session with 404', async () => {
    const response = await fetch(`${baseUrl}/api/chat/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: 'does-not-exist',
        message_id: 'msg-does-not-exist',
        rating: 5,
      }),
    });
    expect(response.status).toBe(404);
  });

  it('POST /api/chat rejects an over-long message with 422 (validation, no LLM call)', async () => {
    const response = await fetch(`${baseUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'x'.repeat(2001) }),
    });
    // Pydantic rejects it before any RAG or Gemini work happens.
    expect(response.status).toBe(422);
  });

  it('the CORS policy allows the dev frontend origin', async () => {
    const response = await fetch(`${baseUrl}/api/health`, {
      headers: { Origin: 'http://localhost:5173' },
    });
    expect(response.headers.get('access-control-allow-origin')).toBe('http://localhost:5173');
  });
});
