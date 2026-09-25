import type { SiteZone, SiteZoneProperties } from '@/types';
import { bufferLineToPolygon, extractZoneCenterline, parsePersistedCenterline } from '@/utils/roadGeometry';
import { resolvePilotStreetSectionProfile } from '@/components/viewer/globe/streetSectionProfiles';
import { CANONICAL_CHOICES, canonicalDrawing, type CanonicalSelection } from './canonicalCatalogue';
import type { StreetAsset } from './assetRegistry';
import { roundAuthoredStreetRoute } from '@/utils/streetRouteCurves';

const cache = new Map<string, StreetAsset>();

/** The live section resolver owns width; catalogue images never define geometry. */
export function canonicalStreetAsset(selection: CanonicalSelection): StreetAsset {
  const { choice, variant } = selection;
  if (choice.domain !== 'street_pathway') throw new Error('Choose a street archetype.');
  const id = `canonical-street:${choice.option.id}:${variant?.id ?? ''}`;
  const cached = cache.get(id);
  if (cached) return cached;
  const properties = canonicalDrawing(selection).properties;
  const variantId = variant?.id ?? `${choice.option.id}_v0`;
  Object.assign(properties, { road_archetype_id: choice.option.id, road_selected_variant_id: variantId });
  const profile = resolvePilotStreetSectionProfile({ properties });
  if (!profile || !Number.isFinite(profile.rowM) || profile.rowM <= 0) throw new Error('This street has no usable cross-section.');
  const asset: StreetAsset = {
    id, kind: 'street', definitionVersion: 1, readiness: 'candidate', reshapeMode: 'fixed_section_route',
    label: choice.option.label, description: variant?.description ?? choice.option.description,
    thumbnail: variant?.thumbnailUrl ?? choice.option.photoUrl, calgaryGuide: choice.option.calgaryGuide!,
    model: { variantId, revision: null, method: 'catalogue_section' }, sectionWidth: profile.rowM,
    properties: { ...properties, width: profile.rowM, pick_place_street_section: variantId,
      pick_place_automatic_3d: true, community_3d_mask_existing_tiles: true,
      road_standard_citation: properties.road_standard_citation ?? 'City Prompt representative teaching section' },
  };
  cache.set(id, asset);
  return asset;
}

export function canonicalStreetForZone(zone: Pick<SiteZone, 'zone_type' | 'properties'>): StreetAsset | undefined {
  const props = zone.properties;
  if (zone.zone_type !== 'road' || !props?.pick_place_street_section) return undefined;
  const choice = CANONICAL_CHOICES.find(c => c.domain === 'street_pathway' && c.option.id === props.road_archetype_id);
  if (!choice || props.pick_place_street_section !== props.road_selected_variant_id) return undefined;
  const variant = choice.option.variants?.find(v => v.id === props.road_selected_variant_id);
  if (!variant) return undefined;
  return canonicalStreetAsset({ choice, variant });
}

/** Centreline, identity and buffered footprint must change in one undoable write. */
export function streetDesignUpdate(zone: SiteZone, asset: StreetAsset): { coordinates: number[][]; properties: SiteZoneProperties } {
  const savedControls = parsePersistedCenterline(zone.properties?.plan_route_controls);
  const controls = savedControls ?? extractZoneCenterline(zone);
  const line = savedControls && savedControls.length >= 3
    ? roundAuthoredStreetRoute(controls, asset.sectionWidth, asset.properties)
    : controls;
  return { coordinates: bufferLineToPolygon(line, asset.sectionWidth),
    properties: { ...zone.properties, ...asset.properties, procedural_road: 0, public_realm_lego: undefined,
      plan_centerline: line, plan_route_controls: savedControls ?? undefined } };
}
