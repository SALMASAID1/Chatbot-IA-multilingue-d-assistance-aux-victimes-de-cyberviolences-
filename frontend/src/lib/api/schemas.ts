/**
 * Zod schemas validating every API response at the boundary.
 *
 * Optionality mirrors the FastAPI models: fields with server-side defaults are
 * `.optional()` here because FastAPI omits nothing but Pydantic defaults can be
 * absent in older/leaner responses; required fields stay required so a genuinely
 * malformed payload is rejected instead of silently rendering `undefined`.
 */
import { z } from 'zod';

export const sourceInfoSchema = z.object({
  path: z.string().nullish(),
  categorie: z.string().nullish(),
  score: z.number().nullish(),
});

export const chatResponseSchema = z.object({
  answer: z.string(),
  sources: z.array(sourceInfoSchema).optional().default([]),
  langue: z.string(),
  is_darija: z.boolean().optional().default(false),
  is_urgent: z.boolean().optional().default(false),
  user_profile: z.string().optional().default('victim'),
  session_id: z.string(),
  message_id: z.string(),
  timestamp: z.string().optional(),
});

export const sessionResponseSchema = z.object({
  session_id: z.string(),
  created_at: z.string(),
  langue: z.string().nullish(),
});

export const chatMessageSchema = z.object({
  role: z.string(),
  content: z.string(),
  timestamp: z.string(),
  message_id: z.string().nullish(),
});

export const chatHistorySchema = z.object({
  session_id: z.string(),
  messages: z.array(chatMessageSchema).optional().default([]),
  total_messages: z.number().optional().default(0),
});

export const feedbackResponseSchema = z.object({
  status: z.string().optional().default('received'),
  message: z.string().optional().default(''),
});

export const healthResponseSchema = z.object({
  status: z.string(),
  version: z.string(),
  rag_status: z.string(),
  llm_status: z.string().optional().default('unknown'),
  active_sessions: z.number().optional().default(0),
  uptime_seconds: z.number().optional().default(0),
});

/** FastAPI/HTTPException error envelope. `detail` may also be a 422 array. */
export const errorResponseSchema = z.object({
  detail: z.union([z.string(), z.array(z.unknown()), z.unknown()]).optional(),
  error_code: z.string().nullish(),
});
