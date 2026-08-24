import { useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ArrowDown, Loader2 } from 'lucide-react';
import { ChatComposer } from './ChatComposer';
import { ChatNotice } from './ChatNotice';
import { ChatTimeline } from './ChatTimeline';
import { WelcomePanel } from './WelcomePanel';
import { ConfirmDialog } from '@/components/ConfirmDialog';
import { useChatController } from './useChatController';
import { useConversationScroll } from './useConversationScroll';

interface Props {
  /** Bumped by the shell when "New conversation" is requested from the header. */
  newConversationToken: number;
}

export function ChatView({ newConversationToken }: Props) {
  const { t } = useTranslation();
  const chat = useChatController();
  const scroll = useConversationScroll(chat.messages.length);
  const [pendingPrompt, setPendingPrompt] = useState<string | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [resetToken, setResetToken] = useState(0);
  const [handledToken, setHandledToken] = useState(newConversationToken);

  // "New conversation" only interrupts with a confirmation when there is
  // something meaningful to lose.
  if (newConversationToken !== handledToken) {
    setHandledToken(newConversationToken);
    if (chat.hasConversation) {
      setConfirmOpen(true);
    } else {
      setPendingPrompt(null);
    }
  }

  const confirmReset = useCallback(() => {
    chat.reset();
    setConfirmOpen(false);
    setResetToken((token) => token + 1);
  }, [chat]);

  return (
    <>
      {chat.notice ? (
        <ChatNotice notice={chat.notice} onRetry={chat.retryLast} onDismiss={chat.dismissNotice} />
      ) : null}

      {chat.isLoadingHistory ? (
        <p className="flex items-center gap-2 py-6 text-sm text-muted">
          <Loader2 aria-hidden="true" className="size-4 animate-spin" />
          {t('chat.loadingHistory')}
        </p>
      ) : null}

      {chat.hasConversation ? (
        <ChatTimeline
          messages={chat.messages}
          isSending={chat.isSending}
          sessionId={chat.sessionId}
          lastUrgentMessageId={chat.lastUrgentMessageId}
          containerRef={scroll.containerRef}
        />
      ) : (
        <WelcomePanel onSelectSuggestion={setPendingPrompt} />
      )}

      {/* One sticky footer holds both affordances, so the "new answer" button
          can never sit underneath the composer. */}
      <div className="sticky bottom-0 z-20 -mx-4 border-t border-line bg-sand-50/95 px-4 backdrop-blur-sm">
        {scroll.hasUnseen ? (
          <div className="flex justify-center pt-3">
            <button
              type="button"
              onClick={() => scroll.scrollToBottom('smooth')}
              className="tap-target flex items-center gap-2 rounded-full border border-line bg-white px-4 py-2 text-sm font-semibold text-navy-800 shadow-raised"
            >
              <ArrowDown aria-hidden="true" className="size-4" />
              {t('chat.newMessages')}
            </button>
          </div>
        ) : null}

        <ChatComposer
          onSend={chat.send}
          onCancel={chat.cancel}
          isSending={chat.isSending}
          pendingPrompt={pendingPrompt}
          onPendingPromptConsumed={() => setPendingPrompt(null)}
          resetToken={resetToken}
        />
      </div>

      <ConfirmDialog
        open={confirmOpen}
        title={t('newConversation.confirmTitle')}
        body={t('newConversation.confirmBody')}
        confirmLabel={t('newConversation.confirm')}
        cancelLabel={t('newConversation.cancel')}
        onConfirm={confirmReset}
        onCancel={() => setConfirmOpen(false)}
      />
    </>
  );
}
