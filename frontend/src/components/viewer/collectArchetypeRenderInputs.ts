/**
 * collectArchetypeRenderInputs — Extracts archetype prompt data from site zones
 * for use in the AI render pipeline.
 *
 * Iterates zone properties using the same domain-prefix pattern as
 * masterPlan2DReferences.ts to pull positive/negative prompts and
 * reference image URLs from archetype selections.
 */
import type { SiteZone } from '@/types';

// ---------------------------------------------------------------------------
// Domain prefix config (mirrors masterPlan2DReferences.ts)
// ---------------------------------------------------------------------------

const DOMAIN_PREFIXES = ['development', 'road', 'green_space', 'plaza'] as const;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ArchetypeRenderInputs {
  /** Positive prompt fragments extracted from archetype imagePrompt.positive */
  positivePrompts: string[];
  /** Negative prompt fragments extracted from archetype imagePrompt.negative */
  negativePrompts: string[];
  /** Reference image URLs from archetype selections */
  referenceImageUrls: string[];
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
  const positiveSet = new Set<string>();
  const negativeSet = new Set<string>();
  const imageUrlSet = new Set<string>();

  for (const zone of siteZones) {
    const props = zone.properties;
    if (!props) continue;

    for (const prefix of DOMAIN_PREFIXES) {
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
