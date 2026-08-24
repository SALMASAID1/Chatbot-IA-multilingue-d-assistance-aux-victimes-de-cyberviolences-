/**
 * The message list.
 *
 * Announcements are handled by one dedicated polite live region rather than by
 * marking the whole list live: that avoids re-announcing the user's own words
 * and avoids competing with the assertive `role="alert"` used for emergencies.
 */
import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ArrowDown, Loader2 } from 'lucide-react';
import { MessageBubble } from './MessageBubble';
import type { TimelineMessage } from '@/types/api';

interface Props {
  messages: TimelineMessage[];
  isSending: boolean;
  sessionId: string | null;
  lastUrgentMessageId: string | null;
}

const NEAR_BOTTOM_PX = 120;

export function ChatTimeline({ messages, isSending, sessionId, lastUrgentMessageId }: Props) {
  const { t } = useTranslation();
  const endRef = useRef<HTMLDivElement>(null);
  const [pinnedToBottom, setPinnedToBottom] = useState(true);
  const [seenCount, setSeenCount] = useState(messages.length);

  // Track whether the reader is at the bottom; never yank them away from an
  // earlier message they may still be reading.
  useEffect(() => {
    const onScroll = () => {
      const distance = document.documentElement.scrollHeight - window.innerHeight - window.scrollY;
      setPinnedToBottom(distance <= NEAR_BOTTOM_PX);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const scrollToEnd = (behavior: ScrollBehavior = 'smooth') => {
    const node = endRef.current;
    if (node && typeof node.scrollIntoView === 'function') {
      node.scrollIntoView({ behavior, block: 'end' });
    }
    setSeenCount(messages.length);
  };

  // Adjusting state during render (the documented React pattern) instead of an
  // effect: while the reader is at the bottom, everything counts as seen.
  if (pinnedToBottom && seenCount !== messages.length) {
    setSeenCount(messages.length);
  }
  const hasUnseen = messages.length > seenCount;

  // The only effect left performs a DOM side effect and never sets state.
  useEffect(() => {
    if (!pinnedToBottom) return;
    const node = endRef.current;
    if (node && typeof node.scrollIntoView === 'function') {
      node.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [messages.length, pinnedToBottom]);

  const lastAssistant = [...messages].reverse().find((message) => message.role === 'assistant');
  // Urgent answers announce themselves through role="alert" in the panel.
  const politeAnnouncement = lastAssistant && !lastAssistant.isUrgent ? lastAssistant.content : '';

  return (
    <div className="relative">
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

      <div ref={endRef} aria-hidden="true" className="h-px" />

      {hasUnseen ? (
        <button
          type="button"
          onClick={() => scrollToEnd()}
          className="tap-target sticky bottom-4 mx-auto flex items-center gap-2 rounded-full border border-line bg-white px-4 py-2 text-sm font-semibold text-navy-800 shadow-raised"
        >
          <ArrowDown aria-hidden="true" className="size-4" />
          {t('chat.newMessages')}
        </button>
      ) : null}
    </div>
  );
}
