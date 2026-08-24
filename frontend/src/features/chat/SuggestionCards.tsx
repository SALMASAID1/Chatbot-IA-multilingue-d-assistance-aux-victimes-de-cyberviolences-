import { useTranslation } from 'react-i18next';
import { FileSearch, LifeBuoy, ShieldCheck, Flag } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

const SUGGESTIONS: { id: string; icon: LucideIcon }[] = [
  { id: 'protectAccounts', icon: ShieldCheck },
  { id: 'report', icon: Flag },
  { id: 'evidence', icon: FileSearch },
  { id: 'helpOther', icon: LifeBuoy },
];

export function SuggestionCards({ onSelect }: { onSelect: (prompt: string) => void }) {
  const { t } = useTranslation();

  return (
    <section aria-labelledby="suggestions-heading">
      <h2 id="suggestions-heading" className="mb-2 text-sm font-bold text-navy-800">
        {t('welcome.suggestionsTitle')}
      </h2>
      <ul className="grid gap-2 sm:grid-cols-2">
        {SUGGESTIONS.map(({ id, icon: Icon }) => (
          <li key={id}>
            <button
              type="button"
              onClick={() => onSelect(t(`suggestions.${id}.prompt`))}
              className="tap-target group flex w-full items-start gap-3 rounded-xl border border-line bg-white p-3 text-start transition-colors hover:border-teal-200 hover:bg-teal-50"
            >
              <span
                aria-hidden="true"
                className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-teal-50 text-teal-700 group-hover:bg-white"
              >
                <Icon className="size-4" />
              </span>
              <span className="min-w-0">
                <span className="block text-sm font-bold text-navy-800">
                  {t(`suggestions.${id}.title`)}
                </span>
                <span className="block text-xs leading-snug text-muted">
                  {t(`suggestions.${id}.description`)}
                </span>
              </span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
