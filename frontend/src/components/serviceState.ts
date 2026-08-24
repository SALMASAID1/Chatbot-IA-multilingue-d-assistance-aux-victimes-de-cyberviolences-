import type { HealthResponse } from '@/types/api';

export type ServiceState = 'checking' | 'online' | 'degraded' | 'offline' | 'unreachable';

/**
 * Collapses browser connectivity and the backend's own health report into one
 * state. `GET /api/health` returns "degraded" when the RAG store or the Gemini
 * client is not ready, which is worth telling the user about up front.
 */
export function resolveServiceState(options: {
  online: boolean;
  isLoading: boolean;
  isError: boolean;
  data?: HealthResponse | undefined;
}): ServiceState {
  if (!options.online) return 'offline';
  if (options.isError) return 'unreachable';
  if (options.isLoading || !options.data) return 'checking';
  return options.data.status === 'healthy' ? 'online' : 'degraded';
}
