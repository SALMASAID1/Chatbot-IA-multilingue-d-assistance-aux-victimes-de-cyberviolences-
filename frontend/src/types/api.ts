/**
 * Types mirroring the FastAPI contract exactly.
 *
 * Source of truth: backend/api/models/schemas.py, cross-checked against the
 * generated OpenAPI document. Fields that are optional/defaulted server-side
 * are optional here too — nothing is invented.
 */
import type { z } from 'zod';
import type {
  chatHistorySchema,
  chatMessageSchema,
  chatResponseSchema,
  feedbackResponseSchema,
  healthResponseSchema,
  sessionResponseSchema,
  sourceInfoSchema,
} from '@/lib/api/schemas';

/** The backend only accepts these two values as a `langue` override. */
export type SupportedLanguage = 'fr' | 'ar';

/** UI languages. Darija shares the Arabic pipeline server-side. */
export type UiLanguage = 'fr' | 'ar' | 'ary';

export type SourceInfo = z.infer<typeof sourceInfoSchema>;
export type ChatResponse = z.infer<typeof chatResponseSchema>;
export type SessionResponse = z.infer<typeof sessionResponseSchema>;
export type ChatMessage = z.infer<typeof chatMessageSchema>;
export type ChatHistory = z.infer<typeof chatHistorySchema>;
export type FeedbackResponse = z.infer<typeof feedbackResponseSchema>;
export type HealthResponse = z.infer<typeof healthResponseSchema>;

export interface ChatRequestBody {
  message: string;
  session_id?: string | null;
  langue?: SupportedLanguage | null;
}

export interface FeedbackRequestBody {
  session_id: string;
  message_id: string;
  rating: number;
  comment?: string | null;
}

/**
 * Internal-only classification returned by the backend. Deliberately NOT
 * surfaced as a user-visible label — see docs/decisions in the README.
 */
export type UserProfile =
  'victim' | 'parent' | 'enseignant' | 'temoin' | 'jeune' | 'detresse_emotionnelle' | (string & {});

/** A message as held in local UI state. */
export interface TimelineMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  /** Language of this specific message, when known (assistant messages). */
  langue?: SupportedLanguage;
  isUrgent?: boolean;
  isDarija?: boolean;
  sources?: SourceInfo[];
  /** Exchange id used for the feedback endpoint. */
  exchangeId?: string;
  /** Set when the assistant turn failed, so the UI can explain it inline. */
  errorKind?: string;
}
