import { Dialog } from './Dialog';

interface Props {
  open: boolean;
  title: string;
  body: string;
  confirmLabel: string;
  cancelLabel: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({
  open,
  title,
  body,
  confirmLabel,
  cancelLabel,
  onConfirm,
  onCancel,
}: Props) {
  return (
    <Dialog
      open={open}
      onClose={onCancel}
      title={title}
      footer={
        <>
          <button
            type="button"
            onClick={onCancel}
            className="tap-target rounded-xl border border-line px-4 py-2 text-sm font-semibold text-navy-800 hover:bg-sand-100"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="tap-target rounded-xl bg-navy-800 px-4 py-2 text-sm font-semibold text-white hover:bg-navy-900"
          >
            {confirmLabel}
          </button>
        </>
      }
    >
      <p className="text-muted">{body}</p>
    </Dialog>
  );
}
