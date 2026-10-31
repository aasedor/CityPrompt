import type { ZoningLabel } from './zoningLabels';
import { calgaryDistrictColour } from './calgaryBylaw';

/** Published Calgary Land Use Class colours, shared with the bylaw editor.
 * DC keeps its own class colour; its underlying use cannot be inferred from DC.
 */
export function zoningColor(district: Pick<ZoningLabel, 'code' | 'label'>): string {
  return calgaryDistrictColour(district.code?.trim() || district.label);
}

export interface ZoningPreferences {
  enabled: boolean;
  clipToSite: boolean;
  labels: boolean;
  lines: boolean;
  fill: boolean;
  fillOpacity: number;
}

export const DEFAULT_ZONING_PREFERENCES: ZoningPreferences = {
  enabled: false, clipToSite: false, labels: true, lines: true, fill: true, fillOpacity: 0.4,
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
      clipToSite: value.clipToSite === true,
      labels: typeof value.labels === 'boolean' ? value.labels : true,
      // The retired cadastral "lines" key must never become district outlines.
      lines: typeof value.districtLines === 'boolean' ? value.districtLines : !legacy,
      fill: typeof value.fill === 'boolean' ? value.fill : !legacy,
      fillOpacity: typeof value.fillOpacity === 'number' && Number.isFinite(value.fillOpacity)
        ? Math.min(1, Math.max(0, value.fillOpacity)) : DEFAULT_ZONING_PREFERENCES.fillOpacity,
    };
  } catch { return { ...DEFAULT_ZONING_PREFERENCES }; }
}
