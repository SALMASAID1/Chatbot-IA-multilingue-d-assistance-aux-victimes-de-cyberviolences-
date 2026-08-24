/**
 * Supporting visual for the welcome state.
 *
 * No image was downloaded: `scripts/fetch_google_images.py` requires a search
 * API key (SERPAPI_KEY or Google CSE) and none is configured in this
 * environment, so per the acceptance rules this is an inline, dependency-free
 * illustration rather than a fabricated asset.
 *
 * Deliberately abstract: no faces, no minors, no padlocks over mouths, no
 * "hacker in a hoodie" imagery — nothing that could deepen distress. The
 * composition is laid out for a wide banner (6:1) and centred on the shield, so
 * cropping at other aspect ratios only trims empty space. Once the conversation
 * starts the welcome panel unmounts and the space goes to messages.
 */
import { useTranslation } from 'react-i18next';

export function WelcomeIllustration({ className = '' }: { className?: string }) {
  const { t } = useTranslation();

  return (
    <svg
      viewBox="0 0 1200 200"
      role="img"
      aria-label={t('welcome.imageAlt')}
      className={className}
      preserveAspectRatio="xMidYMid slice"
    >
      <defs>
        <linearGradient id="emc-sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#eef6f5" />
          <stop offset="100%" stopColor="#f3ede4" />
        </linearGradient>
        <linearGradient id="emc-shield" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#0c625c" />
          <stop offset="100%" stopColor="#163149" />
        </linearGradient>
      </defs>

      <rect width="1200" height="200" fill="url(#emc-sky)" />

      {/* Soft horizon: an open, unthreatening space. */}
      <circle cx="210" cy="230" r="150" fill="#d3e8e6" opacity="0.5" />
      <circle cx="980" cy="250" r="175" fill="#a8d2ce" opacity="0.32" />
      <circle cx="600" cy="285" r="200" fill="#d3e8e6" opacity="0.4" />

      {/* Sheltering arc across the full width. */}
      <path
        d="M120 190C120 95 335 25 600 25s480 70 480 165"
        fill="none"
        stroke="#a8d2ce"
        strokeWidth="3"
        strokeLinecap="round"
        opacity="0.75"
      />

      {/* Shield: protection, centred and quiet. */}
      <path
        d="M600 48l46 17.5v35c0 28.5-19 50-46 57.5-27-7.5-46-29-46-57.5v-35L600 48z"
        fill="url(#emc-shield)"
      />
      <path
        d="m582 110 12.5 12.5L621 96"
        fill="none"
        stroke="#f3ede4"
        strokeWidth="6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      {/* Two conversation marks: someone is on the other side. */}
      <g opacity="0.95">
        <rect x="330" y="82" width="120" height="52" rx="20" fill="#fff" />
        <rect x="352" y="100" width="62" height="7" rx="3.5" fill="#a8d2ce" />
        <rect x="352" y="114" width="38" height="7" rx="3.5" fill="#d3e8e6" />
      </g>
      <g opacity="0.95">
        <rect x="752" y="96" width="120" height="52" rx="20" fill="#fff" />
        <rect x="774" y="114" width="68" height="7" rx="3.5" fill="#f6c9b8" />
        <rect x="774" y="128" width="42" height="7" rx="3.5" fill="#e9e1d5" />
      </g>
    </svg>
  );
}
