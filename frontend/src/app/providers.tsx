import { QueryClientProvider, type QueryClient } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { createQueryClient } from './queryClient';

export function AppProviders({ children, client }: { children: ReactNode; client?: QueryClient }) {
  const queryClient = client ?? createQueryClient();
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
