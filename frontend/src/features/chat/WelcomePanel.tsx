import { useTranslation } from 'react-i18next';
import { EyeOff, TriangleAlert } from 'lucide-react';
import { SuggestionCards } from './SuggestionCards';
import { WelcomeIllustration } from './WelcomeIllustration';

export function WelcomePanel({ onSelectSuggestion }: { onSelectSuggestion: (p: string) => void }) {
  const { t } = useTranslation();

  return (
    <div className="animate-rise space-y-4 pb-2">
      <section className="card overflow-hidden">
        <WelcomeIllustration className="h-28 w-full sm:h-36" />
        <div className="p-4 sm:p-5">
          <h1 className="text-xl font-extrabold text-navy-800 sm:text-2xl">
            {t('welcome.greeting')}
          </h1>
          <p className="mt-2 text-[0.95rem] text-navy-800">{t('welcome.intro')}</p>
          <p className="mt-2 text-sm text-muted">{t('welcome.howToStart')}</p>
        </div>
      </section>

      <SuggestionCards onSelect={onSelectSuggestion} />

      <div className="grid gap-2 sm:grid-cols-2">
        <section
          aria-labelledby="privacy-heading"
          className="rounded-xl border border-line bg-white p-3"
        >
          <h2
            id="privacy-heading"
            className="mb-1 flex items-center gap-2 text-sm font-bold text-navy-800"
          >
            <EyeOff aria-hidden="true" className="size-4 text-teal-700" />
            {t('welcome.privacyTitle')}
          </h2>
          <p className="text-xs leading-relaxed text-muted">{t('welcome.privacyBody')}</p>
        </section>

        <section
          aria-labelledby="disclaimer-heading"
          className="rounded-xl border border-coral-200 bg-coral-50 p-3"
        >
          <h2
            id="disclaimer-heading"
            className="mb-1 flex items-center gap-2 text-sm font-bold text-navy-800"
          >
            <TriangleAlert aria-hidden="true" className="size-4 text-coral-600" />
            {t('welcome.disclaimerTitle')}
          </h2>
          <p className="text-xs leading-relaxed text-navy-800">{t('welcome.disclaimerBody')}</p>
        </section>
      </div>
    </div>
  );
}
