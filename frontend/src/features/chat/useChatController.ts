/**
 * Owns the conversation: timeline, session lifecycle, sending, cancellation and
 * error surfacing. Kept separate from the presentation components so the flow
 * can be unit-tested without a DOM tree.
 *
 * Restored history is *derived* from the query cache rather than copied into
 * state, so there is no effect-driven duplication of the same data and no
 * cascading render when a previous conversation loads.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useHistory, useSendMessage, queryKeys } from '@/lib/api/queries';
import { isApiError, type ApiErrorKind } from '@/lib/api/errors';
import { clearStoredSessionId, readStoredSessionId, storeSessionId } from '@/lib/security/storage';
import { parseBackendDate } from '@/lib/datetime';
import { logDebug } from '@/lib/logger';
import type { SupportedLanguage, TimelineMessage } from '@/types/api';

let localIdCounter = 0;
function nextLocalId(prefix: string): string {
  localIdCounter += 1;
  return `${prefix}-${localIdCounter}-${Date.now().toString(36)}`;
}

function nowIso(): string {
  return new Date().toISOString();
}

export interface ChatNotice {
  kind: ApiErrorKind | 'sessionRestored' | 'sessionExpired';
  /** Retry sends the same text again; only set when a send failed. */
  retryText?: string;
}

export interface ChatController {
  messages: TimelineMessage[];
  isSending: boolean;
  isLoadingHistory: boolean;
  notice: ChatNotice | null;
  sessionId: string | null;
  hasConversation: boolean;
  send: (text: string, langue?: SupportedLanguage | null) => void;
  cancel: () => void;
  retryLast: () => void;
  reset: () => void;
  dismissNotice: () => void;
  /** Set when the newest assistant message is an emergency answer. */
  lastUrgentMessageId: string | null;
}

export function useChatController(): ChatController {
  const queryClient = useQueryClient();
  const [storedSessionId, setStoredSessionId] = useState<string | null>(() =>
    readStoredSessionId(),
  );
  const [liveMessages, setLiveMessages] = useState<TimelineMessage[]>([]);
  const [explicitNotice, setExplicitNotice] = useState<ChatNotice | null>(null);
  const [dismissedNoticeKind, setDismissedNoticeKind] = useState<string | null>(null);
  const [lastUrgentMessageId, setLastUrgentMessageId] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const pendingTextRef = useRef<string | null>(null);

  // Only fetch history for a session that already existed when the tab loaded.
  const [restorableSessionId] = useState<string | null>(() => readStoredSessionId());
  const history = useHistory(restorableSessionId, restorableSessionId !== null);

  // A 404 means the session expired server-side (30-minute TTL by default).
  const sessionExpired =
    history.isError && isApiError(history.error) && history.error.isMissingSession;

  useEffect(() => {
    // External side effect only — no state updates, so no cascading render.
    if (sessionExpired) {
      logDebug('Stored session no longer exists; a fresh one will be created on send');
      clearStoredSessionId();
    }
  }, [sessionExpired]);

  const sessionId = sessionExpired ? null : storedSessionId;

  const restoredMessages = useMemo<TimelineMessage[]>(() => {
    if (!history.data || sessionExpired) return [];
    return history.data.messages
      .filter((message) => message.role === 'user' || message.role === 'assistant')
      .map((message, index) => ({
        id: message.message_id ?? `restored-${index}`,
        role: message.role === 'user' ? 'user' : 'assistant',
        content: message.content,
        timestamp: parseBackendDate(message.timestamp)?.toISOString() ?? nowIso(),
      }));
  }, [history.data, sessionExpired]);

  const messages = useMemo(
    () => [...restoredMessages, ...liveMessages],
    [restoredMessages, liveMessages],
  );

  const derivedNotice = useMemo<ChatNotice | null>(
    () =>
      sessionExpired
        ? { kind: 'sessionExpired' }
        : restoredMessages.length > 0
          ? { kind: 'sessionRestored' }
          : null,
    [sessionExpired, restoredMessages.length],
  );

  const notice =
    explicitNotice ??
    (derivedNotice && derivedNotice.kind !== dismissedNoticeKind ? derivedNotice : null);

  const finishPending = useCallback(() => {
    abortRef.current = null;
    pendingTextRef.current = null;
  }, []);

  const mutation = useSendMessage({
    onSuccess: (data) => {
      setStoredSessionId((current) => {
        if (current !== data.session_id) storeSessionId(data.session_id);
        return data.session_id;
      });
      const assistantId = nextLocalId('assistant');
      const langue: SupportedLanguage = data.langue === 'ar' ? 'ar' : 'fr';
      setLiveMessages((current) => [
        ...current,
        {
          id: assistantId,
          role: 'assistant',
          content: data.answer,
          timestamp: parseBackendDate(data.timestamp)?.toISOString() ?? nowIso(),
          langue,
          isUrgent: data.is_urgent,
          isDarija: data.is_darija,
          sources: data.sources,
          exchangeId: data.message_id,
        },
      ]);
      if (data.is_urgent) setLastUrgentMessageId(assistantId);
      setExplicitNotice(null);
      finishPending();
    },
    onError: (error) => {
      const kind = isApiError(error) ? error.kind : 'unknown';
      const retryText = pendingTextRef.current ?? undefined;
      // Mark the user's turn as failed so the timeline stays truthful.
      setLiveMessages((current) => {
        const last = current[current.length - 1];
        if (!last || last.role !== 'user') return current;
        return [...current.slice(0, -1), { ...last, errorKind: kind }];
      });
      setExplicitNotice({ kind, retryText });
      finishPending();
    },
  });

  const isPending = mutation.isPending;

  const send = useCallback(
    (text: string, langue: SupportedLanguage | null = null) => {
      const trimmed = text.trim();
      if (trimmed === '' || isPending) return;

      setExplicitNotice(null);
      setDismissedNoticeKind(null);
      setLiveMessages((current) => [
        ...current,
        { id: nextLocalId('user'), role: 'user', content: trimmed, timestamp: nowIso() },
      ]);

      const controller = new AbortController();
      abortRef.current = controller;
      pendingTextRef.current = trimmed;

      mutation.mutate({
        message: trimmed,
        session_id: sessionExpired ? null : storedSessionId,
        langue,
        signal: controller.signal,
      });
    },
    [mutation, isPending, sessionExpired, storedSessionId],
  );

  const cancel = useCallback(() => abortRef.current?.abort(), []);

  const retryLast = useCallback(() => {
    const text = notice?.retryText;
    if (!text) return;
    // Drop the failed user turn; `send` re-adds it.
    setLiveMessages((current) => {
      const last = current[current.length - 1];
      if (last && last.role === 'user' && last.errorKind) return current.slice(0, -1);
      return current;
    });
    setExplicitNotice(null);
    send(text);
  }, [notice, send]);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    pendingTextRef.current = null;
    clearStoredSessionId();
    setStoredSessionId(null);
    setLiveMessages([]);
    setExplicitNotice(null);
    setDismissedNoticeKind(null);
    setLastUrgentMessageId(null);
    if (restorableSessionId) {
      queryClient.removeQueries({ queryKey: queryKeys.history(restorableSessionId) });
    }
  }, [queryClient, restorableSessionId]);

  const dismissNotice = useCallback(() => {
    setExplicitNotice(null);
    setDismissedNoticeKind(derivedNotice?.kind ?? null);
  }, [derivedNotice]);

  useEffect(() => () => abortRef.current?.abort(), []);

  return {
    messages,
    isSending: isPending,
    isLoadingHistory: history.isLoading && restorableSessionId !== null,
    notice,
    sessionId,
    hasConversation: messages.length > 0,
    send,
    cancel,
    retryLast,
    reset,
    dismissNotice,
    lastUrgentMessageId,
  };
}
