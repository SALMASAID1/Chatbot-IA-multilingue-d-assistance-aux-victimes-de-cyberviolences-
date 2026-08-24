import { expect, test, type Page } from '@playwright/test';
import { frenchAnswer, mockApi } from './fixtures/mock-api';

/** An answer taller than the viewport, so the page really has to scroll. */
const longAnswer = {
  ...frenchAnswer,
  answer: Array.from(
    { length: 14 },
    (_, i) => `Ligne ${i + 1} de la réponse détaillée de l'assistant.`,
  ).join('\n\n'),
};

async function ask(page: Page, text: string) {
  const composer = page.getByLabel('Votre message');
  await composer.fill(text);
  await composer.press('Enter');
  await page.waitForTimeout(500);
}

function metrics(page: Page) {
  return page.evaluate(() => {
    const doc = document.documentElement;
    const form = document.querySelector('form') as HTMLElement;
    const items = document.querySelectorAll('ol[aria-label] > li');
    const last = items[items.length - 1] as HTMLElement;
    return {
      scrollY: Math.round(window.scrollY),
      maxScroll: Math.round(doc.scrollHeight - window.innerHeight),
      lastMessageBottom: Math.round(last.getBoundingClientRect().bottom),
      composerTop: Math.round(form.getBoundingClientRect().top),
    };
  });
}

test.beforeEach(async ({ page }) => {
  await mockApi(page, { chatAnswer: longAnswer });
});

test('the page follows the conversation instead of stranding the answer off-screen', async ({
  page,
}) => {
  await page.goto('/');
  await ask(page, 'Première question');
  await ask(page, 'Deuxième question');
  await page.waitForTimeout(600);

  const { scrollY, maxScroll, lastMessageBottom, composerTop } = await metrics(page);

  // Regression: the Markdown chunk loads *after* the message is added and grows
  // the page, which previously left the reader stranded near the top.
  expect(maxScroll - scrollY, 'the page should be scrolled to the bottom').toBeLessThanOrEqual(4);

  // Regression: the composer is sticky, so aligning to the viewport bottom used
  // to hide the end of the answer underneath it.
  expect(lastMessageBottom, 'the answer must not sit under the composer').toBeLessThanOrEqual(
    composerTop + 1,
  );
});

test('it does not yank a reader who scrolled back up', async ({ page }) => {
  await page.goto('/');
  await ask(page, 'Une question');
  await page.waitForTimeout(600);

  // Park just inside the "near the bottom" threshold — this used to snap.
  const target = await page.evaluate(() => {
    const top = document.documentElement.scrollHeight - window.innerHeight - 100;
    window.scrollTo({ top, behavior: 'instant' as ScrollBehavior });
    return Math.round(window.scrollY);
  });
  await page.waitForTimeout(900);
  expect(await page.evaluate(() => Math.round(window.scrollY))).toBe(target);

  // And further up, the position is held too.
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior }));
  await page.waitForTimeout(900);
  expect(await page.evaluate(() => Math.round(window.scrollY))).toBe(0);
});

test('a new answer arriving while reading offers a button instead of jumping', async ({ page }) => {
  await page.goto('/');
  await ask(page, 'Première question');
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior }));

  await ask(page, 'Deuxième question');
  await page.waitForTimeout(700);

  // The reader was not moved…
  expect(await page.evaluate(() => Math.round(window.scrollY))).toBe(0);

  // …and the affordance sits above the composer, never underneath it.
  const pill = page.getByRole('button', { name: 'Nouvelle réponse disponible' });
  await expect(pill).toBeVisible();

  const overlap = await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const p = buttons.find((b) => b.textContent?.includes('Nouvelle réponse'))!;
    const form = document.querySelector('form') as HTMLElement;
    return p.getBoundingClientRect().bottom - form.getBoundingClientRect().top;
  });
  expect(overlap, 'the pill must not overlap the composer').toBeLessThanOrEqual(1);

  await pill.click();
  await page.waitForTimeout(800);
  const after = await metrics(page);
  expect(after.maxScroll - after.scrollY).toBeLessThanOrEqual(4);
  await expect(pill).toBeHidden();
});
