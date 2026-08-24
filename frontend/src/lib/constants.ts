/** Mirrors ChatRequest.message max_length in backend/api/models/schemas.py. */
export const MAX_MESSAGE_LENGTH = 2000;

/** Show the character counter only when the user gets close to the limit. */
export const CHAR_COUNTER_THRESHOLD = 1800;

/** Backend rate limit for POST /api/chat (RATE_LIMIT_CHAT default). */
export const CHAT_RATE_LIMIT_PER_MINUTE = 30;
