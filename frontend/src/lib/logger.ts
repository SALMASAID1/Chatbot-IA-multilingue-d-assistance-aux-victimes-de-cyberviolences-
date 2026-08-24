/**
 * Development-only logging.
 *
 * Production builds log nothing: message contents, profile classifications and
 * session identifiers must never reach a console or a third party.
 */
const enabled = import.meta.env.DEV;

export function logDebug(message: string, meta?: Record<string, unknown>): void {
  if (!enabled) return;
  console.debug(`[emc] ${message}`, meta ?? '');
}

export function logError(message: string, meta?: Record<string, unknown>): void {
  if (!enabled) return;
  console.error(`[emc] ${message}`, meta ?? '');
}
