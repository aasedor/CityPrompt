import catalogue from '@/data/buildingArchetypes.json';
import type { SiteZone } from '@/types';

interface LandscapeSource {
  id: string;
  description?: string;
  aestheticCategory?: string;
  palette?: { landscape?: string };
  styleProfile?: { frontageType?: string; streetRelationship?: string; publicRealm?: string };
  facadeDetail?: { groundFloor?: string };
  variants?: LandscapeSource[];
}
const entries = new Map((catalogue.archetypes as LandscapeSource[]).map(entry => [entry.id, entry]));

/** Read ground-level notes only: roof gardens must never become frontage planting.
 * These are design cues, not measured permission to occupy a route or model. */
export function buildingLandscapeNotes(zone: Pick<SiteZone, 'properties'>) {
  const p = zone.properties ?? {};
  const entry = entries.get(String(p.building_archetype_id ?? ''));
  const variant = entry?.variants?.find(v => v.id === p.development_selected_variant_id);
  const notes = [variant?.facadeDetail?.groundFloor, entry?.styleProfile?.frontageType,
    entry?.styleProfile?.streetRelationship, entry?.styleProfile?.publicRealm,
    entry?.facadeDetail?.groundFloor].filter((note): note is string => Boolean(note));
  for (const description of [variant?.description, entry?.description]) {
    for (const sentence of description?.split(/(?<=[.!?])\s+/) ?? []) {
      if (/garden|front yard|planting|planted|landscap|forecourt|hedge|boulevard/i.test(sentence)
        && !/roof|upper|balcon/i.test(sentence)) notes.push(sentence);
    }
  }
  const text = notes.join(' ').toLowerCase();
  const planting = /native|grass|fern|meadow|biophilic/.test(text) ? 'grasses'
    : entry?.aestheticCategory === 'minimalist' || /formal|hedge|clipped/.test(text) ? 'evergreen'
      : /flower|cottage|planted front|planted bed|heritage/.test(text) ? 'flowering' : 'mixed';
  const color = variant?.palette?.landscape ?? entry?.palette?.landscape;
  return { archetypeId: entry?.id ?? null, variantId: variant?.id ?? null, notes, planting,
    source: notes.length ? 'archetype_ground_notes' as const : 'conservative_fallback' as const,
    foliage: /^#[\da-f]{6}$/i.test(color ?? '') ? color! : '#527344',
    bed: /gravel|aggregate/.test(text) ? '#a59b82' : '#665342' };
}
