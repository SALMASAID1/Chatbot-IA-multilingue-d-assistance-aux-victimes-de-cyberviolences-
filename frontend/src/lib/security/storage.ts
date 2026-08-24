/**
 * Session-scoped storage.
 *
 * Only the session identifier is persisted, and only in `sessionStorage`, so it
 * dies with the browser tab. Conversation contents are never written to disk:
 * a shared or seized device must not reveal what someone asked.
 *
 * Every access is guarded — Safari private mode and hardened browsers throw on
 * `sessionStorage` access rather than returning null.
 */
const SESSION_KEY = 'emc.session_id';
const LANG_KEY = 'emc.ui_language';

function safeGet(key: string): string | null {
  try {
    return window.sessionStorage.getItem(key);
  } catch {
    return null;
  }
}

function safeSet(key: string, value: string): void {
  try {
    window.sessionStorage.setItem(key, value);
  } catch {
    /* storage unavailable — the app still works, it just forgets on reload */
  }
}

function safeRemove(key: string): void {
  try {
    window.sessionStorage.removeItem(key);
  } catch {
    /* ignore */
  }
}

export function readStoredSessionId(): string | null {
  const value = safeGet(SESSION_KEY);
  return value && value.trim() !== '' ? value : null;
}

export function storeSessionId(sessionId: string): void {
  safeSet(SESSION_KEY, sessionId);
}

export function clearStoredSessionId(): void {
  safeRemove(SESSION_KEY);
}

/**
 * The interface language is a display preference, not conversation content, so
 * remembering it for the tab is safe and avoids re-picking a language on reload.
 */
export function readStoredLanguage(): string | null {
  return safeGet(LANG_KEY);
}

export function storeLanguage(language: string): void {
  safeSet(LANG_KEY, language);
}
