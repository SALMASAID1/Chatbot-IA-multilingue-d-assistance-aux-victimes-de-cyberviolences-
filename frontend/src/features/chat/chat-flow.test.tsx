import { beforeEach, describe, expect, it, vi } from 'vitest';
import { screen, waitFor, within } from '@testing-library/react';
import { http, HttpResponse, delay } from 'msw';
import { server } from '@/mocks/server';
import { SESSION_ID, arabicAnswer, degradedHealth, frenchAnswer } from '@/mocks/fixtures';
import { renderApp, setLanguage } from '@/test/utils';

async function composer() {
  return screen.findByLabelText('Votre message');
}

/**
 * The assistant answer intentionally exists twice in the DOM: once in the
 * visible timeline and once in the sr-only polite live region. Assertions about
 * what is *displayed* are scoped to the timeline list.
 */
function timeline() {
  return within(screen.getByRole('list', { name: 'Fil de la conversation' }));
}

beforeEach(async () => {
  await setLanguage('fr');
});

describe('sending a message', () => {
  it('sends a French message and renders the answer with its sources', async () => {
    const { user } = renderApp();

    const textarea = await composer();
    await user.type(textarea, 'Je suis victime de cyberharcèlement');
    await user.click(screen.getByRole('button', { name: 'Envoyer le message' }));

    // The user's own message appears immediately (optimistic).
    expect(await screen.findByText('Je suis victime de cyberharcèlement')).toBeInTheDocument();

    expect(
      await timeline().findByText(/Vous n'êtes pas responsable de ce qui vous arrive/),
    ).toBeInTheDocument();

    // The composer is cleared and keeps focus for the next message.
    await waitFor(() => expect((textarea as HTMLTextAreaElement).value).toBe(''));
    expect(textarea).toHaveFocus();

    expect(screen.getByText('Sources consultées (2)')).toBeInTheDocument();
  });

  it('creates and stores a session id for the tab, and reuses it', async () => {
    const bodies: unknown[] = [];
    server.use(
      http.post('*/api/chat', async ({ request }) => {
        bodies.push(await request.json());
        return HttpResponse.json(frenchAnswer);
      }),
    );

    const { user } = renderApp();
    const textarea = await composer();

    await user.type(textarea, 'Premier message');
    await user.keyboard('{Enter}');
    await timeline().findByText(/Vous n'êtes pas responsable/);

    expect(window.sessionStorage.getItem('emc.session_id')).toBe(SESSION_ID);
    expect(bodies[0]).toMatchObject({ message: 'Premier message', session_id: null });

    await user.type(textarea, 'Deuxième message');
    await user.keyboard('{Enter}');

    await waitFor(() => expect(bodies).toHaveLength(2));
    expect(bodies[1]).toMatchObject({ message: 'Deuxième message', session_id: SESSION_ID });
  });

  it('shows a respectful loading state while the answer is prepared', async () => {
    server.use(
      http.post('*/api/chat', async () => {
        await delay(80);
        return HttpResponse.json(frenchAnswer);
      }),
    );

    const { user } = renderApp();
    await user.type(await composer(), 'Bonjour');
    await user.keyboard('{Enter}');

    expect(await timeline().findByText('Préparation d’une réponse…')).toBeInTheDocument();
    await timeline().findByText(/Vous n'êtes pas responsable/);
    expect(timeline().queryByText('Préparation d’une réponse…')).not.toBeInTheDocument();
  });

  it('lets the user cancel a pending request', async () => {
    server.use(
      http.post('*/api/chat', async () => {
        await delay(500);
        return HttpResponse.json(frenchAnswer);
      }),
    );

    const { user } = renderApp();
    await user.type(await composer(), 'Une question');
    await user.keyboard('{Enter}');

    const cancel = await screen.findByRole('button', { name: 'Annuler la demande' });
    await user.click(cancel);

    expect(await screen.findByText('Demande annulée.')).toBeInTheDocument();
    expect(timeline().queryByText(/Vous n'êtes pas responsable/)).not.toBeInTheDocument();
  });
});

describe('failure handling', () => {
  it('explains a 429 rate limit and offers a retry', async () => {
    let attempts = 0;
    server.use(
      http.post('*/api/chat', () => {
        attempts += 1;
        if (attempts === 1) {
          return HttpResponse.json(
            { detail: 'Trop de requêtes.', error_code: 'RATE_LIMIT_EXCEEDED' },
            { status: 429 },
          );
        }
        return HttpResponse.json(frenchAnswer);
      }),
    );

    const { user } = renderApp();
    await user.type(await composer(), 'Question');
    await user.keyboard('{Enter}');

    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent(/Trop de messages envoyés coup sur coup/);
    // The failed request must not have been retried automatically.
    expect(attempts).toBe(1);

    await user.click(within(alert).getByRole('button', { name: 'Réessayer' }));
    expect(await timeline().findByText(/Vous n'êtes pas responsable/)).toBeInTheDocument();
    expect(attempts).toBe(2);
  });

  it('reports an unavailable RAG/LLM backend (503)', async () => {
    server.use(
      http.post('*/api/chat', () =>
        HttpResponse.json({ detail: 'RAG indisponible' }, { status: 503 }),
      ),
    );

    const { user } = renderApp();
    await user.type(await composer(), 'Question');
    await user.keyboard('{Enter}');

    expect(await screen.findByRole('alert')).toHaveTextContent(
      /L’assistant est momentanément indisponible/,
    );
  });

  it('warns when the health endpoint reports a degraded service', async () => {
    server.use(http.get('*/api/health', () => HttpResponse.json(degradedHealth)));
    renderApp();

    const banner = await screen.findByRole('status');
    expect(banner).toHaveTextContent('Service partiellement disponible');
    // Emergency contacts stay reachable while the service is degraded.
    expect(
      within(banner).getByRole('button', { name: 'Voir les numéros d’urgence' }),
    ).toBeInTheDocument();
  });

  it(
    'reports an unreachable backend without hiding emergency access',
    { timeout: 15_000 },
    async () => {
      server.use(http.get('*/api/health', () => HttpResponse.error()));
      renderApp();

      // Both the header indicator and the banner report it; assert on the banner.
      const banner = await screen.findByRole('status', undefined, { timeout: 10_000 });
      expect(banner).toHaveTextContent(/Service momentanément injoignable/);
      expect(
        within(banner).getByRole('button', { name: 'Voir les numéros d’urgence' }),
      ).toBeInTheDocument();
    },
  );
});

describe('session restoration', () => {
  it('restores the conversation of an existing session', async () => {
    window.sessionStorage.setItem('emc.session_id', SESSION_ID);
    server.use(
      http.get('*/api/chat/history/:sessionId', () =>
        HttpResponse.json({
          session_id: SESSION_ID,
          messages: [
            {
              role: 'user',
              content: 'Ma question précédente',
              timestamp: '2026-08-24T09:00:00.000000',
              message_id: 'm1',
            },
            {
              role: 'assistant',
              content: 'Ma réponse précédente',
              timestamp: '2026-08-24T09:00:03.000000',
              message_id: 'm2',
            },
          ],
          total_messages: 2,
        }),
      ),
    );

    renderApp();

    const list = await screen.findByRole('list', { name: 'Fil de la conversation' });
    expect(within(list).getByText('Ma question précédente')).toBeInTheDocument();
    expect(within(list).getByText('Ma réponse précédente')).toBeInTheDocument();
    expect(screen.getByText('Conversation précédente restaurée.')).toBeInTheDocument();
  });

  it('recovers from an expired session without losing the draft', async () => {
    window.sessionStorage.setItem('emc.session_id', 'expired-session');
    server.use(
      http.get('*/api/chat/history/:sessionId', async () => {
        await delay(60);
        return HttpResponse.json({ detail: 'Session introuvable ou expirée.' }, { status: 404 });
      }),
    );

    const { user } = renderApp();
    const textarea = await composer();
    await user.type(textarea, 'Un brouillon que je ne veux pas perdre');

    expect(await screen.findByText(/Cette conversation a expiré/)).toBeInTheDocument();
    // The stale id is dropped, a new session will be created on send…
    expect(window.sessionStorage.getItem('emc.session_id')).toBeNull();
    // …and the unsent draft survives.
    expect((textarea as HTMLTextAreaElement).value).toBe('Un brouillon que je ne veux pas perdre');

    await user.keyboard('{Enter}');
    expect(await timeline().findByText(/Vous n'êtes pas responsable/)).toBeInTheDocument();
    expect(window.sessionStorage.getItem('emc.session_id')).toBe(SESSION_ID);
  });
});

describe('message validation', () => {
  it('disables sending an empty message and explains why on submit', async () => {
    const seen = vi.fn();
    server.use(
      http.post('*/api/chat', () => {
        seen();
        return HttpResponse.json(frenchAnswer);
      }),
    );

    const { user } = renderApp();
    const textarea = await composer();

    expect(screen.getByRole('button', { name: 'Envoyer le message' })).toBeDisabled();

    await user.type(textarea, '   ');
    await user.keyboard('{Enter}');

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Écrivez un message avant d’envoyer.',
    );
    expect(seen).not.toHaveBeenCalled();
  });

  it('accepts exactly 2000 characters and rejects 2001', async () => {
    const seen = vi.fn();
    server.use(
      http.post('*/api/chat', async ({ request }) => {
        const body = (await request.json()) as { message: string };
        seen(body.message.length);
        return HttpResponse.json(frenchAnswer);
      }),
    );

    const { user } = renderApp();
    const textarea = await composer();

    await user.click(textarea);
    await user.paste('x'.repeat(2001));
    // The counter warns before the user submits.
    expect(await screen.findByText(/dépasse 2000 caractères/)).toBeInTheDocument();

    await user.keyboard('{Enter}');
    expect(await screen.findByRole('alert')).toHaveTextContent(/dépasse 2000 caractères/);
    expect(seen).not.toHaveBeenCalled();

    await user.clear(textarea);
    await user.click(textarea);
    await user.paste('y'.repeat(2000));
    await user.keyboard('{Enter}');

    await waitFor(() => expect(seen).toHaveBeenCalledWith(2000));
  });

  it('inserts a newline with Shift+Enter instead of sending', async () => {
    const seen = vi.fn();
    server.use(
      http.post('*/api/chat', () => {
        seen();
        return HttpResponse.json(frenchAnswer);
      }),
    );

    const { user } = renderApp();
    const textarea = (await composer()) as HTMLTextAreaElement;

    await user.type(textarea, 'Première ligne');
    await user.keyboard('{Shift>}{Enter}{/Shift}');
    await user.type(textarea, 'Deuxième ligne');

    expect(textarea.value).toBe('Première ligne\nDeuxième ligne');
    expect(seen).not.toHaveBeenCalled();
  });
});

describe('multilingual rendering', () => {
  it('renders an Arabic answer right-to-left', async () => {
    server.use(http.post('*/api/chat', () => HttpResponse.json(arabicAnswer)));

    const { user } = renderApp();
    await user.type(await composer(), 'مرحبا');
    await user.keyboard('{Enter}');

    const answer = await timeline().findByText(/لست مسؤولا عما وقع لك/);
    const container = answer.closest('[dir]');
    expect(container).toHaveAttribute('dir', 'rtl');
    expect(container).toHaveAttribute('lang', 'ar');
  });

  it('keeps an Arabizi message left-to-right even in the Arabic interface', async () => {
    await setLanguage('ary');
    const { user } = renderApp();

    const textarea = await screen.findByLabelText('الرسالة ديالك');
    await user.type(textarea, 'wach n9der ndir chi chikaya?');
    await user.keyboard('{Enter}');

    const bubble = (await screen.findByText('wach n9der ndir chi chikaya?')).closest('[dir]');
    expect(bubble).toHaveAttribute('dir', 'ltr');
  });
});
