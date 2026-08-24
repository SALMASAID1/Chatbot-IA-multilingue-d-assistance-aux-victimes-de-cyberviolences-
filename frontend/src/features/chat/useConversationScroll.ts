/**
 * Keeps the page following the conversation without ever fighting the reader.
 *
 * Three things make this non-trivial here:
 *  1. The answer is rendered by a lazily-loaded Markdown chunk, so the page
 *     keeps growing *after* the message is added — scrolling once, immediately,
 *     lands far short of the bottom. A ResizeObserver keeps up with the growth.
 *  2. Auto-scrolling must react to *new content only*. Reacting to the
 *     "am I near the bottom" flag made the page yank itself whenever the reader
 *     scrolled close to the end.
 *  3. The scroll target is the document bottom, not a sentinel element: the
 *     composer is sticky, so anything aligned to the viewport bottom ends up
 *     hidden behind it.
 */
import { useCallback, useEffect, useRef, useState } from 'react';

/** How close to the bottom still counts as "following the conversation". */
const NEAR_BOTTOM_PX = 120;

export interface ConversationScroll {
  /**
   * Attach to the element wrapping the messages.
   *
   * A *callback* ref, not an object ref: the timeline only mounts once the
   * first message exists, so an effect running at mount time would observe
   * `null` and never re-attach — which is exactly how the first answer used to
   * strand the reader near the top of the page.
   */
  containerRef: (node: HTMLDivElement | null) => void;
  /** A newer message arrived while the reader was further up. */
  hasUnseen: boolean;
  scrollToBottom: (behavior?: ScrollBehavior) => void;
}

function distanceFromBottom(): number {
  return document.documentElement.scrollHeight - window.innerHeight - window.scrollY;
}

export function useConversationScroll(messageCount: number): ConversationScroll {
  const observerRef = useRef<ResizeObserver | null>(null);
  // Mirrored in a ref so the follow effect does not depend on it and therefore
  // never re-fires just because the reader moved.
  const pinnedRef = useRef(true);
  const [pinned, setPinned] = useState(true);
  const [seenCount, setSeenCount] = useState(messageCount);
  const lastFollowedCount = useRef(messageCount);

  const scrollToBottom = useCallback((behavior: ScrollBehavior = 'auto') => {
    if (typeof window.scrollTo !== 'function') return;
    window.scrollTo({ top: document.documentElement.scrollHeight, behavior });
    pinnedRef.current = true;
  }, []);

  useEffect(() => {
    // Only a real scroll changes whether we are following. Measuring at mount
    // would switch following *off* whenever the welcome panel happens to be
    // taller than the viewport — before the reader has touched anything — and
    // the conversation would then never scroll into view.
    const onScroll = () => {
      const near = distanceFromBottom() <= NEAR_BOTTOM_PX;
      pinnedRef.current = near;
      setPinned(near);
    };
    // A resize (notably the mobile keyboard opening) must not be mistaken for
    // the reader scrolling away; if we were following, keep following.
    const onResize = () => {
      if (pinnedRef.current) scrollToBottom('auto');
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onResize);
    return () => {
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onResize);
    };
  }, [scrollToBottom]);

  // New content only — `pinned` is deliberately absent from the dependencies.
  useEffect(() => {
    if (messageCount === lastFollowedCount.current) return;
    lastFollowedCount.current = messageCount;
    if (pinnedRef.current) scrollToBottom('auto');
  }, [messageCount, scrollToBottom]);

  // Markdown loads and images reflow after the fact: keep up while following.
  const containerRef = useCallback(
    (node: HTMLDivElement | null) => {
      observerRef.current?.disconnect();
      observerRef.current = null;
      if (!node || typeof ResizeObserver === 'undefined') return;
      const observer = new ResizeObserver(() => {
        if (pinnedRef.current) scrollToBottom('auto');
      });
      observer.observe(node);
      observerRef.current = observer;
    },
    [scrollToBottom],
  );

  useEffect(() => () => observerRef.current?.disconnect(), []);

  // Adjusting state during render (the documented React pattern): while the
  // reader is at the bottom, everything on screen counts as seen.
  if (pinned && seenCount !== messageCount) {
    setSeenCount(messageCount);
  }

  return {
    containerRef,
    hasUnseen: messageCount > seenCount,
    scrollToBottom,
  };
}
