/**
 * Compact identity bar.
 *
 * No official EMC logo asset is present in the repository, so the brand is a
 * text wordmark with a Lucide shield — no protected mark is imitated.
 */
import { useEffect, useId, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LifeBuoy, Menu, MessageSquarePlus, ShieldCheck, X } from 'lucide-react';
import { LanguageSwitcher } from './LanguageSwitcher';
import { ServiceStatus } from './ServiceStatus';
import type { ServiceState } from './serviceState';

interface Props {
  serviceState: ServiceState;
  onNewConversation: () => void;
  onOpenHelp: () => void;
}

export function Header({ serviceState, onNewConversation, onOpenHelp }: Props) {
  const { t } = useTranslation();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuId = useId();
  const menuRef = useRef<HTMLDivElement>(null);
  const toggleRef = useRef<HTMLButtonElement>(null);

  // Close the mobile menu on Escape or when focus/pointer leaves it.
  useEffect(() => {
    if (!menuOpen) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setMenuOpen(false);
        toggleRef.current?.focus();
      }
    };
    const onPointer = (event: PointerEvent) => {
      const target = event.target as Node;
      if (!menuRef.current?.contains(target) && !toggleRef.current?.contains(target)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener('keydown', onKey);
    document.addEventListener('pointerdown', onPointer);
    return () => {
      document.removeEventListener('keydown', onKey);
      document.removeEventListener('pointerdown', onPointer);
    };
  }, [menuOpen]);

  const actionClass =
    'tap-target inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-semibold text-navy-800 transition-colors hover:bg-sand-100';

  return (
    <header className="sticky top-0 z-30 border-b border-line bg-sand-50/90 backdrop-blur-sm">
      <div className="mx-auto flex w-full max-w-5xl items-center gap-3 px-4 py-2.5">
        <div className="flex min-w-0 flex-1 items-center gap-2.5">
          <span
            aria-hidden="true"
            className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-navy-800 text-white"
          >
            <ShieldCheck className="size-5" />
          </span>
          <div className="min-w-0">
            <p className="force-ltr truncate text-[0.95rem] leading-tight font-extrabold text-navy-800">
              EMC Helpline
            </p>
            <p className="truncate text-xs leading-tight text-muted">{t('app.subtitle')}</p>
          </div>
        </div>

        {/* Desktop actions */}
        <div className="hidden items-center gap-2 md:flex">
          <ServiceStatus state={serviceState} />
          <LanguageSwitcher />
          <button type="button" onClick={onNewConversation} className={actionClass}>
            <MessageSquarePlus aria-hidden="true" className="size-4" />
            {t('header.newConversation')}
          </button>
          <button type="button" onClick={onOpenHelp} className={actionClass}>
            <LifeBuoy aria-hidden="true" className="size-4" />
            {t('header.help')}
          </button>
        </div>

        {/* Mobile disclosure */}
        <button
          ref={toggleRef}
          type="button"
          onClick={() => setMenuOpen((open) => !open)}
          aria-expanded={menuOpen}
          aria-controls={menuId}
          className="tap-target inline-flex items-center justify-center rounded-xl border border-line bg-white text-navy-800 md:hidden"
        >
          {menuOpen ? (
            <X aria-hidden="true" className="size-5" />
          ) : (
            <Menu aria-hidden="true" className="size-5" />
          )}
          <span className="sr-only">{menuOpen ? t('header.closeMenu') : t('header.openMenu')}</span>
        </button>
      </div>

      {menuOpen ? (
        <div
          ref={menuRef}
          id={menuId}
          aria-label={t('header.menuLabel')}
          className="border-t border-line bg-white px-4 py-3 md:hidden"
        >
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <ServiceStatus state={serviceState} />
            <LanguageSwitcher />
          </div>
          <div className="flex flex-col">
            <button
              type="button"
              onClick={() => {
                setMenuOpen(false);
                onNewConversation();
              }}
              className={`${actionClass} justify-start`}
            >
              <MessageSquarePlus aria-hidden="true" className="size-4" />
              {t('header.newConversation')}
            </button>
            <button
              type="button"
              onClick={() => {
                setMenuOpen(false);
                onOpenHelp();
              }}
              className={`${actionClass} justify-start`}
            >
              <LifeBuoy aria-hidden="true" className="size-4" />
              {t('header.help')}
            </button>
          </div>
        </div>
      ) : null}
    </header>
  );
}
