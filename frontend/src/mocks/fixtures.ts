/**
 * Fixtures mirroring real backend payloads.
 *
 * Field shapes and the naive-UTC timestamp format ("…T10:00:00.000000", no Z)
 * match what FastAPI actually returns from `datetime.utcnow()`.
 */
import type { ChatResponse, HealthResponse } from '@/types/api';

export const SESSION_ID = '550e8400-e29b-41d4-a716-446655440000';

export const healthyHealth: HealthResponse = {
  status: 'healthy',
  version: '1.0.0',
  rag_status: 'healthy',
  llm_status: 'configured',
  active_sessions: 1,
  uptime_seconds: 128.5,
};

export const degradedHealth: HealthResponse = {
  ...healthyHealth,
  status: 'degraded',
  rag_status: 'empty',
  llm_status: 'unconfigured',
};

export const frenchAnswer: ChatResponse = {
  answer:
    "Vous n'êtes pas responsable de ce qui vous arrive.\n\n" +
    '- Conservez les preuves (captures d’écran).\n' +
    '- Signalez le compte sur le réseau social.\n' +
    '- Signalement : [eVigilance](https://evigilance.ma/fr/signaler)\n',
  sources: [
    { path: 'fiches_pratiques/cyberharcelement.md', categorie: 'fiches_pratiques', score: 0.82 },
    { path: 'juridique/loi_103_13.md', categorie: 'juridique', score: 0.61 },
  ],
  langue: 'fr',
  is_darija: false,
  is_urgent: false,
  user_profile: 'victim',
  session_id: SESSION_ID,
  message_id: 'msg-abc123def456',
  timestamp: '2026-08-24T10:00:00.000000',
};

export const arabicAnswer: ChatResponse = {
  ...frenchAnswer,
  answer: 'لست مسؤولا عما وقع لك.\n\n- احتفظ بالأدلة.\n- بلّغ عن الحساب داخل الشبكة الاجتماعية.',
  langue: 'ar',
  is_darija: false,
  sources: [
    { path: 'fiches_pratiques/cyberharcelement.md', categorie: 'fiches_pratiques', score: 0.74 },
  ],
  message_id: 'msg-ar0001',
};

export const darijaAnswer: ChatResponse = {
  ...arabicAnswer,
  answer: 'ما كاين باس، غادي نعاونك خطوة بخطوة.',
  is_darija: true,
  message_id: 'msg-ary001',
};

/** Mirrors backend/config.py EMERGENCY_RESPONSE_FR. */
export const urgentAnswer: ChatResponse = {
  ...frenchAnswer,
  answer:
    'Si vous etes en danger immediat, appelez les autorites tout de suite :\n' +
    '- Police : 19 (en ville)\n' +
    '- Gendarmerie Royale : 177 (en zone rurale)\n' +
    '- Protection Civile : 15 (urgence medicale)\n' +
    '- ONDE : 2511 (si la victime est un enfant)\n\n' +
    "Vous n'etes pas seul(e). L'aide est disponible 24h/24.",
  sources: [],
  is_urgent: true,
  user_profile: 'detresse_emotionnelle',
  message_id: 'msg-urgent01',
};

/** Sources with no path/score at all — every field is optional server-side. */
export const answerWithBareSources: ChatResponse = {
  ...frenchAnswer,
  sources: [{ categorie: 'ressources' }, {}],
  message_id: 'msg-bare01',
};

export const answerWithHostileMarkdown: ChatResponse = {
  ...frenchAnswer,
  answer:
    'Voici de l’aide.\n\n' +
    '<script>window.__pwned = true;</script>\n\n' +
    '<img src=x onerror="window.__pwned = true" />\n\n' +
    '[Lien piégé](javascript:alert(1))\n\n' +
    '[Signalement officiel](https://evigilance.ma/fr/signaler)\n',
  message_id: 'msg-xss01',
};
