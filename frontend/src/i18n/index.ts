import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import fr from './locales/fr.json';
import ar from './locales/ar.json';
import ary from './locales/ary.json';
import { DEFAULT_LANGUAGE, UI_LANGUAGES, isUiLanguage, getLanguageConfig } from './languages';
import { readStoredLanguage } from '@/lib/security/storage';
import type { UiLanguage } from '@/types/api';

function detectInitialLanguage(): UiLanguage {
  const stored = readStoredLanguage();
  if (isUiLanguage(stored)) return stored;

  if (typeof navigator !== 'undefined') {
    for (const raw of navigator.languages ?? [navigator.language]) {
      const tag = (raw ?? '').toLowerCase();
      if (tag.startsWith('ary')) return 'ary';
      // ar-MA speakers are served Darija; other Arabic locales get MSA.
      if (tag === 'ar-ma') return 'ary';
      if (tag.startsWith('ar')) return 'ar';
      if (tag.startsWith('fr')) return 'fr';
    }
  }
  return DEFAULT_LANGUAGE;
}

/** Applies <html lang> and <html dir> — required for correct RTL rendering. */
export function applyDocumentLanguage(language: string): void {
  if (typeof document === 'undefined') return;
  const config = getLanguageConfig(language);
  document.documentElement.lang = config.htmlLang;
  document.documentElement.dir = config.dir;
}

const initialLanguage = detectInitialLanguage();

void i18n.use(initReactI18next).init({
  resources: {
    fr: { translation: fr },
    ar: { translation: ar },
    ary: { translation: ary },
  },
  lng: initialLanguage,
  fallbackLng: DEFAULT_LANGUAGE,
  supportedLngs: UI_LANGUAGES,
  interpolation: {
    // React already escapes interpolated values.
    escapeValue: false,
  },
  returnNull: false,
});

applyDocumentLanguage(initialLanguage);

export default i18n;
