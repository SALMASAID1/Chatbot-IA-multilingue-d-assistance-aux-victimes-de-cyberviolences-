/**
 * TanStack Query bindings.
 *
 * Retry policy is deliberate:
 *  - `POST /api/chat` NEVER retries (non-idempotent: a retry can duplicate the
 *    user's message and spend LLM quota twice).
 *  - `POST /api/chat/feedback` never retries either.
 *  - Read-only calls retry once, and never on 404/422/429.
 */
import { useMutation, useQuery, type UseQueryResult } from '@tanstack/react-query';
import { getHealth, getHistory } from './endpoints';
import { sendChatMessage, submitFeedback } from './endpoints';
import { isApiError } from './errors';
import type {
  ChatHistory,
  ChatRequestBody,
  ChatResponse,
  FeedbackRequestBody,
  FeedbackResponse,
  HealthResponse,
} from '@/types/api';

export const queryKeys = {
  health: ['health'] as const,
  history: (sessionId: string) => ['history', sessionId] as const,
};

function retryReadOnly(failureCount: number, error: Error): boolean {
  if (isApiError(error)) {
    if (['notFound', 'validation', 'rateLimited', 'aborted', 'offline'].includes(error.kind)) {
      return false;
    }
  }
  return failureCount < 1;
}

export function useHealth(enabled = true): UseQueryResult<HealthResponse, Error> {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: ({ signal }) => getHealth(signal),
    enabled,
    retry: retryReadOnly,
    refetchInterval: 60_000,
    refetchOnWindowFocus: true,
    staleTime: 30_000,
  });
}

export function useHistory(
  sessionId: string | null,
  enabled: boolean,
): UseQueryResult<ChatHistory, Error> {
  return useQuery({
    queryKey: queryKeys.history(sessionId ?? 'none'),
    queryFn: ({ signal }) => getHistory(sessionId as string, signal),
    enabled: enabled && Boolean(sessionId),
    retry: retryReadOnly,
    refetchOnWindowFocus: false,
    staleTime: Infinity,
    gcTime: 0,
  });
}

export interface SendMessageVariables extends ChatRequestBody {
  signal?: AbortSignal;
}

export function useSendMessage(options: {
  onSuccess?: (data: ChatResponse, variables: SendMessageVariables) => void;
  onError?: (error: Error, variables: SendMessageVariables) => void;
}) {
  return useMutation<ChatResponse, Error, SendMessageVariables>({
    mutationFn: ({ signal, ...body }) => sendChatMessage(body, signal),
    retry: false,
    ...options,
  });
}

export function useFeedback() {
  return useMutation<FeedbackResponse, Error, FeedbackRequestBody>({
    mutationFn: (body) => submitFeedback(body),
    retry: false,
  });
}
