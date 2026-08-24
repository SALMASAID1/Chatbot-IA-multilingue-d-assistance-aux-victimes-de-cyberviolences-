/**
 * The single entry point for rendering assistant text.
 *
 * While the Markdown chunk loads, the raw text is shown as escaped plain text
 * with preserved line breaks — so an emergency answer is legible immediately
 * and nothing is ever hidden behind a spinner.
 */
import { Suspense, lazy } from 'react';

const MarkdownRenderer = lazy(() => import('./MarkdownRenderer'));

export function SafeMarkdown({ children }: { children: string }) {
  return (
    <div className="prose-answer">
      <Suspense fallback={<p className="whitespace-pre-wrap">{children}</p>}>
        <MarkdownRenderer>{children}</MarkdownRenderer>
      </Suspense>
    </div>
  );
}
