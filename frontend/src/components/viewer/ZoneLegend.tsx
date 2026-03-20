/**
 * ZoneLegend — Collapsible floating legend showing APA standard land-use colors
 * for the zone types present on the current map.
 *
 * When zones have a `development_type` property, shows the granular APA color.
 * Otherwise falls back to the coarse ZONE_TYPE_CONFIG color.
 */

import { useState, useMemo } from 'react';
import { ZONE_TYPE_CONFIG, type SiteZone } from '@/types';
import { getColourForDevelopmentType } from '@/data/landUseColours';

interface ZoneLegendProps {
  siteZones: SiteZone[];
}

interface LegendEntry {
  key: string;
  color: string;
  label: string;
  outline?: boolean; // true for site_boundary (outline only)
}

export function ZoneLegend({ siteZones }: ZoneLegendProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const entries = useMemo(() => {
    const seen = new Set<string>();
    const result: LegendEntry[] = [];

    for (const zone of siteZones) {
      // Try archetype label first (unique shade per archetype)
      const archetypeLabel = (zone.properties?.development_archetype_label as string)
        || (zone.properties?.road_archetype_label as string)
        || (zone.properties?.green_space_archetype_label as string)
        || (zone.properties?.plaza_archetype_label as string);
      if (archetypeLabel && !seen.has(zone.id)) {
        seen.add(zone.id);
        result.push({
          key: zone.id,
          color: zone.color,
          label: archetypeLabel,
          outline: zone.zone_type === 'site_boundary',
        });
        continue;
      }

      // Try granular development_type
      const devType = zone.properties?.development_type as string | undefined;
      if (devType) {
        const apaColor = getColourForDevelopmentType(devType);
        if (apaColor.label !== 'Unclassified' && !seen.has(devType)) {
          seen.add(devType);
          result.push({
            key: devType,
            color: apaColor.fill,
            label: apaColor.label,
            outline: zone.zone_type === 'site_boundary',
          });
          continue;
        }
      }

      // Fallback to zone_type
      const zt = zone.zone_type;
      if (zt === 'site_boundary') {
        if (!seen.has(zt)) {
          seen.add(zt);
          result.push({ key: zt, color: '#FF6B35', label: 'Site Boundary', outline: true });
        }
        continue;
      }

      if (!seen.has(zt)) {
        seen.add(zt);
        const config = ZONE_TYPE_CONFIG[zt];
        if (config) {
          result.push({ key: zt, color: config.color, label: config.label });
        }
      }
    }

    return result;
  }, [siteZones]);

  if (entries.length === 0) return null;

  return (
    <div className="absolute bottom-3 left-3 z-10">
      {/* Collapsed: small button */}
      {!isExpanded ? (
        <button
          onClick={() => setIsExpanded(true)}
          className="flex items-center gap-1.5 rounded-lg bg-gray-900/90 backdrop-blur-sm px-3 py-2 text-[11px] font-medium text-gray-300 shadow-lg border border-gray-700/50 hover:bg-gray-800/90 transition"
        >
          <span className="flex gap-0.5">
            {entries.slice(0, 4).map((e) => (
              <span
                key={e.key}
                className="h-2.5 w-2.5 rounded-sm"
                style={e.outline
                  ? { border: `2px solid ${e.color}`, backgroundColor: 'transparent' }
                  : { backgroundColor: e.color }
                }
              />
            ))}
          </span>
          Legend
          <svg className="h-3 w-3 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
          </svg>
        </button>
      ) : (
        /* Expanded: full legend */
        <div className="rounded-lg bg-gray-900/90 backdrop-blur-sm shadow-lg border border-gray-700/50">
          <button
            onClick={() => setIsExpanded(false)}
            className="flex w-full items-center justify-between px-3 py-2 border-b border-white/5"
          >
            <span className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Land Use Legend</span>
            <svg className="h-3 w-3 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 12h-15" />
            </svg>
          </button>
          <div className="px-3 py-2 space-y-1 max-h-48 overflow-y-auto">
            {entries.map((entry) => (
              <div key={entry.key} className="flex items-center gap-2">
                <span
                  className="h-3 w-3 rounded-sm flex-shrink-0"
                  style={entry.outline
                    ? { border: `2px solid ${entry.color}`, backgroundColor: 'transparent' }
                    : { backgroundColor: entry.color, border: '1px solid rgba(255,255,255,0.15)' }
                  }
                />
                <span className="text-[10px] font-medium text-gray-300 truncate">
                  {entry.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
