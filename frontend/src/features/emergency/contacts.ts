/**
 * Verified emergency and reporting contacts.
 *
 * These mirror the values already defined by the backend
 * (backend/config.py EMERGENCY_RESPONSE_FR/AR and the system prompts) so the UI
 * can offer actionable `tel:` links without parsing free-text answers. They are
 * shown even when the API is unreachable — that is the point of duplicating them.
 */
export interface PhoneContact {
  kind: 'phone';
  id: string;
  /** i18n key under `emergency.` */
  labelKey: string;
  number: string;
}

export interface LinkContact {
  kind: 'link';
  id: string;
  labelKey: string;
  name: string;
  url: string;
}

export type EmergencyContact = PhoneContact | LinkContact;

export const EMERGENCY_PHONES: PhoneContact[] = [
  { kind: 'phone', id: 'police', labelKey: 'emergency.police', number: '19' },
  { kind: 'phone', id: 'gendarmerie', labelKey: 'emergency.gendarmerie', number: '177' },
  {
    kind: 'phone',
    id: 'civil-protection',
    labelKey: 'emergency.civilProtection',
    number: '15',
  },
  { kind: 'phone', id: 'onde', labelKey: 'emergency.onde', number: '2511' },
];

export const SUPPORT_LINKS: LinkContact[] = [
  {
    kind: 'link',
    id: 'emc',
    labelKey: 'emergency.emc',
    name: 'EMC-Helpline',
    url: 'https://www.cyberconfiance.ma',
  },
  {
    kind: 'link',
    id: 'evigilance',
    labelKey: 'emergency.evigilance',
    name: 'eVigilance',
    url: 'https://evigilance.ma/fr/signaler',
  },
];
