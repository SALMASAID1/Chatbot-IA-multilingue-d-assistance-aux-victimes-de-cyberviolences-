import { useTranslation } from 'react-i18next';
import { Dialog } from '@/components/Dialog';
import { EmergencyContacts } from '@/features/emergency/EmergencyContacts';

export function HelpDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { t } = useTranslation();

  return (
    <Dialog open={open} onClose={onClose} title={t('help.title')}>
      <section>
        <h3 className="mb-1 font-bold text-navy-800">{t('help.aboutTitle')}</h3>
        <p className="text-muted">{t('help.aboutBody')}</p>
      </section>
      <section>
        <h3 className="mb-1 font-bold text-navy-800">{t('help.limitsTitle')}</h3>
        <p className="text-muted">{t('help.limitsBody')}</p>
      </section>
      <section>
        <h3 className="mb-1 font-bold text-navy-800">{t('help.privacyTitle')}</h3>
        <p className="text-muted">{t('help.privacyBody')}</p>
      </section>
      <section>
        <h3 className="mb-1 font-bold text-navy-800">{t('help.safetyTitle')}</h3>
        <p className="mb-3 text-muted">{t('help.safetyBody')}</p>
        <EmergencyContacts />
      </section>
    </Dialog>
  );
}
