/**
 * Automated accessibility checks with axe-core.
 *
 * The `color-contrast` rule is disabled here because jsdom performs no layout
 * or style resolution and would report false results; contrast is instead
 * asserted directly against the design tokens in src/styles/contrast.test.ts.
 */
import { beforeEach, describe, expect, it } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import axe, { type Result } from 'axe-core';
import { http, HttpResponse } from 'msw';
import { server } from '@/mocks/server';
import { arabicAnswer, degradedHealth, urgentAnswer } from '@/mocks/fixtures';
import { renderApp, setLanguage } from '@/test/utils';

async function analyse(container: HTMLElement): Promise<Result[]> {
  const results = await axe.run(container, {
    rules: { 'color-contrast': { enabled: false } },
    resultTypes: ['violations'],
  });
  return results.violations;
}

function describeViolations(violations: Result[]): string {
  return violations
    .map((violation) => `${violation.id}: ${violation.help} (${violation.nodes.length} node(s))`)
    .join('\n');
}

beforeEach(async () => {
  await setLanguage('fr');
});

describe('accessibility', () => {
  it('has no violations in the welcome state', async () => {
    const { container } = renderApp();
    await screen.findByLabelText('Votre message');

    const violations = await analyse(container);
    expect(describeViolations(violations)).toBe('');
  });

  it('has no violations once a conversation is under way', async () => {
    const { container, user } = renderApp();
    await user.type(screen.getByLabelText('Votre message'), 'Bonjour');
    await user.keyboard('{Enter}');
    await screen.findByText('Sources consultées (2)');

    const violations = await analyse(container);
    expect(describeViolations(violations)).toBe('');
  });

  it('has no violations in the emergency state', async () => {
    server.use(http.post('*/api/chat', () => HttpResponse.json(urgentAnswer)));
    const { container, user } = renderApp();
    await user.type(screen.getByLabelText('Votre message'), 'Je suis en danger');
    await user.keyboard('{Enter}');
    await screen.findByRole('alert', { name: 'Réponse d’urgence' });

    const violations = await analyse(container);
    expect(describeViolations(violations)).toBe('');
  });

  it('has no violations in the Arabic right-to-left interface', async () => {
    server.use(http.post('*/api/chat', () => HttpResponse.json(arabicAnswer)));
    const { container, user } = renderApp();
    await user.click(screen.getByRole('button', { name: 'العربية' }));
    await waitFor(() => expect(document.documentElement.dir).toBe('rtl'));

    const textarea = await screen.findByLabelText('رسالتك');
    await user.type(textarea, 'مرحبا');
    await user.keyboard('{Enter}');
    // Also present in the sr-only announcer, so match all occurrences.
    await waitFor(() => expect(screen.getAllByText(/لست مسؤولا/).length).toBeGreaterThan(0));

    const violations = await analyse(container);
    expect(describeViolations(violations)).toBe('');
  });

  it('has no violations in the help dialog', async () => {
    const { container, user } = renderApp();
    await user.click(screen.getByRole('button', { name: 'Aide et ressources' }));
    await screen.findByRole('dialog');

    const violations = await analyse(container);
    expect(describeViolations(violations)).toBe('');
  });

  it('has no violations while the service is degraded', async () => {
    server.use(http.get('*/api/health', () => HttpResponse.json(degradedHealth)));
    const { container } = renderApp();
    await screen.findByRole('status');

    const violations = await analyse(container);
    expect(describeViolations(violations)).toBe('');
  });
});
