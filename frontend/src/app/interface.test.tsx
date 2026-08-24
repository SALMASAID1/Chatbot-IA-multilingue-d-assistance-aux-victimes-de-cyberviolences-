import { beforeEach, describe, expect, it } from 'vitest';
import { screen, waitFor, within } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { server } from '@/mocks/server';
import { arabicAnswer, frenchAnswer } from '@/mocks/fixtures';
import { renderApp, setLanguage } from '@/test/utils';

beforeEach(async () => {
  await setLanguage('fr');
});

describe('language switching', () => {
  it('switches the interface, the document language and the direction', async () => {
    const { user } = renderApp();

    expect(document.documentElement.lang).toBe('fr');
    expect(document.documentElement.dir).toBe('ltr');

    await user.click(screen.getByRole('button', { name: 'العربية' }));

    await waitFor(() => expect(document.documentElement.lang).toBe('ar'));
    expect(document.documentElement.dir).toBe('rtl');
    expect(await screen.findByLabelText('رسالتك')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'الدارجة' }));
    await waitFor(() => expect(document.documentElement.lang).toBe('ary'));
    expect(document.documentElement.dir).toBe('rtl');
    // Darija strings differ from MSA ones.
    expect(await screen.findByLabelText('الرسالة ديالك')).toBeInTheDocument();
  });

  it('remembers the choice for the tab only', async () => {
    const { user } = renderApp();
    await user.click(screen.getByRole('button', { name: 'العربية' }));
    await waitFor(() => expect(window.sessionStorage.getItem('emc.ui_language')).toBe('ar'));
  });

  it('marks the active language for assistive technology', async () => {
    const { user } = renderApp();
    const arabic = screen.getByRole('button', { name: 'العربية' });
    expect(arabic).toHaveAttribute('aria-pressed', 'false');

    await user.click(arabic);
    await waitFor(() => expect(arabic).toHaveAttribute('aria-pressed', 'true'));
    expect(screen.getByRole('button', { name: 'Français' })).toHaveAttribute(
      'aria-pressed',
      'false',
    );
  });

  it('never changes the interface language because an answer came back in another one', async () => {
    server.use(http.post('*/api/chat', () => HttpResponse.json(arabicAnswer)));
    const { user } = renderApp();

    await user.type(screen.getByLabelText('Votre message'), 'أنا ضحية');
    await user.keyboard('{Enter}');
    await within(await screen.findByRole('list', { name: 'Fil de la conversation' })).findByText(
      /لست مسؤولا عما وقع لك/,
    );

    // Interface stays French; only the message itself is Arabic.
    expect(document.documentElement.lang).toBe('fr');
    expect(document.documentElement.dir).toBe('ltr');
    // …and the difference is surfaced discreetly.
    expect(screen.getByText('Réponse en العربية')).toBeInTheDocument();
  });
});

describe('keyboard navigation', () => {
  it('starts with a skip link that targets the main region', async () => {
    const { user } = renderApp();
    await user.tab();

    const skip = screen.getByRole('link', { name: 'Aller au contenu principal' });
    expect(skip).toHaveFocus();
    expect(skip).toHaveAttribute('href', '#main-content');
    expect(document.getElementById('main-content')).not.toBeNull();
  });

  it('reaches the language controls and header actions with the keyboard', async () => {
    const { user } = renderApp();
    await user.tab(); // skip link
    await user.tab(); // Français
    expect(screen.getByRole('button', { name: 'Français' })).toHaveFocus();
    await user.tab();
    expect(screen.getByRole('button', { name: 'العربية' })).toHaveFocus();
    await user.tab();
    expect(screen.getByRole('button', { name: 'الدارجة' })).toHaveFocus();
    await user.tab();
    expect(screen.getByRole('button', { name: 'Nouvelle conversation' })).toHaveFocus();
  });

  it('can send a message with the keyboard alone', async () => {
    const { user } = renderApp();
    const textarea = screen.getByLabelText('Votre message');
    textarea.focus();
    await user.keyboard('Bonjour{Enter}');

    expect(await screen.findByText('Bonjour')).toBeInTheDocument();
    await waitFor(() =>
      expect(
        within(screen.getByRole('list', { name: 'Fil de la conversation' })).getByText(
          /Vous n'êtes pas responsable/,
        ),
      ).toBeInTheDocument(),
    );
  });
});

describe('help dialog', () => {
  it('opens, traps focus, closes on Escape and restores focus', async () => {
    const { user } = renderApp();
    const trigger = screen.getByRole('button', { name: 'Aide et ressources' });
    await user.click(trigger);

    const dialog = await screen.findByRole('dialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(within(dialog).getByRole('heading', { name: 'Aide et ressources' })).toBeInTheDocument();
    // Emergency numbers are always reachable from help.
    expect(within(dialog).getByRole('link', { name: /Appeler le 19/ })).toHaveAttribute(
      'href',
      'tel:19',
    );

    await user.keyboard('{Escape}');
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
    expect(trigger).toHaveFocus();
  });
});

describe('new conversation', () => {
  it('starts immediately when there is nothing to lose', async () => {
    const { user } = renderApp();
    await user.click(screen.getByRole('button', { name: 'Nouvelle conversation' }));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('asks for confirmation once a conversation exists, and can be cancelled', async () => {
    const { user } = renderApp();
    await user.type(screen.getByLabelText('Votre message'), 'Bonjour');
    await user.keyboard('{Enter}');
    await screen.findByText('Bonjour');

    await user.click(screen.getByRole('button', { name: 'Nouvelle conversation' }));
    const dialog = await screen.findByRole('dialog');
    await user.click(within(dialog).getByRole('button', { name: 'Garder la conversation' }));

    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
    expect(screen.getByText('Bonjour')).toBeInTheDocument();
  });

  it('clears the conversation, the stored session and the draft when confirmed', async () => {
    const { user } = renderApp();
    const textarea = screen.getByLabelText('Votre message');
    await user.type(textarea, 'Bonjour');
    await user.keyboard('{Enter}');
    await screen.findByText('Bonjour');
    await waitFor(() => expect(window.sessionStorage.getItem('emc.session_id')).not.toBeNull());

    await user.type(textarea, 'Un brouillon');
    await user.click(screen.getByRole('button', { name: 'Nouvelle conversation' }));
    const dialog = await screen.findByRole('dialog');
    await user.click(within(dialog).getByRole('button', { name: 'Effacer et recommencer' }));

    await waitFor(() => expect(screen.queryByText('Bonjour')).not.toBeInTheDocument());
    expect(window.sessionStorage.getItem('emc.session_id')).toBeNull();
    expect((screen.getByLabelText('Votre message') as HTMLTextAreaElement).value).toBe('');
    // Back to the welcome state.
    expect(
      screen.getByRole('heading', { name: /Bonjour, vous êtes au bon endroit/ }),
    ).toBeInTheDocument();
  });
});

describe('welcome state', () => {
  it('offers the four localized suggestions and fills the composer', async () => {
    const { user } = renderApp();

    for (const title of [
      'Protéger mes comptes',
      'Signaler un contenu',
      'Conserver les preuves',
      'Aider quelqu’un',
    ]) {
      expect(screen.getByRole('button', { name: new RegExp(title) })).toBeInTheDocument();
    }

    await user.click(screen.getByRole('button', { name: /Conserver les preuves/ }));
    const textarea = screen.getByLabelText('Votre message') as HTMLTextAreaElement;
    await waitFor(() =>
      expect(textarea.value).toBe(
        'Comment conserver correctement les preuves d’une cyberviolence ?',
      ),
    );
    expect(textarea).toHaveFocus();
  });

  it('states the privacy position and the limits of the service', async () => {
    renderApp();
    expect(
      screen.getByText(/Votre conversation n’est pas enregistrée sur cet appareil/),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/ne remplace ni la police, ni les secours, ni un avocat/),
    ).toBeInTheDocument();
  });

  it('hides the welcome panel once the conversation starts', async () => {
    const { user } = renderApp();
    await user.type(screen.getByLabelText('Votre message'), 'Bonjour');
    await user.keyboard('{Enter}');

    await screen.findByText('Bonjour');
    expect(
      screen.queryByRole('heading', { name: /Bonjour, vous êtes au bon endroit/ }),
    ).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Protéger mes comptes/ })).not.toBeInTheDocument();
  });
});

describe('admin surface', () => {
  it('exposes no admin controls or requests', async () => {
    // The admin endpoints are unauthenticated on the backend, so the client
    // must offer no way to reach them.
    server.use(
      http.get('*/api/admin/*', () => {
        throw new Error('The frontend must never call an admin endpoint');
      }),
    );
    renderApp();
    await screen.findByLabelText('Votre message');

    expect(screen.queryByText(/admin/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/sessions actives/i)).not.toBeInTheDocument();
    expect(frenchAnswer.session_id).toBeTruthy();
  });
});
