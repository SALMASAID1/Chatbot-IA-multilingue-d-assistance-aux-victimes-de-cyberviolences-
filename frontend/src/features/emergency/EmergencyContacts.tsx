/**
 * Verified Moroccan emergency numbers and reporting links.
 *
 * Numbers are `tel:` links the user must activate themselves — a call is never
 * placed automatically. Digits are wrapped in `.force-ltr` so they read
 * correctly inside RTL text.
 */
import { useTranslation } from 'react-i18next';
import { ExternalLink, Phone } from 'lucide-react';
import { EMERGENCY_PHONES, SUPPORT_LINKS } from './contacts';
import { telHref } from '@/lib/security/url';

interface Props {
  /** `compact` drops the section heading (used inside the urgent panel). */
  variant?: 'default' | 'compact';
  includeLinks?: boolean;
}

export function EmergencyContacts({ variant = 'default', includeLinks = true }: Props) {
  const { t } = useTranslation();

  return (
    <section aria-labelledby="emergency-contacts-heading" className="space-y-2">
      <h3
        id="emergency-contacts-heading"
        className={
          variant === 'compact'
            ? 'sr-only'
            : 'text-sm font-bold tracking-wide text-navy-800 uppercase'
        }
      >
        {t('emergency.contactsTitle')}
      </h3>

      <ul className="grid gap-2 sm:grid-cols-2">
        {EMERGENCY_PHONES.map((contact) => (
          <li key={contact.id}>
            <a
              href={telHref(contact.number)}
              className="tap-target flex items-center gap-3 rounded-xl border border-alert-200 bg-white px-3 py-2.5 text-start transition-colors hover:bg-alert-50"
            >
              <span
                aria-hidden="true"
                className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-alert-50 text-alert-600"
              >
                <Phone className="size-4" />
              </span>
              <span className="min-w-0">
                <span className="force-ltr block text-base font-bold text-alert-700">
                  {contact.number}
                </span>
                <span className="block text-xs leading-snug text-muted">{t(contact.labelKey)}</span>
              </span>
              <span className="sr-only">
                {t('emergency.callAction', { number: contact.number })}
              </span>
            </a>
          </li>
        ))}
      </ul>

      <p className="text-xs text-muted">{t('emergency.callNote')}</p>

      {includeLinks ? (
        <ul className="space-y-1.5 pt-1">
          {SUPPORT_LINKS.map((link) => (
            <li key={link.id}>
              <a
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="tap-target inline-flex items-center gap-2 py-1 text-sm font-semibold text-teal-700 underline underline-offset-2 hover:text-teal-800"
              >
                <ExternalLink aria-hidden="true" className="size-4 shrink-0" />
                <span>
                  <span className="force-ltr">{link.name}</span>
                  <span className="font-normal text-muted"> — {t(link.labelKey)}</span>
                </span>
              </a>
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
