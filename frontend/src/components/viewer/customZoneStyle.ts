/**
 * Custom-style zone support: the user defines the zone with a free-text prompt
 * (optionally LLM-expanded) and uploaded reference photos instead of a catalog
 * archetype. Shared between the aerial (useAIRender) and globe
 * (useGlobeAIRender) render pipelines.
 */
import type { SiteZone } from '@/types';

export interface CustomZoneStyle {
  /** Expanded prompt if present, otherwise the raw user prompt. */
  promptText: string;
  /** Up to 3 uploaded photo URLs to use as render reference images. */
  photoUrls: string[];
}

/**
 * Returns null unless the zone has custom style enabled with a non-empty prompt.
 */
export function getCustomZoneStyle(zone: SiteZone): CustomZoneStyle | null {
  const props = zone.properties;
  if (!props?.custom_style_enabled) return null;
  const promptText = ((props.custom_style_expanded_prompt as string) || (props.custom_style_prompt as string) || '').trim();
  if (!promptText) return null;
  const attachments = Array.isArray(props.custom_style_attachments)
    ? (props.custom_style_attachments as Array<{ kind?: string; url?: string }>)
    : [];
  const photoUrls = attachments
    .filter(a => a?.kind === 'photo' && typeof a.url === 'string' && a.url)
    .map(a => a.url as string)
    .slice(0, 3);
  return { promptText, photoUrls };
}
