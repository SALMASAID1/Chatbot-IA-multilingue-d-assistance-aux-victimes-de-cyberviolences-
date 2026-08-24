import { expect, test } from '@playwright/test';
import { mockApi } from './fixtures/mock-api';

/** Mobile-specific behaviour: disclosure navigation and the sticky composer. */
test.describe('mobile', () => {
  test.skip(({ isMobile }) => !isMobile, 'mobile viewport only');

  test.beforeEach(async ({ page }) => {
    await mockApi(page);
  });

  test('the header actions live behind an accessible disclosure', async ({ page }) => {
    await page.goto('/');

    const toggle = page.getByRole('button', { name: 'Ouvrir le menu' });
    await expect(toggle).toBeVisible();
    await expect(toggle).toHaveAttribute('aria-expanded', 'false');

    await toggle.click();
    await expect(page.getByRole('button', { name: 'Fermer le menu' })).toHaveAttribute(
      'aria-expanded',
      'true',
    );
    await expect(page.getByRole('button', { name: 'Aide et ressources' })).toBeVisible();

    await page.keyboard.press('Escape');
    await expect(page.getByRole('button', { name: 'Ouvrir le menu' })).toHaveAttribute(
      'aria-expanded',
      'false',
    );
  });

  test('the composer stays reachable while the conversation scrolls', async ({ page }) => {
    await page.goto('/');

    const composer = page.getByLabel('Votre message');
    for (const message of ['Première question', 'Deuxième question', 'Troisième question']) {
      await composer.fill(message);
      await composer.press('Enter');
      await expect(page.getByText(message)).toBeVisible();
    }

    // Sticky: still on screen after the timeline has grown.
    await expect(composer).toBeInViewport();

    const box = await page.getByRole('button', { name: 'Envoyer le message' }).boundingBox();
    expect(box?.height ?? 0).toBeGreaterThanOrEqual(44);
  });

  test('an answer can be sent entirely with the on-screen keyboard flow', async ({ page }) => {
    await page.goto('/');
    const composer = page.getByLabel('Votre message');
    await composer.tap();
    await composer.fill('Bonjour');
    await page.getByRole('button', { name: 'Envoyer le message' }).tap();

    await expect(
      page
        .getByRole('list', { name: 'Fil de la conversation' })
        .getByText(/Vous n'êtes pas responsable/),
    ).toBeVisible();
  });
});
