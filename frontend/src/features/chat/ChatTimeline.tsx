/**
 * The message list — presentational only; scrolling lives in
 * `useConversationScroll` so the composer and the "new answer" affordance can
 * share one sticky footer.
 *
 * Announcements go through a single dedicated polite live region rather than
 * marking the whole list live: that avoids re-announcing the reader's own words
 * and avoids competing with the assertive `role="alert"` used for emergencies.
 */
import { useTranslation } from 'react-i18next';
import { Loader2 } from 'lucide-react';
import { MessageBubble } from './MessageBubble';
import type { TimelineMessage } from '@/types/api';

interface Props {
  messages: TimelineMessage[];
  isSending: boolean;
  sessionId: string | null;
  lastUrgentMessageId: string | null;
  containerRef: (node: HTMLDivElement | null) => void;
}

export function ChatTimeline({
  messages,
  isSending,
  sessionId,
  lastUrgentMessageId,
  containerRef,
}: Props) {
  const { t } = useTranslation();

  const lastAssistant = [...messages].reverse().find((message) => message.role === 'assistant');
  // Urgent answers announce themselves through role="alert" in the panel.
  const politeAnnouncement = lastAssistant && !lastAssistant.isUrgent ? lastAssistant.content : '';

  return (
    <div ref={containerRef}>
      <ol aria-label={t('chat.timelineLabel')} className="space-y-4">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            sessionId={sessionId}
            focusUrgent={message.id === lastUrgentMessageId}
          />
        ))}

        {isSending ? (
          <li className="flex items-center gap-2.5 text-sm text-muted">
            <Loader2 aria-hidden="true" className="size-4 animate-spin text-teal-600" />
            <span>
              {t('chat.preparing')}
              <span className="block text-xs">{t('chat.preparingHint')}</span>
            </span>
          </li>
        ) : null}
      </ol>

      {/* Single polite announcer for assistant answers and pending state. */}
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {isSending ? t('chat.preparing') : politeAnnouncement}
      </div>
    </div>
  );
}
