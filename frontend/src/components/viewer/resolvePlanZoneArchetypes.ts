/**
 * Deterministic archetype resolution for AI-planner plan zones.
 *
 * Plan zones drawn by the backend geometry engine carry semantic hints
 * (`_plan_role`, `development_type`, `development_aesthetic`, `floors`,
 * `width`, `tree_density`) but no archetype IDs — so the render pipeline
 * attaches zero reference images to them. This module maps those hints onto
 * real catalog entries and injects the standard `{prefix}_archetype_id` /
 * `{prefix}_selected_variant_id` properties that every render consumer
 * (collectArchetypeImages, getMapOverlayPrompt, collectArchetypeRenderInputs)
 * already keys off. Same inputs always resolve to the same archetype.
 *
 * Users can still override: an explicit archetype ID on the zone wins, and
 * these are plain zone properties editable in ZonePropertiesPanel.
 */

import buildingCatalog from '@/data/buildingArchetypes.json';
import openSpaceCatalog from '@/data/openSpaceArchetypes.json';
import streetPathCatalog from '@/data/streetPathArchetypes.json';
import type { SiteZone } from '@/types';

interface CatalogEntry {
  id: string;
  developmentType?: string;
  aestheticCategory?: string;
  minFloors?: number;
  maxFloors?: number;
  thumbnailUrl?: string;
  variants?: Array<{ id: string; thumbnailUrl?: string }>;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const BUILDINGS = ((buildingCatalog as any).archetypes ?? buildingCatalog) as CatalogEntry[];
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const OPEN_SPACES = ((openSpaceCatalog as any).archetypes ?? openSpaceCatalog) as CatalogEntry[];
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const STREETS = ((streetPathCatalog as any).archetypes ?? streetPathCatalog) as CatalogEntry[];

const ARCHETYPE_ID_KEYS = [
  'development_archetype_id',
  'road_archetype_id',
  'green_space_archetype_id',
  'plaza_archetype_id',
] as const;

const norm = (value: unknown): string =>
  String(value ?? '').toLowerCase().trim().replace(/[\s-]+/g, '_');

const usable = (entry: CatalogEntry): boolean =>
  Boolean(entry.thumbnailUrl || entry.variants?.some((v) => v.thumbnailUrl));

/** Deterministic pick: prefer entries with variants, then lexicographic id. */
function stablePick(candidates: CatalogEntry[]): CatalogEntry | undefined {
  return [...candidates].sort((a, b) => {
    const av = a.variants?.length ? 0 : 1;
    const bv = b.variants?.length ? 0 : 1;
    return av !== bv ? av - bv : a.id.localeCompare(b.id);
  })[0];
}

// Family aliases: generic brief terms -> concrete catalog aestheticCategory
// keywords. The direct includes-match runs first; families are the second tier
// so "european" still narrows the pool even though no catalog entry is
// literally categorized "european". Keywords match with the same
// bidirectional includes as the direct tier, and the pool is never emptied.
const AESTHETIC_FAMILIES: Record<string, string[]> = {
  european: ['parisian', 'haussmann', 'amsterdam', 'mediterranean', 'neoclassical', 'classical'],
  heritage: ['historical', 'brownstone', 'industrial_brick', 'traditional_vernacular', 'neoclassical', 'romanesque'],
  historic: ['historical', 'brownstone', 'traditional_vernacular', 'neoclassical', 'romanesque'],
  modern: ['contemporary_urban', 'contemporary_midrise', 'modernist', 'minimalist', 'glass_tower_modern'],
  contemporary: ['contemporary_urban', 'contemporary_midrise', 'japanese_contemporary', 'modernist'],
  nordic: ['scandinavian_nordic'],
  scandinavian: ['scandinavian_nordic'],
  green: ['eco_urban_green_architecture', 'biophilic'],
  sustainable: ['eco_urban_green_architecture', 'biophilic'],
  industrial: ['industrial_brick', 'daylight_factory', 'machine_aesthetic'],
};

function resolveBuilding(props: Record<string, unknown>): CatalogEntry | undefined {
  const devType = norm(props.development_type) || 'mixed_use';
  const aesthetic = norm(props.development_aesthetic);
  const floors = Number(props.floors) || 4;

  // developmentType match: exact first, then family prefix either way
  // ("residential" hint matches residential_multifamily; "mixed_use" exact).
  let pool = BUILDINGS.filter((e) => usable(e) && norm(e.developmentType) === devType);
  if (!pool.length) {
    pool = BUILDINGS.filter((e) => {
      const et = norm(e.developmentType);
      return usable(e) && (et.startsWith(`${devType}_`) || devType.startsWith(`${et}_`));
    });
  }
  if (!pool.length) pool = BUILDINGS.filter((e) => usable(e) && norm(e.developmentType) === 'mixed_use');
  if (!pool.length) return undefined;

  // Floor fit: hard filter when possible, else nearest floor range.
  const inRange = pool.filter(
    (e) => (e.minFloors ?? 1) <= floors && floors <= (e.maxFloors ?? 999),
  );
  if (inRange.length) {
    pool = inRange;
  } else {
    const distance = (e: CatalogEntry) =>
      Math.min(Math.abs((e.minFloors ?? 1) - floors), Math.abs((e.maxFloors ?? 999) - floors));
    const best = Math.min(...pool.map(distance));
    pool = pool.filter((e) => distance(e) === best);
  }

  // Aesthetic affinity narrows but never empties the pool: direct
  // includes-match first, family alias tier second.
  if (aesthetic) {
    const direct = pool.filter((e) => {
      const cat = norm(e.aestheticCategory);
      return cat && (cat.includes(aesthetic) || aesthetic.includes(cat));
    });
    if (direct.length) {
      pool = direct;
    } else {
      const familyTerms = Object.entries(AESTHETIC_FAMILIES)
        .filter(([family]) => aesthetic.includes(family) || family.includes(aesthetic))
        .flatMap(([, terms]) => terms);
      if (familyTerms.length) {
        const familial = pool.filter((e) => {
          const cat = norm(e.aestheticCategory);
          return cat && familyTerms.some((term) => cat.includes(term) || term.includes(cat));
        });
        if (familial.length) pool = familial;
      }
    }
  }
  return stablePick(pool);
}

/** Planar shoelace area in m² — good enough for a pocket-park threshold. */
function approxAreaM2(coordinates: number[][] | undefined): number {
  if (!coordinates || coordinates.length < 3) return Infinity;
  const lat = coordinates[0][1];
  const mPerLon = 111_320 * Math.cos((lat * Math.PI) / 180);
  const mPerLat = 111_320;
  let sum = 0;
  for (let i = 0; i < coordinates.length; i++) {
    const [x1, y1] = coordinates[i];
    const [x2, y2] = coordinates[(i + 1) % coordinates.length];
    sum += x1 * mPerLon * (y2 * mPerLat) - x2 * mPerLon * (y1 * mPerLat);
  }
  return Math.abs(sum) / 2;
}

const POCKET_PARK_MAX_M2 = 1500;

function resolveOpenSpace(zone: SiteZone): CatalogEntry | undefined {
  const area = approxAreaM2(zone.coordinates);
  const wanted = area < POCKET_PARK_MAX_M2 ? 'urban_pocket_park' : 'neighborhood_park';
  return (
    OPEN_SPACES.find((e) => e.id === wanted && usable(e)) ||
    OPEN_SPACES.find((e) => e.id === 'neighborhood_park' && usable(e))
  );
}

/** Street archetype by right-of-way width band. */
function resolveStreet(props: Record<string, unknown>): CatalogEntry | undefined {
  const width = Number(props.width) || 14;
  const wanted =
    width < 10 ? 'yield_street'
    : width < 15 ? 'narrow_residential_street'
    : width < 22 ? 'collector_road'
    : 'main_street_complete';
  return (
    STREETS.find((e) => e.id === wanted && usable(e)) ||
    STREETS.find((e) => e.id === 'narrow_residential_street' && usable(e))
  );
}

function inject(
  zone: SiteZone,
  prefix: 'development' | 'road' | 'green_space',
  entry: CatalogEntry,
): SiteZone {
  const firstVariant = entry.variants?.find((v) => v.thumbnailUrl) ?? entry.variants?.[0];
  return {
    ...zone,
    properties: {
      ...zone.properties,
      [`${prefix}_archetype_id`]: entry.id,
      ...(firstVariant ? { [`${prefix}_selected_variant_id`]: firstVariant.id } : {}),
      _plan_archetype_resolved: true,
    },
  };
}

/**
 * Full render normalization: resolve plan-zone archetypes AND drop height-
 * framework overlays. Framework zones are LAP-style reference bands covering
 * whole blocks — in a render they'd dominate the prompt and mask as the
 * biggest "zone" while carrying no buildable content.
 */
export function prepareZonesForRender(zones: SiteZone[]): SiteZone[] {
  return withPlanArchetypeDefaults(zones).filter(
    (zone) => (zone.properties as Record<string, unknown> | undefined)?._plan_role !== 'framework_height',
  );
}

/**
 * Normalize a zone list so plan zones carry archetype references.
 * Non-plan zones, framework layers, custom-style zones and zones with an
 * explicit archetype ID pass through untouched.
 */
export function withPlanArchetypeDefaults(zones: SiteZone[]): SiteZone[] {
  return zones.map((zone) => {
    const props = (zone.properties ?? {}) as Record<string, unknown>;
    const role = props._plan_role as string | undefined;
    if (!role || role === 'framework_height') return zone;
    if (ARCHETYPE_ID_KEYS.some((k) => props[k])) return zone; // user override wins
    if (props.custom_style_enabled) return zone; // custom style replaces archetypes

    if (role === 'building') {
      const entry = resolveBuilding(props);
      return entry ? inject(zone, 'development', entry) : zone;
    }
    if (role === 'open_space') {
      const entry = resolveOpenSpace(zone);
      return entry ? inject(zone, 'green_space', entry) : zone;
    }
    if (role === 'street') {
      const entry = resolveStreet(props);
      return entry ? inject(zone, 'road', entry) : zone;
    }
    return zone;
  });
}
