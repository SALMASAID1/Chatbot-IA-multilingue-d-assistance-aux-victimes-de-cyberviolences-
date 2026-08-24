import { useTranslation } from 'react-i18next';
import { Info, RotateCcw, TriangleAlert, X } from 'lucide-react';
import type { ChatNotice as Notice } from './useChatController';

const INFO_KINDS = new Set(['sessionRestored', 'sessionExpired', 'aborted']);

export function ChatNotice({
  notice,
  onRetry,
  onDismiss,
}: {
  notice: Notice;
  onRetry: () => void;
  onDismiss: () => void;
}) {
  const { t } = useTranslation();
  const informational = INFO_KINDS.has(notice.kind);

  const text =
    notice.kind === 'sessionRestored'
      ? t('chat.historyRestored')
      : notice.kind === 'sessionExpired'
        ? t('errors.notFound')
        : t(`errors.${notice.kind}`);

  return (
    <div
      // Errors interrupt politely-announced content; notices do not.
      role={informational ? 'status' : 'alert'}
      className={[
        'mb-3 flex flex-wrap items-center gap-x-3 gap-y-2 rounded-xl border px-4 py-3 text-sm',
        informational
          ? 'border-line bg-white text-muted'
          : 'border-alert-200 bg-alert-50 text-alert-700',
      ].join(' ')}
    >
      {informational ? (
        <Info aria-hidden="true" className="size-4 shrink-0" />
      ) : (
        <TriangleAlert aria-hidden="true" className="size-4 shrink-0" />
      )}
      <span className="min-w-0 flex-1">{text}</span>

      {notice.retryText ? (
        <button
          type="button"
          onClick={onRetry}
          className="tap-target inline-flex items-center gap-1.5 rounded-lg bg-white px-3 py-1.5 font-semibold text-navy-800 hover:bg-sand-100"
        >
          <RotateCcw aria-hidden="true" className="size-3.5" />
          {t('errors.retry')}
        </button>
      ) : null}

      <button
        type="button"
        onClick={onDismiss}
        className="tap-target inline-flex items-center justify-center rounded-lg hover:bg-white/60"
      >
        <X aria-hidden="true" className="size-4" />
        <span className="sr-only">{t('errors.dismiss')}</span>
      </button>
    </div>
  );
}
