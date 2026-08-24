import { http, HttpResponse } from 'msw';
import { SESSION_ID, frenchAnswer, healthyHealth } from './fixtures';

/** Default happy-path handlers; individual tests override what they need. */
export const handlers = [
  http.get('*/api/health', () => HttpResponse.json(healthyHealth)),

  http.post('*/api/chat/session', () =>
    HttpResponse.json({
      session_id: SESSION_ID,
      created_at: '2026-08-24T09:59:00.000000',
      langue: 'fr',
    }),
  ),

  http.post('*/api/chat', () => HttpResponse.json(frenchAnswer)),

  http.get('*/api/chat/history/:sessionId', ({ params }) =>
    HttpResponse.json({
      session_id: params.sessionId as string,
      messages: [],
      total_messages: 0,
    }),
  ),

  http.post('*/api/chat/feedback', () =>
    HttpResponse.json({ status: 'received', message: 'Merci pour votre retour.' }),
  ),
];
