/**
 * Deterministic API stubbing for end-to-end runs.
 *
 * Every backend call is intercepted at the network layer with Playwright's
 * routing, so the suite spends no Gemini quota, needs no running FastAPI
 * process, and no mock code ever ships in the application bundle.
 */
import type { Page, Route } from '@playwright/test';

export const SESSION_ID = '550e8400-e29b-41d4-a716-446655440000';

export const healthyHealth = {
  status: 'healthy',
  version: '1.0.0',
  rag_status: 'healthy',
  llm_status: 'configured',
  active_sessions: 1,
  uptime_seconds: 42,
};

export const degradedHealth = {
  ...healthyHealth,
  status: 'degraded',
  rag_status: 'empty',
  llm_status: 'unconfigured',
};

export const frenchAnswer = {
  answer:
    "Vous n'êtes pas responsable de ce qui vous arrive.\n\n" +
    '- Conservez les preuves (captures d’écran).\n' +
    '- Signalez le compte sur le réseau social.\n',
  sources: [
    { path: 'fiches_pratiques/cyberharcelement.md', categorie: 'fiches_pratiques', score: 0.82 },
  ],
  langue: 'fr',
  is_darija: false,
  is_urgent: false,
  user_profile: 'victim',
  session_id: SESSION_ID,
  message_id: 'msg-e2e-0001',
  timestamp: '2026-08-24T10:00:00.000000',
};

export const urgentAnswer = {
  ...frenchAnswer,
  answer:
    'Si vous etes en danger immediat, appelez les autorites tout de suite :\n' +
    '- Police : 19 (en ville)\n' +
    '- Gendarmerie Royale : 177 (en zone rurale)\n' +
    '- Protection Civile : 15 (urgence medicale)\n' +
    '- ONDE : 2511 (si la victime est un enfant)\n',
  sources: [],
  is_urgent: true,
  message_id: 'msg-e2e-urgent',
};

interface MockOptions {
  health?: Record<string, unknown>;
  chatAnswer?: Record<string, unknown>;
  chatStatus?: number;
  chatDelayMs?: number;
}

function json(route: Route, body: unknown, status = 200) {
  return route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  });
}

export async function mockApi(page: Page, options: MockOptions = {}): Promise<void> {
  const {
    health = healthyHealth,
    chatAnswer = frenchAnswer,
    chatStatus = 200,
    chatDelayMs = 0,
  } = options;

  // Playwright evaluates routes in reverse registration order, so the catch-all
  // is registered first and the specific handlers below take precedence over it.
  await page.route('**/api/**', (route) => route.abort());

  await page.route('**/api/health', (route) => json(route, health));

  await page.route('**/api/chat/history/**', (route) =>
    json(route, { session_id: SESSION_ID, messages: [], total_messages: 0 }),
  );

  await page.route('**/api/chat/feedback', (route) =>
    json(route, { status: 'received', message: 'Merci pour votre retour.' }),
  );

  await page.route('**/api/chat', async (route) => {
    if (chatDelayMs > 0) await new Promise((resolve) => setTimeout(resolve, chatDelayMs));
    if (chatStatus !== 200) {
      return json(route, { detail: 'Erreur', error_code: 'TEST' }, chatStatus);
    }
    return json(route, chatAnswer);
  });
}
