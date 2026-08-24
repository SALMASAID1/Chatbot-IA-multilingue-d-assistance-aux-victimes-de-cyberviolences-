import { Component, type ErrorInfo, type ReactNode } from 'react';
import { withTranslation, type WithTranslation } from 'react-i18next';
import { AlertTriangle, Phone } from 'lucide-react';
import { logError } from '@/lib/logger';
import { telHref } from '@/lib/security/url';

interface Props extends WithTranslation {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

class ErrorBoundaryInner extends Component<Props, State> {
  override state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  override componentDidCatch(error: Error, info: ErrorInfo): void {
    // Only the component stack — never props, which may hold message text.
    logError('Render error', { message: error.message, stack: info.componentStack?.slice(0, 300) });
  }

  override render(): ReactNode {
    const { t, children } = this.props;
    if (!this.state.hasError) return children;

    return (
      <div role="alert" className="mx-auto max-w-md p-6 text-center">
        <AlertTriangle aria-hidden="true" className="mx-auto mb-3 size-8 text-alert-600" />
        <h1 className="mb-2 text-lg font-bold text-navy-800">{t('errors.boundaryTitle')}</h1>
        <p className="mb-4 text-sm text-muted">{t('errors.boundaryBody')}</p>
        <div className="flex flex-wrap justify-center gap-2">
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="tap-target rounded-xl bg-teal-600 px-4 py-2 font-semibold text-white hover:bg-teal-700"
          >
            {t('errors.reload')}
          </button>
          <a
            href={telHref('19')}
            className="tap-target inline-flex items-center gap-2 rounded-xl border border-alert-200 bg-alert-50 px-4 py-2 font-semibold text-alert-700"
          >
            <Phone aria-hidden="true" className="size-4" />
            <span className="force-ltr">19</span>
          </a>
        </div>
      </div>
    );
  }
}

export const ErrorBoundary = withTranslation()(ErrorBoundaryInner);
