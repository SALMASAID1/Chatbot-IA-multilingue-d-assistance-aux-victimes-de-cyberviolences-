import { render, type RenderResult } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient } from '@tanstack/react-query';
import type { ReactElement } from 'react';
import { AppProviders } from '@/app/providers';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { AppShell } from '@/app/AppShell';
import i18n from '@/i18n';
import { applyDocumentLanguage } from '@/i18n';

/** Query client with retries and background refetching off for determinism. */
export function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, refetchInterval: false, refetchOnWindowFocus: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });
}

export function renderWithProviders(
  ui: ReactElement,
): RenderResult & { user: ReturnType<typeof userEvent.setup> } {
  const user = userEvent.setup();
  const result = render(<AppProviders client={createTestQueryClient()}>{ui}</AppProviders>);
  return { ...result, user };
}

export function renderApp(): RenderResult & { user: ReturnType<typeof userEvent.setup> } {
  return renderWithProviders(
    <ErrorBoundary>
      <AppShell />
    </ErrorBoundary>,
  );
}

/** Tests share the i18n singleton, so reset the language between them. */
export async function setLanguage(language: 'fr' | 'ar' | 'ary'): Promise<void> {
  await i18n.changeLanguage(language);
  applyDocumentLanguage(language);
}
