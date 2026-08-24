/**
 * Emergency answer treatment.
 *
 * Rules encoded here:
 *  - `role="alert"` so assistive tech announces it immediately;
 *  - the backend's complete answer is preserved and rendered verbatim;
 *  - calm, bounded visual treatment — a bordered card, not a full red screen;
 *  - no animation, no confirmation step, nothing that delays access to help;
 *  - focus moves to the heading once (never trapped) so keyboard and screen
 *    reader users land on the help rather than hunting for it.
 */
import { useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { LifeBuoy } from 'lucide-react';
import { SafeMarkdown } from '@/components/SafeMarkdown';
import { EmergencyContacts } from './EmergencyContacts';
import { directionForMessageLanguage } from '@/i18n/languages';
import type { SupportedLanguage } from '@/types/api';

interface Props {
  answer: string;
  langue?: SupportedLanguage;
  /** Focus the heading when this is the newest urgent answer. */
  takeFocus?: boolean;
}

export function UrgentResponsePanel({ answer, langue, takeFocus = false }: Props) {
  const { t } = useTranslation();
  const headingRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    if (takeFocus) headingRef.current?.focus();
  }, [takeFocus]);

  const dir = directionForMessageLanguage(langue);

  return (
    <div
      role="alert"
      aria-label={t('emergency.panelLabel')}
      className="rounded-2xl border-2 border-alert-200 bg-alert-50 p-4 sm:p-5"
    >
      <div className="mb-3 flex items-start gap-3">
        <span
          aria-hidden="true"
          className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-alert-600 text-white"
        >
          <LifeBuoy className="size-5" />
        </span>
        <div className="min-w-0">
          <h2
            ref={headingRef}
            tabIndex={-1}
            className="text-base font-bold text-alert-700 outline-none"
          >
            {t('emergency.responseTitle')}
          </h2>
          <p className="text-sm text-navy-800">{t('emergency.responseLead')}</p>
        </div>
      </div>

      <div className="mb-4 rounded-xl bg-white/85 p-3 text-[0.95rem] text-navy-800">
        <div dir={dir} lang={langue === 'ar' ? 'ar' : 'fr'}>
          <SafeMarkdown>{answer}</SafeMarkdown>
        </div>
      </div>

      <EmergencyContacts variant="compact" />
    </div>
  );
}
