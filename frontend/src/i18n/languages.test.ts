import { describe, expect, it } from 'vitest';
import {
  detectTextDirection,
  directionForMessageLanguage,
  getLanguageConfig,
  isUiLanguage,
  LANGUAGES,
} from './languages';

describe('language configuration', () => {
  it('maps Darija onto the Arabic backend pipeline', () => {
    expect(LANGUAGES.ary.apiLangue).toBe('ar');
    expect(LANGUAGES.ary.dir).toBe('rtl');
    expect(LANGUAGES.ary.htmlLang).toBe('ary');
  });

  it('keeps French left-to-right', () => {
    expect(LANGUAGES.fr.dir).toBe('ltr');
  });

  it('falls back to French for unknown codes', () => {
    expect(getLanguageConfig('de').code).toBe('fr');
    expect(isUiLanguage('de')).toBe(false);
    expect(isUiLanguage('ary')).toBe(true);
  });

  it('derives message direction from the answer language', () => {
    expect(directionForMessageLanguage('ar')).toBe('rtl');
    expect(directionForMessageLanguage('fr')).toBe('ltr');
    expect(directionForMessageLanguage(undefined)).toBe('ltr');
  });
});

describe('per-message direction', () => {
  it('renders Arabic-script text right-to-left', () => {
    expect(detectTextDirection('أنا ضحية ابتزاز جنسي')).toBe('rtl');
  });

  it('keeps Arabizi Darija left-to-right so it is not reversed', () => {
    expect(detectTextDirection('wach n9der ndir chi chikaya?')).toBe('ltr');
    expect(detectTextDirection('ana ma9hora o knbki chno ndir')).toBe('ltr');
  });

  it('keeps French left-to-right', () => {
    expect(detectTextDirection('Je suis victime de cyberharcèlement')).toBe('ltr');
  });

  it('follows the dominant script in mixed content', () => {
    expect(detectTextDirection('التبليغ عبر eVigilance فالمغرب دابا')).toBe('rtl');
  });
});
