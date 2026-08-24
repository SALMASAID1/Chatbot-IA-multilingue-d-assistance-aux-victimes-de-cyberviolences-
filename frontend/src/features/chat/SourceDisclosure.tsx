/**
 * Collapsible list of the knowledge-base extracts behind an answer.
 *
 * The backend's SourceInfo carries exactly three optional fields — path,
 * categorie, score. There is no URL in the contract, so none is rendered:
 * inventing a citation link for a legal-advice product would be indefensible.
 */
import { useTranslation } from 'react-i18next';
import { BookOpen, ChevronDown } from 'lucide-react';
import type { SourceInfo } from '@/types/api';

function formatScore(score: number | null | undefined, locale: string): string | null {
  if (typeof score !== 'number' || Number.isNaN(score)) return null;
  const clamped = Math.max(0, Math.min(1, score));
  try {
    return new Intl.NumberFormat(locale === 'ary' ? 'ar-MA' : locale, {
      style: 'percent',
      maximumFractionDigits: 0,
      numberingSystem: 'latn',
    }).format(clamped);
  } catch {
    return `${Math.round(clamped * 100)}%`;
  }
}

export function SourceDisclosure({ sources }: { sources: SourceInfo[] }) {
  const { t, i18n } = useTranslation();
  if (sources.length === 0) return null;

  return (
    <details className="group mt-3 rounded-xl border border-line bg-sand-50/70">
      <summary className="tap-target flex cursor-pointer list-none items-center gap-2 px-3 py-2 text-xs font-semibold text-navy-800">
        <BookOpen aria-hidden="true" className="size-3.5 shrink-0 text-teal-700" />
        <span className="flex-1">{t('chat.sourcesCount', { count: sources.length })}</span>
        <ChevronDown
          aria-hidden="true"
          className="size-4 shrink-0 transition-transform group-open:rotate-180"
        />
      </summary>
      <div className="border-t border-line px-3 py-2">
        <p className="mb-2 text-xs text-muted">{t('chat.sourcesNote')}</p>
        <ul className="space-y-1.5">
          {sources.map((source, index) => {
            const score = formatScore(source.score, i18n.language);
            return (
              <li key={`${source.path ?? 'source'}-${index}`} className="text-xs">
                <span className="force-ltr block font-medium break-words text-navy-800">
                  {source.path ?? t('chat.sourceNoPath')}
                </span>
                <span className="text-muted">
                  {source.categorie ? (
                    <>
                      {t('chat.sourceCategory')}: {source.categorie}
                    </>
                  ) : null}
                  {source.categorie && score ? ' · ' : null}
                  {score ? (
                    <>
                      {t('chat.sourceRelevance')}: <span className="force-ltr">{score}</span>
                    </>
                  ) : null}
                </span>
              </li>
            );
          })}
        </ul>
      </div>
    </details>
  );
}
