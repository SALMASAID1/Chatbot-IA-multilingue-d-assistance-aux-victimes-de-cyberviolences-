/**
 * Actual Markdown rendering. Loaded lazily by <SafeMarkdown> — the unified
 * toolchain is ~200 kB and the welcome screen never needs it.
 *
 * - `dangerouslySetInnerHTML` is never used (ESLint blocks it repo-wide).
 * - `rehype-raw` is deliberately NOT installed, so embedded HTML is escaped,
 *   and `rehype-sanitize` runs on top of that as defence in depth.
 * - Links are re-validated at render time against the scheme allow-list.
 */
import ReactMarkdown, { type Components } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSanitize from 'rehype-sanitize';
import { markdownSanitizeSchema } from '@/lib/security/markdown';
import { isExternalHttpUrl, safeHref } from '@/lib/security/url';

const components: Components = {
  a({ href, children, ...rest }) {
    const safe = safeHref(href);
    if (!safe) {
      // Unsupported scheme (javascript:, data:, …): keep the text, drop the link.
      return <span>{children}</span>;
    }
    const external = isExternalHttpUrl(safe);
    return (
      <a
        {...rest}
        href={safe}
        {...(external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
        className="force-ltr"
      >
        {children}
      </a>
    );
  },
};

export default function MarkdownRenderer({ children }: { children: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[[rehypeSanitize, markdownSanitizeSchema]]}
      components={components}
    >
      {children}
    </ReactMarkdown>
  );
}
