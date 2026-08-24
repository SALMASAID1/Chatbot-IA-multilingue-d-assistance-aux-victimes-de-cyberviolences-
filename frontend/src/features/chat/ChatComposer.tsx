/**
 * Message composer.
 *
 * Notable choices:
 *  - No `maxLength` on the textarea: silently truncating someone's account of
 *    what happened to them is worse than showing a clear, localized limit
 *    message, so over-long input is validated rather than clipped.
 *  - Enter sends, Shift+Enter inserts a newline.
 *  - The draft is component state only — it is never written to storage, and it
 *    survives an expired session being replaced underneath it.
 */
import { useEffect, useId, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useTranslation } from 'react-i18next';
import { z } from 'zod';
import { Send, Square } from 'lucide-react';
import { CHAR_COUNTER_THRESHOLD, MAX_MESSAGE_LENGTH } from '@/lib/constants';

const schema = z.object({
  message: z
    .string()
    .trim()
    .min(1, { message: 'composer.emptyMessage' })
    .max(MAX_MESSAGE_LENGTH, { message: 'composer.tooLong' }),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  onSend: (message: string) => void;
  onCancel: () => void;
  isSending: boolean;
  /** Text pushed in from a suggestion card. */
  pendingPrompt?: string | null;
  onPendingPromptConsumed?: () => void;
  /** Bumped by the parent to clear the draft on "new conversation". */
  resetToken?: number;
}

export function ChatComposer({
  onSend,
  onCancel,
  isSending,
  pendingPrompt,
  onPendingPromptConsumed,
  resetToken = 0,
}: Props) {
  const { t } = useTranslation();
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const hintId = useId();
  const errorId = useId();
  const counterId = useId();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { message: '' },
    mode: 'onSubmit',
  });

  // React Compiler cannot memoize react-hook-form's watch(); this component is
  // a leaf that re-renders per keystroke by design, so skipping memoization here
  // is harmless and no memoized value is derived from it.
  // eslint-disable-next-line react-hooks/incompatible-library
  const message = watch('message') ?? '';
  const { ref: registerRef, ...messageField } = register('message');

  // Auto-grow, capped so the composer never swallows the conversation.
  useEffect(() => {
    const node = textareaRef.current;
    if (!node) return;
    node.style.height = 'auto';
    node.style.height = `${Math.min(node.scrollHeight, 200)}px`;
  }, [message]);

  useEffect(() => {
    if (!pendingPrompt) return;
    setValue('message', pendingPrompt, { shouldValidate: false });
    textareaRef.current?.focus();
    onPendingPromptConsumed?.();
  }, [pendingPrompt, setValue, onPendingPromptConsumed]);

  useEffect(() => {
    if (resetToken > 0) reset({ message: '' });
  }, [resetToken, reset]);

  const submit = handleSubmit((values) => {
    onSend(values.message);
    reset({ message: '' });
    // Keep focus in the composer: the answer is announced politely instead.
    textareaRef.current?.focus();
  });

  const onKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault();
      void submit();
    }
  };

  const remaining = MAX_MESSAGE_LENGTH - message.length;
  const showCounter = message.length >= CHAR_COUNTER_THRESHOLD;
  const isEmpty = message.trim().length === 0;
  const errorKey = errors.message?.message;

  const describedBy =
    [hintId, showCounter ? counterId : null, errorKey ? errorId : null].filter(Boolean).join(' ') ||
    undefined;

  return (
    <form
      onSubmit={(event) => void submit(event)}
      className="sticky bottom-0 z-20 border-t border-line bg-sand-50/95 pt-3 pb-3 backdrop-blur-sm"
    >
      <div className="mx-auto w-full max-w-3xl px-4">
        <div className="card flex items-end gap-2 p-2">
          <label htmlFor="chat-message" className="sr-only">
            {t('composer.label')}
          </label>
          <textarea
            {...messageField}
            ref={(element) => {
              registerRef(element);
              textareaRef.current = element;
            }}
            id="chat-message"
            rows={1}
            onKeyDown={onKeyDown}
            placeholder={t('composer.placeholder')}
            aria-describedby={describedBy}
            aria-invalid={errorKey ? true : undefined}
            className="max-h-[200px] min-h-[2.75rem] flex-1 resize-none bg-transparent px-2 py-2.5 text-[0.95rem] text-navy-800 placeholder:text-muted/70 focus:outline-none"
          />

          {isSending ? (
            <button
              type="button"
              onClick={onCancel}
              aria-label={t('composer.cancel')}
              className="tap-target inline-flex shrink-0 items-center justify-center gap-2 rounded-xl border border-line bg-white px-3 text-sm font-semibold text-navy-800 hover:bg-sand-100"
            >
              <Square aria-hidden="true" className="size-4" />
              <span aria-hidden="true" className="hidden sm:inline">
                {t('composer.cancel')}
              </span>
            </button>
          ) : (
            <button
              type="submit"
              disabled={isEmpty}
              className="tap-target inline-flex shrink-0 items-center justify-center rounded-xl bg-teal-600 px-4 text-white transition-colors hover:bg-teal-700 disabled:cursor-not-allowed disabled:bg-line-strong disabled:text-white"
            >
              <Send aria-hidden="true" className="size-4 rtl:-scale-x-100" />
              <span className="sr-only">{t('composer.send')}</span>
            </button>
          )}
        </div>

        <div className="mt-1.5 flex flex-wrap items-center justify-between gap-2 px-1">
          <p id={hintId} className="text-xs text-muted">
            {t('composer.hint')}
          </p>
          {showCounter ? (
            <p
              id={counterId}
              aria-live="polite"
              className={`text-xs font-medium ${remaining < 0 ? 'text-alert-600' : 'text-muted'}`}
            >
              {remaining >= 0
                ? t('composer.charactersRemaining', {
                    remaining,
                    max: MAX_MESSAGE_LENGTH,
                  })
                : t('composer.tooLong', { max: MAX_MESSAGE_LENGTH })}
            </p>
          ) : null}
        </div>

        {errorKey ? (
          <p id={errorId} role="alert" className="mt-1 px-1 text-xs font-medium text-alert-600">
            {t(errorKey, { max: MAX_MESSAGE_LENGTH })}
          </p>
        ) : null}
      </div>
    </form>
  );
}
