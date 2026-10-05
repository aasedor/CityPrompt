import type { ZoningLabel } from './zoningLabels';

/** CityPrompt presentation colours, never a replacement for the published designation.
 * DC has one neutral family colour: its underlying use cannot be inferred from DC.
 */
export function zoningColor(district: Pick<ZoningLabel, 'code' | 'label'>): string {
  const code = (district.code || district.label.split(/\s/)[0]).toUpperCase();
  if (/^DC/.test(code)) return '#aa8bbb';
  if (code === 'S-SPR') return '#9dc35f';
  if (code === 'S-UN') return '#64a57b';
  if (/^MU-/.test(code)) return '#e47760';
  if (/^M-/.test(code)) return '#e6ae56';
  if (/^R-|^H-GO$/.test(code)) return '#f1d36f';
  if (/^C-/.test(code)) return '#88b4cd';
  if (/^I-/.test(code)) return '#a69ebd';
  return '#aab9b6';
}

export interface ZoningPreferences {
  enabled: boolean;
  labels: boolean;
  lines: boolean;
  fill: boolean;
  fillOpacity: number;
}

export const DEFAULT_ZONING_PREFERENCES: ZoningPreferences = {
  enabled: false, labels: true, lines: true, fill: true, fillOpacity: 0.4,
};

export function readZoningPreferences(saved: string | null): ZoningPreferences {
  try {
    const value = JSON.parse(saved ?? '{}');
    if (!value || typeof value !== 'object') return { ...DEFAULT_ZONING_PREFERENCES };
    const legacy = typeof value.enabled !== 'boolean';
    const legacyActive = value.labels === true || value.districtLines === true;
    if (legacy && !legacyActive) return { ...DEFAULT_ZONING_PREFERENCES };
    return {
      enabled: typeof value.enabled === 'boolean' ? value.enabled : legacyActive,
      labels: typeof value.labels === 'boolean' ? value.labels : true,
      // The retired cadastral "lines" key must never become district outlines.
      lines: typeof value.districtLines === 'boolean' ? value.districtLines : !legacy,
      fill: typeof value.fill === 'boolean' ? value.fill : !legacy,
      fillOpacity: typeof value.fillOpacity === 'number' && Number.isFinite(value.fillOpacity)
        ? Math.min(1, Math.max(0, value.fillOpacity)) : DEFAULT_ZONING_PREFERENCES.fillOpacity,
    };
  } catch { return { ...DEFAULT_ZONING_PREFERENCES }; }
}
