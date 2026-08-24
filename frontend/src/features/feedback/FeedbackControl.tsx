/**
 * Two-option feedback bound to POST /api/chat/feedback.
 *
 * The endpoint takes a 1-5 rating; a binary control is far gentler for someone
 * in distress than a five-star widget, so "helpful" maps to 5 and
 * "not helpful" to 1. Never retried, and it fails quietly.
 */
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ThumbsDown, ThumbsUp } from 'lucide-react';
import { useFeedback } from '@/lib/api/queries';

interface Props {
  sessionId: string | null;
  exchangeId: string | undefined;
}

export function FeedbackControl({ sessionId, exchangeId }: Props) {
  const { t } = useTranslation();
  const [submitted, setSubmitted] = useState(false);
  const [failed, setFailed] = useState(false);
  const feedback = useFeedback();

  if (!sessionId || !exchangeId) return null;

  const submit = (rating: number) => {
    setFailed(false);
    feedback.mutate(
      { session_id: sessionId, message_id: exchangeId, rating },
      {
        onSuccess: () => setSubmitted(true),
        onError: () => setFailed(true),
      },
    );
  };

  if (submitted) {
    return (
      <p role="status" className="mt-2 text-xs font-medium text-teal-700">
        {t('feedback.thanks')}
      </p>
    );
  }

  const buttonClass =
    'tap-target inline-flex items-center gap-1.5 rounded-lg border border-line px-2.5 py-1.5 text-xs font-semibold text-muted transition-colors hover:border-teal-200 hover:bg-teal-50 hover:text-teal-700 disabled:opacity-60';

  return (
    <div className="mt-2 flex flex-wrap items-center gap-2">
      <span className="text-xs text-muted">{t('feedback.question')}</span>
      <button
        type="button"
        onClick={() => submit(5)}
        disabled={feedback.isPending}
        className={buttonClass}
      >
        <ThumbsUp aria-hidden="true" className="size-3.5" />
        {t('feedback.helpful')}
      </button>
      <button
        type="button"
        onClick={() => submit(1)}
        disabled={feedback.isPending}
        className={buttonClass}
      >
        <ThumbsDown aria-hidden="true" className="size-3.5" />
        {t('feedback.notHelpful')}
      </button>
      {failed ? (
        <span role="status" className="text-xs text-coral-600">
          {t('feedback.failed')}
        </span>
      ) : null}
    </div>
  );
}
