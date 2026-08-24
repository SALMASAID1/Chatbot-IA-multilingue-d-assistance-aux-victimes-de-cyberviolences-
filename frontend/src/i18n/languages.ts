import type { SupportedLanguage, UiLanguage } from '@/types/api';

export interface LanguageConfig {
  /** UI language code (also the i18next resource key). */
  code: UiLanguage;
  /** Value for <html lang>. Darija's BCP-47 tag is `ary`. */
  htmlLang: string;
  dir: 'ltr' | 'rtl';
  /** Native name shown in the switcher. */
  nativeName: string;
  /** Intl locale used for dates/numbers. */
  locale: string;
  /**
   * How this UI language maps onto the backend's `langue` enum, which only
   * accepts "fr" | "ar". Darija is served by the Arabic pipeline.
   */
  apiLangue: SupportedLanguage;
}

export const LANGUAGES: Record<UiLanguage, LanguageConfig> = {
  fr: {
    code: 'fr',
    htmlLang: 'fr',
    dir: 'ltr',
    nativeName: 'Français',
    locale: 'fr-MA',
    apiLangue: 'fr',
  },
  ar: {
    code: 'ar',
    htmlLang: 'ar',
    dir: 'rtl',
    nativeName: 'العربية',
    locale: 'ar-MA',
    apiLangue: 'ar',
  },
  ary: {
    code: 'ary',
    htmlLang: 'ary',
    dir: 'rtl',
    nativeName: 'الدارجة',
    locale: 'ar-MA',
    apiLangue: 'ar',
  },
};

export const UI_LANGUAGES: UiLanguage[] = ['fr', 'ar', 'ary'];

export const DEFAULT_LANGUAGE: UiLanguage = 'fr';

export function isUiLanguage(value: string | null | undefined): value is UiLanguage {
  return value === 'fr' || value === 'ar' || value === 'ary';
}

export function getLanguageConfig(code: string | null | undefined): LanguageConfig {
  return isUiLanguage(code) ? LANGUAGES[code] : LANGUAGES[DEFAULT_LANGUAGE];
}

/**
 * Direction for a *message*, based on the language the backend answered in.
 * Arabic-script content is RTL; French is LTR.
 */
export function directionForMessageLanguage(langue: string | undefined): 'ltr' | 'rtl' {
  return langue === 'ar' ? 'rtl' : 'ltr';
}

/**
 * Heuristic used only for display direction of a *user's own* message.
 * Arabizi ("wach n9der...") is Latin script and must stay LTR even when the
 * interface is Arabic, otherwise the text renders reversed.
 */
export function detectTextDirection(text: string): 'ltr' | 'rtl' {
  const arabic = text.match(/[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]/g)?.length ?? 0;
  const latin = text.match(/[A-Za-z]/g)?.length ?? 0;
  return arabic > latin ? 'rtl' : 'ltr';
}
