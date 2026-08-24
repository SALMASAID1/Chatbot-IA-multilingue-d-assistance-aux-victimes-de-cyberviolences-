/**
 * Connection / service indicator.
 *
 * `GET /api/health` distinguishes RAG and LLM readiness, so a degraded backend
 * is reported honestly instead of failing silently on the first message. In
 * every non-healthy state the verified emergency numbers stay one click away.
 */
import { useTranslation } from 'react-i18next';
import { CheckCircle2, CircleAlert, WifiOff } from 'lucide-react';
import type { ServiceState } from './serviceState';

const ICONS = {
  checking: CircleAlert,
  online: CheckCircle2,
  degraded: CircleAlert,
  offline: WifiOff,
  unreachable: WifiOff,
} as const;

const DOT_CLASS: Record<ServiceState, string> = {
  checking: 'bg-line-strong',
  online: 'bg-teal-600',
  degraded: 'bg-coral-600',
  offline: 'bg-alert-600',
  unreachable: 'bg-alert-600',
};

export function ServiceStatus({ state }: { state: ServiceState }) {
  const { t } = useTranslation();
  const Icon = ICONS[state];

  return (
    <p
      className="inline-flex items-center gap-1.5 text-xs font-medium text-muted"
      // Status changes are informative, not urgent.
      aria-live="polite"
    >
      <span className="sr-only">{t('status.label')}: </span>
      {/* Shape + text carry the meaning; colour alone never does. */}
      <Icon aria-hidden="true" className="size-3.5" />
      <span aria-hidden="true" className={`size-1.5 rounded-full ${DOT_CLASS[state]}`} />
      {t(`status.${state}`)}
    </p>
  );
}

export function ServiceStatusBanner({
  state,
  onShowEmergency,
}: {
  state: ServiceState;
  onShowEmergency: () => void;
}) {
  const { t } = useTranslation();
  if (state === 'online' || state === 'checking') return null;

  const detailKey =
    state === 'offline'
      ? 'status.offlineDetail'
      : state === 'degraded'
        ? 'status.degradedDetail'
        : 'status.unreachableDetail';

  return (
    <div
      role="status"
      className="mx-auto mb-4 flex w-full max-w-3xl flex-wrap items-center gap-x-3 gap-y-2 rounded-xl border border-warn-200 bg-warn-50 px-4 py-3 text-sm text-warn-700"
    >
      <CircleAlert aria-hidden="true" className="size-4 shrink-0" />
      <span className="min-w-0 flex-1">
        <strong className="font-bold">{t(`status.${state}`)}.</strong> {t(detailKey)}
      </span>
      <button
        type="button"
        onClick={onShowEmergency}
        className="tap-target rounded-lg bg-white px-3 py-1.5 font-semibold text-navy-800 underline underline-offset-2 hover:bg-sand-50"
      >
        {t('status.showEmergency')}
      </button>
    </div>
  );
}
