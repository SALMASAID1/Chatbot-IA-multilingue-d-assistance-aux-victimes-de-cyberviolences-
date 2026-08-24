import { useState } from 'react';
import { AppProviders } from '@/app/providers';
import { createQueryClient } from '@/app/queryClient';
import { AppShell } from '@/app/AppShell';
import { ErrorBoundary } from '@/components/ErrorBoundary';

export default function App() {
  const [client] = useState(createQueryClient);

  return (
    <AppProviders client={client}>
      <ErrorBoundary>
        <AppShell />
      </ErrorBoundary>
    </AppProviders>
  );
}
