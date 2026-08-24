import { QueryClient } from '@tanstack/react-query';

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Conversation data is sensitive: keep it out of long-lived caches.
        gcTime: 5 * 60_000,
        refetchOnWindowFocus: false,
      },
      // Mutations are never retried automatically (see lib/api/queries.ts).
      mutations: { retry: false },
    },
  });
}
