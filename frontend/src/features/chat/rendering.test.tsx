import { beforeEach, describe, expect, it, vi } from 'vitest';
import { screen, waitFor, within } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { server } from '@/mocks/server';
import {
  SESSION_ID,
  answerWithBareSources,
  answerWithHostileMarkdown,
  frenchAnswer,
  urgentAnswer,
} from '@/mocks/fixtures';
import { renderApp, setLanguage } from '@/test/utils';

/** Assistant text also lives in the sr-only announcer; scope to the timeline. */
function timeline() {
  return within(screen.getByRole('list', { name: 'Fil de la conversation' }));
}

async function ask(user: ReturnType<typeof renderApp>['user'], text = 'Question') {
  const textarea = await screen.findByLabelText('Votre message');
  await user.type(textarea, text);
  await user.keyboard('{Enter}');
}

beforeEach(async () => {
  await setLanguage('fr');
});

describe('urgent responses', () => {
  beforeEach(() => {
    server.use(http.post('*/api/chat', () => HttpResponse.json(urgentAnswer)));
  });

  it('renders the emergency answer in an alert panel and keeps it complete', async () => {
    const { user } = renderApp();
    await ask(user, 'Je suis en danger, il est chez moi');

    const alert = await screen.findByRole('alert', { name: 'Réponse d’urgence' });
    expect(within(alert).getByRole('heading', { name: 'Aide immédiate' })).toBeInTheDocument();

    // The backend answer is preserved verbatim, not summarised or replaced.
    await waitFor(() => expect(alert).toHaveTextContent(/Si vous etes en danger immediat/));
    expect(alert).toHaveTextContent(/Vous n'etes pas seul\(e\)/);
  });

  it('offers every Moroccan emergency number as a tel: link', async () => {
    const { user } = renderApp();
    await ask(user, 'Je suis en danger');

    const alert = await screen.findByRole('alert', { name: 'Réponse d’urgence' });
    for (const number of ['19', '177', '15', '2511']) {
      const link = within(alert).getByRole('link', { name: new RegExp(`Appeler le ${number}$`) });
      expect(link).toHaveAttribute('href', `tel:${number}`);
      // A call is offered, never placed automatically.
      expect(link).not.toHaveAttribute('target');
    }
    expect(alert).toHaveTextContent(/Aucun appel n’est lancé automatiquement/);
  });

  it('moves focus to the emergency heading without trapping it', async () => {
    const { user } = renderApp();
    await ask(user, 'Je suis en danger');

    const heading = await screen.findByRole('heading', { name: 'Aide immédiate' });
    await waitFor(() => expect(heading).toHaveFocus());

    // Focus is not trapped: the composer is still reachable.
    await user.tab();
    expect(heading).not.toHaveFocus();
  });

  it('does not show feedback or source controls on an emergency answer', async () => {
    const { user } = renderApp();
    await ask(user, 'Je suis en danger');

    await screen.findByRole('alert', { name: 'Réponse d’urgence' });
    expect(screen.queryByText('Cette réponse vous a-t-elle aidé ?')).not.toBeInTheDocument();
    expect(screen.queryByText(/Sources consultées/)).not.toBeInTheDocument();
  });
});

describe('sources', () => {
  it('lists path, category and relevance when the backend provides them', async () => {
    const { user } = renderApp();
    await ask(user);

    const summary = await screen.findByText('Sources consultées (2)');
    await user.click(summary);

    expect(screen.getByText('fiches_pratiques/cyberharcelement.md')).toBeInTheDocument();
    const disclosure = summary.closest('details') as HTMLElement;
    expect(disclosure).toHaveTextContent('Catégorie: juridique');
    // Percentages are locale-formatted ("82 %" in French), so match loosely.
    expect(disclosure).toHaveTextContent(/Pertinence:\s*82\s*%/);
  });

  it('never renders a link for a source: the API contract has no URL field', async () => {
    const { user } = renderApp();
    await ask(user);

    const summary = await screen.findByText('Sources consultées (2)');
    await user.click(summary);

    const disclosure = summary.closest('details') as HTMLElement;
    expect(within(disclosure).queryAllByRole('link')).toHaveLength(0);
  });

  it('degrades gracefully when path, category and score are all absent', async () => {
    server.use(http.post('*/api/chat', () => HttpResponse.json(answerWithBareSources)));
    const { user } = renderApp();
    await ask(user);

    const summary = await screen.findByText('Sources consultées (2)');
    await user.click(summary);

    const disclosure = summary.closest('details') as HTMLElement;
    // Both bare sources fall back to a neutral label.
    expect(within(disclosure).getAllByText('Document de la base de connaissances')).toHaveLength(2);
    expect(disclosure).toHaveTextContent('Catégorie: ressources');
  });

  it('renders no disclosure when there are no sources', async () => {
    server.use(http.post('*/api/chat', () => HttpResponse.json({ ...frenchAnswer, sources: [] })));
    const { user } = renderApp();
    await ask(user);

    await timeline().findByText(/Vous n'êtes pas responsable/);
    expect(screen.queryByText(/Sources consultées/)).not.toBeInTheDocument();
  });
});

describe('markdown safety', () => {
  it('neutralises scripts, event handlers and javascript: links', async () => {
    server.use(http.post('*/api/chat', () => HttpResponse.json(answerWithHostileMarkdown)));
    const { user } = renderApp();
    await ask(user);

    // Wait for the lazily-loaded Markdown renderer to take over.
    const link = await screen.findByRole('link', { name: 'Signalement officiel' });

    expect((window as unknown as { __pwned?: boolean }).__pwned).toBeUndefined();
    expect(document.querySelector('script')).toBeNull();
    expect(document.querySelector('img')).toBeNull();
    expect(document.querySelector('[onerror]')).toBeNull();

    // The booby-trapped link keeps its text but loses its href.
    const trapped = screen.getByText('Lien piégé');
    expect(trapped.tagName).toBe('SPAN');
    expect(screen.queryByRole('link', { name: 'Lien piégé' })).not.toBeInTheDocument();

    // Genuine external links are hardened.
    expect(link).toHaveAttribute('href', 'https://evigilance.ma/fr/signaler');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    expect(link).toHaveAttribute('target', '_blank');
  });
});

describe('answer actions', () => {
  it('copies the answer text', async () => {
    const { user } = renderApp();
    await ask(user);

    await timeline().findByText(/Vous n'êtes pas responsable/);
    await user.click(screen.getByRole('button', { name: 'Copier la réponse' }));

    // user-event installs a working clipboard stub, so assert on its contents.
    expect(await navigator.clipboard.readText()).toBe(frenchAnswer.answer);
    expect(await screen.findByText('Réponse copiée')).toBeInTheDocument();
  });

  it('submits feedback against the exchange id from the backend', async () => {
    const received = vi.fn();
    server.use(
      http.post('*/api/chat/feedback', async ({ request }) => {
        received(await request.json());
        return HttpResponse.json({ status: 'received', message: 'Merci' });
      }),
    );

    const { user } = renderApp();
    await ask(user);

    await timeline().findByText(/Vous n'êtes pas responsable/);
    await user.click(screen.getByRole('button', { name: 'Oui, cela m’aide' }));

    await waitFor(() =>
      expect(received).toHaveBeenCalledWith({
        session_id: SESSION_ID,
        message_id: frenchAnswer.message_id,
        rating: 5,
      }),
    );
    expect(await screen.findByText('Merci pour votre retour.')).toBeInTheDocument();
  });

  it('keeps the failure quiet and local when feedback cannot be sent', async () => {
    server.use(http.post('*/api/chat/feedback', () => new HttpResponse(null, { status: 404 })));

    const { user } = renderApp();
    await ask(user);

    await timeline().findByText(/Vous n'êtes pas responsable/);
    await user.click(screen.getByRole('button', { name: 'Non, pas vraiment' }));

    expect(await screen.findByText('Votre retour n’a pas pu être envoyé.')).toBeInTheDocument();
    // The answer itself is untouched.
    expect(timeline().getByText(/Vous n'êtes pas responsable/)).toBeInTheDocument();
  });
});
