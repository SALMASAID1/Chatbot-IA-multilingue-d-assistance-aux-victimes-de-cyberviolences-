import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Header } from '@/components/Header';
import { ServiceStatusBanner } from '@/components/ServiceStatus';
import { resolveServiceState } from '@/components/serviceState';
import { ChatView } from '@/features/chat/ChatView';
import { HelpDialog } from '@/features/help/HelpDialog';
import { useHealth } from '@/lib/api/queries';
import { useOnlineStatus } from '@/lib/useOnlineStatus';

export function AppShell() {
  const { t } = useTranslation();
  const online = useOnlineStatus();
  const health = useHealth(online);
  const [helpOpen, setHelpOpen] = useState(false);
  const [newConversationToken, setNewConversationToken] = useState(0);

  const serviceState = resolveServiceState({
    online,
    isLoading: health.isLoading,
    isError: health.isError,
    data: health.data,
  });

  return (
    <div className="flex min-h-dvh flex-col">
      <a
        href="#main-content"
        className="sr-only rounded-lg bg-navy-800 px-4 py-2 font-semibold text-white focus:not-sr-only focus:absolute focus:start-3 focus:top-3 focus:z-50"
      >
        {t('app.skipToContent')}
      </a>

      <Header
        serviceState={serviceState}
        onNewConversation={() => setNewConversationToken((token) => token + 1)}
        onOpenHelp={() => setHelpOpen(true)}
      />

      <main
        id="main-content"
        aria-label={t('app.mainLabel')}
        className="flex flex-1 flex-col justify-end"
      >
        <div className="mx-auto w-full max-w-3xl flex-1 px-4 pt-4 pb-2">
          <ServiceStatusBanner state={serviceState} onShowEmergency={() => setHelpOpen(true)} />
          <ChatView newConversationToken={newConversationToken} />
        </div>
      </main>

      <footer className="border-t border-line bg-white/60 px-4 py-3">
        <p className="mx-auto max-w-3xl text-center text-xs text-muted">{t('app.footerNote')}</p>
      </footer>

      <HelpDialog open={helpOpen} onClose={() => setHelpOpen(false)} />
    </div>
  );
}
