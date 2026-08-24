/**
 * WCAG 2.2 AA contrast is asserted against the real design tokens: the test
 * parses src/styles/index.css, so changing a colour that breaks a documented
 * pairing fails the suite instead of silently shipping.
 */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';

// import.meta.url is an http URL under the jsdom environment, so resolve from cwd.
const css = readFileSync(resolve(process.cwd(), 'src/styles/index.css'), 'utf8');

function token(name: string): string {
  const match = new RegExp(`--color-${name}:\\s*(#[0-9a-fA-F]{3,8});`).exec(css);
  if (!match?.[1]) throw new Error(`Design token --color-${name} is missing from index.css`);
  return match[1];
}

function channel(value: number): number {
  const srgb = value / 255;
  return srgb <= 0.03928 ? srgb / 12.92 : ((srgb + 0.055) / 1.055) ** 2.4;
}

function luminance(hex: string): number {
  const clean = hex.replace('#', '');
  const full =
    clean.length === 3
      ? clean
          .split('')
          .map((c) => c + c)
          .join('')
      : clean;
  const r = parseInt(full.slice(0, 2), 16);
  const g = parseInt(full.slice(2, 4), 16);
  const b = parseInt(full.slice(4, 6), 16);
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
}

function ratio(foreground: string, background: string): number {
  const a = luminance(foreground);
  const b = luminance(background);
  const [light, dark] = a > b ? [a, b] : [b, a];
  return ((light as number) + 0.05) / ((dark as number) + 0.05);
}

const WHITE = '#ffffff';

describe('WCAG 2.2 AA contrast of the palette', () => {
  const bodyText: [string, string, string][] = [
    ['body text on the app background', token('navy-800'), token('sand-50')],
    ['muted text on the app background', token('muted'), token('sand-50')],
    ['muted text on cards', token('muted'), WHITE],
    ['body text on cards', token('navy-800'), WHITE],
    ['primary button label', WHITE, token('teal-600')],
    ['user message text', WHITE, token('navy-800')],
    ['links on cards', token('teal-700'), WHITE],
    ['emergency number on cards', token('alert-600'), WHITE],
    ['emergency text in the alert panel', token('alert-700'), token('alert-50')],
    ['degraded-service banner text', token('warn-700'), token('warn-50')],
    ['disclaimer text on the coral panel', token('navy-800'), token('coral-50')],
    ['coral accent text', token('coral-600'), token('coral-50')],
  ];

  it.each(bodyText)('%s reaches 4.5:1', (_label, fg, bg) => {
    expect(ratio(fg, bg)).toBeGreaterThanOrEqual(4.5);
  });

  const nonText: [string, string, string][] = [
    ['focus ring against the app background', token('teal-600'), token('sand-50')],
    ['focus ring against cards', token('teal-600'), WHITE],
    ['emergency panel border', token('alert-200'), token('alert-50')],
    ['emergency contact border on cards', token('alert-200'), WHITE],
  ];

  it.each(nonText)('%s reaches 3:1 for non-text contrast', (_label, fg, bg) => {
    expect(ratio(fg, bg)).toBeGreaterThanOrEqual(3);
  });
});
