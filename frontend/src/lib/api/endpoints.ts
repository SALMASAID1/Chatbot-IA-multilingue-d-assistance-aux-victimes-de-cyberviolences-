/**
 * One function per backend endpoint.
 *
 * The admin endpoints (`GET /api/admin/sessions`, `DELETE /api/admin/sessions/{id}`)
 * are intentionally NOT implemented: they are unauthenticated on the backend and
 * expose session metadata, so no client surface is provided for them.
 */
import { request, timeouts } from './client';
import {
  chatHistorySchema,
  chatResponseSchema,
  feedbackResponseSchema,
  healthResponseSchema,
  sessionResponseSchema,
} from './schemas';
import type {
  ChatHistory,
  ChatRequestBody,
  ChatResponse,
  FeedbackRequestBody,
  FeedbackResponse,
  HealthResponse,
  SessionResponse,
  SupportedLanguage,
} from '@/types/api';

export function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return request('/api/health', {
    schema: healthResponseSchema,
    signal,
    timeoutMs: timeouts.health,
  });
}

export function createSession(
  langue?: SupportedLanguage | null,
  signal?: AbortSignal,
): Promise<SessionResponse> {
  return request('/api/chat/session', {
    method: 'POST',
    body: { langue: langue ?? null },
    schema: sessionResponseSchema,
    signal,
  });
}

export function sendChatMessage(
  body: ChatRequestBody,
  signal?: AbortSignal,
): Promise<ChatResponse> {
  return request('/api/chat', {
    method: 'POST',
    body,
    schema: chatResponseSchema,
    signal,
  });
}

export function getHistory(sessionId: string, signal?: AbortSignal): Promise<ChatHistory> {
  return request(`/api/chat/history/${encodeURIComponent(sessionId)}`, {
    schema: chatHistorySchema,
    signal,
    timeoutMs: timeouts.health,
  });
}

export function submitFeedback(
  body: FeedbackRequestBody,
  signal?: AbortSignal,
): Promise<FeedbackResponse> {
  return request('/api/chat/feedback', {
    method: 'POST',
    body,
    schema: feedbackResponseSchema,
    signal,
  });
}
