/**
 * collectArchetypeRenderInputs — Extracts archetype prompt data from site zones
 * for use in the AI render pipeline.
 *
 * Iterates zone properties using the same domain-prefix pattern as
 * masterPlan2DReferences.ts to pull positive/negative prompts and
 * reference image URLs from archetype selections.
 *
 * Also loads enriched metadata (facadeDetail, roofDetail, renderPrompt)
 * from the archetype catalog for map-overlay rendering.
 */
import type { SiteZone } from '@/types';
import archetypeCatalog from '@/data/buildingArchetypes.json';
import { withPlanArchetypeDefaults } from './resolvePlanZoneArchetypes';

// ---------------------------------------------------------------------------
// Domain prefix config (mirrors masterPlan2DReferences.ts)
// ---------------------------------------------------------------------------

const DOMAIN_PREFIXES = ['development', 'road', 'green_space', 'plaza'] as const;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Enriched facade/roof/render metadata from the archetype catalog */
export interface ArchetypeFacadeDetail {
  primaryMaterial?: string;
  secondaryMaterial?: string;
  accentMaterial?: string;
  groundFloor?: string;
  upperFloors?: string;
  cornice?: string;
  colorScheme?: string;
}

export interface ArchetypeRoofDetail {
  form?: string;
  material?: string;
  features?: string;
  aerialAppearance?: string;
}

export interface ArchetypeRenderPrompt {
  mapOverlay?: string;
  roofView?: string;
  negative?: string;
}

export interface ArchetypeRenderInputs {
  /** Positive prompt fragments extracted from archetype imagePrompt.positive */
  positivePrompts: string[];
  /** Negative prompt fragments extracted from archetype imagePrompt.negative */
  negativePrompts: string[];
  /** Reference image URLs from archetype selections */
  referenceImageUrls: string[];
  /** Enriched facade detail from the archetype catalog (first match) */
  facadeDetail?: ArchetypeFacadeDetail;
  /** Enriched roof detail from the archetype catalog (first match) */
  roofDetail?: ArchetypeRoofDetail;
  /** Map-overlay-specific render prompt from the archetype catalog (first match) */
  renderPrompt?: ArchetypeRenderPrompt;
  /** The archetype ID that was matched */
  matchedArchetypeId?: string;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function asObject(value: unknown): Record<string, unknown> | undefined {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : undefined;
}

function asString(value: unknown): string | undefined {
  if (typeof value !== 'string') return undefined;
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : undefined;
}

// ---------------------------------------------------------------------------
// Main function
// ---------------------------------------------------------------------------

/**
 * Scan all site zones for archetype prompt data stored in domain-prefixed
 * properties (e.g. `development_generation_style_input`, `road_archetype_image`).
 *
 * Returns deduplicated arrays of positive prompts, negative prompts, and
 * reference image URLs ready to merge into AIRenderOptions.
 */
export function collectArchetypeRenderInputs(siteZones: SiteZone[]): ArchetypeRenderInputs {
  // AI-planner plan zones resolve their archetypes from semantic hints.
  siteZones = withPlanArchetypeDefaults(siteZones);
  const positiveSet = new Set<string>();
  const negativeSet = new Set<string>();
  const imageUrlSet = new Set<string>();
  let facadeDetail: ArchetypeFacadeDetail | undefined;
  let roofDetail: ArchetypeRoofDetail | undefined;
  let renderPrompt: ArchetypeRenderPrompt | undefined;
  let matchedArchetypeId: string | undefined;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const catalog = (archetypeCatalog as any)?.archetypes as any[] | undefined;

  for (const zone of siteZones) {
    const props = zone.properties;
    if (!props) continue;

    for (const prefix of DOMAIN_PREFIXES) {
      // --- Look up enriched metadata from the archetype catalog ---
      const archetypeIdKey = `${prefix}_archetype_id`;
      const archetypeId = asString(props[archetypeIdKey]);
      if (archetypeId && !matchedArchetypeId && catalog) {
        // Match either exact ID or ID with variant suffix (e.g. "industrial_brick_mixed_use_front_day")
        const catalogEntry = catalog.find((a: any) =>
          a.id === archetypeId || archetypeId.startsWith(a.id + '_'),
        );
        if (catalogEntry) {
          matchedArchetypeId = catalogEntry.id;
          if (catalogEntry.facadeDetail) facadeDetail = catalogEntry.facadeDetail;
          if (catalogEntry.roofDetail) roofDetail = catalogEntry.roofDetail;
          if (catalogEntry.renderPrompt) renderPrompt = catalogEntry.renderPrompt;
        }
      }

      // --- Generation style input (contains imagePrompt with positive/negative) ---
      const styleInput = asObject(props[`${prefix}_generation_style_input`]);
      if (styleInput) {
        const imagePrompt = asObject(styleInput.imagePrompt);
        if (imagePrompt) {
          const positive = asString(imagePrompt.positive);
          if (positive) positiveSet.add(positive);

          const negative = asString(imagePrompt.negative);
          if (negative) negativeSet.add(negative);
        }

        // Also check for archetypeImageUrl at the style input level
        const archetypeUrl = asString(styleInput.archetypeImageUrl);
        if (archetypeUrl) imageUrlSet.add(archetypeUrl);
      }

      // --- Archetype image object (has .url or .imageUrl) ---
      const archetypeImage = props[`${prefix}_archetype_image`];
      if (archetypeImage) {
        const imageObj = asObject(archetypeImage);
        if (imageObj) {
          const url = asString(imageObj.url) || asString(imageObj.imageUrl);
          if (url) imageUrlSet.add(url);
        } else {
          // Could be a direct string URL
          const directUrl = asString(archetypeImage);
          if (directUrl) imageUrlSet.add(directUrl);
        }
      }

      // --- Archetype image URL as direct property ---
      const directImageUrl = asString(props[`${prefix}_archetype_image_url`]);
      if (directImageUrl) imageUrlSet.add(directImageUrl);
    }
  }

  return {
    positivePrompts: [...positiveSet],
    negativePrompts: [...negativeSet],
    referenceImageUrls: [...imageUrlSet],
    facadeDetail,
    roofDetail,
    renderPrompt,
    matchedArchetypeId,
  };
}

/**
 * Convenience: merge archetype prompts into a single comma-separated string.
 * Useful for appending to the AI render style prompt.
 */
export function mergeArchetypePrompts(inputs: ArchetypeRenderInputs): {
  archetypePrompt: string;
  archetypeNegative: string;
} {
  return {
    archetypePrompt: inputs.positivePrompts.join(', '),
    archetypeNegative: inputs.negativePrompts.join(', '),
  };
}
