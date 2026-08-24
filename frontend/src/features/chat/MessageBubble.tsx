import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Check, Copy, TriangleAlert } from 'lucide-react';
import { SafeMarkdown } from '@/components/SafeMarkdown';
import { SourceDisclosure } from './SourceDisclosure';
import { FeedbackControl } from '@/features/feedback/FeedbackControl';
import { UrgentResponsePanel } from '@/features/emergency/UrgentResponsePanel';
import { detectTextDirection, directionForMessageLanguage, LANGUAGES } from '@/i18n/languages';
import { formatTime } from '@/lib/datetime';
import type { TimelineMessage } from '@/types/api';

interface Props {
  message: TimelineMessage;
  sessionId: string | null;
  /** True for the newest urgent answer: it takes focus once. */
  focusUrgent?: boolean;
}

export function MessageBubble({ message, sessionId, focusUrgent = false }: Props) {
  const { t, i18n } = useTranslation();
  const [copied, setCopied] = useState(false);

  const time = formatTime(message.timestamp, i18n.language);

  if (message.role === 'user') {
    // Arabizi ("wach n9der...") is Latin script and must not be flipped to RTL.
    const dir = detectTextDirection(message.content);
    return (
      <li className="animate-rise flex flex-col items-end">
        <div
          dir={dir}
          className="max-w-[85%] rounded-2xl rounded-ee-md bg-navy-800 px-4 py-2.5 text-white sm:max-w-[75%]"
        >
          <span className="sr-only">{t('chat.you')}: </span>
          <p className="text-[0.95rem] whitespace-pre-wrap">{message.content}</p>
        </div>
        <div className="mt-1 flex items-center gap-2 text-[0.7rem] text-muted">
          {time ? <time className="force-ltr">{time}</time> : null}
          {message.errorKind ? (
            <span className="inline-flex items-center gap-1 text-alert-600">
              <TriangleAlert aria-hidden="true" className="size-3" />
              {t('chat.messageFailed')}
            </span>
          ) : null}
        </div>
      </li>
    );
  }

  const langue = message.langue;
  const dir = directionForMessageLanguage(langue);
  const lang = langue === 'ar' ? (message.isDarija ? 'ary' : 'ar') : 'fr';
  const interfaceLang = i18n.language;
  const showLanguageHint = lang !== interfaceLang;

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

  return (
    <li className="animate-rise flex flex-col items-start">
      <div className="w-full max-w-[95%] sm:max-w-[88%]">
        {message.isUrgent ? (
          <UrgentResponsePanel answer={message.content} langue={langue} takeFocus={focusUrgent} />
        ) : (
          <div className="card p-4">
            <span className="sr-only">{t('chat.assistant')}: </span>
            <div dir={dir} lang={lang} className="text-[0.95rem] text-navy-800">
              <SafeMarkdown>{message.content}</SafeMarkdown>
            </div>
            {message.sources ? <SourceDisclosure sources={message.sources} /> : null}
            <FeedbackControl sessionId={sessionId} exchangeId={message.exchangeId} />
          </div>
        )}

        <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-[0.7rem] text-muted">
          {time ? <time className="force-ltr">{time}</time> : null}
          {showLanguageHint ? (
            <span>
              {message.isDarija
                ? t('chat.answerLanguageDarija')
                : t('chat.answerLanguage', {
                    language: LANGUAGES[lang === 'ar' ? 'ar' : 'fr'].nativeName,
                  })}
            </span>
          ) : null}
          <button
            type="button"
            onClick={() => void copy()}
            className="tap-target inline-flex items-center gap-1 rounded-lg px-1.5 py-1 font-medium hover:bg-sand-100 hover:text-navy-800"
          >
            {copied ? (
              <Check aria-hidden="true" className="size-3.5 text-teal-700" />
            ) : (
              <Copy aria-hidden="true" className="size-3.5" />
            )}
            {copied ? t('chat.copied') : t('chat.copy')}
          </button>
        </div>
      </div>
    </li>
  );
}
