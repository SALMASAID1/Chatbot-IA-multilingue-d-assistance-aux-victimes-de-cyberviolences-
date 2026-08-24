/**
 * Interface-language control.
 *
 * Changing it never changes what the assistant answers in: the backend detects
 * the language of each message on its own, and silently flipping the interface
 * under someone mid-conversation would be disorienting.
 */
import { useTranslation } from 'react-i18next';
import { LANGUAGES, UI_LANGUAGES } from '@/i18n/languages';
import { applyDocumentLanguage } from '@/i18n';
import { storeLanguage } from '@/lib/security/storage';
import type { UiLanguage } from '@/types/api';

export function LanguageSwitcher({ className = '' }: { className?: string }) {
  const { t, i18n } = useTranslation();
  const current = i18n.language;

  const change = (language: UiLanguage) => {
    void i18n.changeLanguage(language);
    applyDocumentLanguage(language);
    storeLanguage(language);
  };

  return (
    <div
      role="group"
      aria-label={t('language.label')}
      className={`inline-flex rounded-xl border border-line bg-white p-0.5 ${className}`}
    >
      {UI_LANGUAGES.map((code) => {
        const config = LANGUAGES[code];
        const active = current === code;
        return (
          <button
            key={code}
            type="button"
            lang={config.htmlLang}
            aria-pressed={active}
            onClick={() => change(code)}
            className={[
              'rounded-lg px-2.5 py-1.5 text-sm font-semibold transition-colors',
              'min-h-[2.25rem] min-w-[3rem]',
              active
                ? 'bg-navy-800 text-white'
                : 'text-muted hover:bg-sand-100 hover:text-navy-800',
            ].join(' ')}
          >
            {config.nativeName}
          </button>
        );
      })}
    </div>
  );
}
