/**
 * Sanitization schema for assistant Markdown.
 *
 * Starts from hast-util-sanitize's default (which already strips <script>,
 * event handlers and unknown attributes) and then tightens it:
 *  - `tel:` is added so Moroccan emergency numbers stay actionable;
 *  - `xmpp:`, `irc:` and `ircs:` are removed;
 *  - images are not allowed (the assistant never returns any, and allowing them
 *    would enable remote pixel tracking of a vulnerable user).
 */
import { defaultSchema } from 'rehype-sanitize';
import type { Options as SanitizeOptions } from 'rehype-sanitize';

const baseAttributes = defaultSchema.attributes ?? {};
const baseTagNames = defaultSchema.tagNames ?? [];

export const markdownSanitizeSchema: SanitizeOptions = {
  ...defaultSchema,
  tagNames: baseTagNames.filter((tag) => tag !== 'img' && tag !== 'input'),
  protocols: {
    ...defaultSchema.protocols,
    href: ['http', 'https', 'mailto', 'tel'],
  },
  attributes: {
    ...baseAttributes,
    a: [...(baseAttributes.a ?? []), 'dir'],
    '*': ['dir', 'lang'],
  },
};
