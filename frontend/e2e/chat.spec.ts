import { expect, test } from '@playwright/test';
import type { Page } from '@playwright/test';
import { degradedHealth, mockApi, urgentAnswer } from './fixtures/mock-api';

/** On small viewports the header actions live behind a disclosure button. */
async function openHeaderActions(page: Page): Promise<void> {
  const toggle = page.getByRole('button', { name: 'Ouvrir le menu' });
  if (await toggle.isVisible()) await toggle.click();
}

test.beforeEach(async ({ page }) => {
  await mockApi(page);
});

test('a visitor can read the welcome state and send a first message', async ({ page }) => {
  await page.goto('/');

  await expect(
    page.getByRole('heading', { name: /Bonjour, vous êtes au bon endroit/ }),
  ).toBeVisible();
  await expect(page.getByText(/Votre conversation n’est pas enregistrée/)).toBeVisible();
  await expect(page.getByRole('button', { name: /Protéger mes comptes/ })).toBeVisible();

  const composer = page.getByLabel('Votre message');
  await composer.fill('Je suis victime de cyberharcèlement');
  await composer.press('Enter');

  await expect(page.getByText('Je suis victime de cyberharcèlement')).toBeVisible();
  const timeline = page.getByRole('list', { name: 'Fil de la conversation' });
  await expect(timeline.getByText(/Vous n'êtes pas responsable/)).toBeVisible();
  await expect(page.getByText('Sources consultées (1)')).toBeVisible();

  // The welcome panel gives way to the conversation.
  await expect(
    page.getByRole('heading', { name: /Bonjour, vous êtes au bon endroit/ }),
  ).toBeHidden();
  await expect(composer).toBeFocused();
  await expect(composer).toHaveValue('');
});

test('a suggestion card fills the composer', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: /Conserver les preuves/ }).click();
  await expect(page.getByLabel('Votre message')).toHaveValue(
    'Comment conserver correctement les preuves d’une cyberviolence ?',
  );
});

test('an urgent answer is announced as an alert with callable numbers', async ({ page }) => {
  await mockApi(page, { chatAnswer: urgentAnswer });
  await page.goto('/');

  const composer = page.getByLabel('Votre message');
  await composer.fill('Je suis en danger, il est chez moi');
  await composer.press('Enter');

  const alert = page.getByRole('alert', { name: 'Réponse d’urgence' });
  await expect(alert).toBeVisible();
  await expect(alert.getByRole('heading', { name: 'Aide immédiate' })).toBeFocused();
  await expect(alert).toContainText('Si vous etes en danger immediat');

  for (const [number] of [['19'], ['177'], ['15'], ['2511']]) {
    await expect(
      alert.getByRole('link', { name: new RegExp(`Appeler le ${number}$`) }),
    ).toHaveAttribute('href', `tel:${number}`);
  }
});

test('the interface switches to Arabic and flips direction', async ({ page }) => {
  await page.goto('/');
  await openHeaderActions(page);
  await page.getByRole('button', { name: 'العربية' }).click();

  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  await expect(page.locator('html')).toHaveAttribute('lang', 'ar');
  await expect(page.getByLabel('رسالتك')).toBeVisible();

  await page.getByRole('button', { name: 'الدارجة' }).click();
  await expect(page.locator('html')).toHaveAttribute('lang', 'ary');
  await expect(page.getByLabel('الرسالة ديالك')).toBeVisible();
});

test('a degraded backend is reported without hiding emergency contacts', async ({ page }) => {
  await mockApi(page, { health: degradedHealth });
  await page.goto('/');

  const banner = page.getByRole('status').first();
  await expect(banner).toContainText('Service partiellement disponible');
  await banner.getByRole('button', { name: 'Voir les numéros d’urgence' }).click();

  const dialog = page.getByRole('dialog');
  await expect(dialog.getByRole('link', { name: /Appeler le 19/ })).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(dialog).toBeHidden();
});

test('a rate-limited send explains itself and offers a retry', async ({ page }) => {
  await mockApi(page, { chatStatus: 429 });
  await page.goto('/');

  const composer = page.getByLabel('Votre message');
  await composer.fill('Question');
  await composer.press('Enter');

  const alert = page.getByRole('alert');
  await expect(alert).toContainText(/Trop de messages envoyés coup sur coup/);
  await expect(alert.getByRole('button', { name: 'Réessayer' })).toBeVisible();
});

test('a pending request can be cancelled', async ({ page }) => {
  await mockApi(page, { chatDelayMs: 4000 });
  await page.goto('/');

  const composer = page.getByLabel('Votre message');
  await composer.fill('Une question longue');
  await composer.press('Enter');

  // Also present in the sr-only announcer; assert on the visible one.
  await expect(
    page
      .getByRole('list', { name: 'Fil de la conversation' })
      .getByText('Préparation d’une réponse…'),
  ).toBeVisible();
  await page.getByRole('button', { name: 'Annuler la demande' }).click();
  await expect(page.getByText('Demande annulée.')).toBeVisible();
});

test('the page has no horizontal overflow from 320px to desktop', async ({ page }) => {
  await page.goto('/');
  for (const width of [320, 375, 768, 1024, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    expect(overflow, `viewport ${width}px must not scroll horizontally`).toBeLessThanOrEqual(0);
  }
});
