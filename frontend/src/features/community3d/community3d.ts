import type { Building, SiteZone, SiteZoneProperties } from '@/types';

/** The three pieces of a master plan that can be compiled into the globe. */
export type Community3DKind = 'building' | 'park' | 'street';

export type Community3DGenerator =
  | 'lego_assembly'
  | 'planned_massing'
  | 'meshy'
  | 'park_kit'
  | 'street_section';

export interface Community3DMeta {
  schema_version: 1;
  state: 'compiled';
  kind: Community3DKind;
  generator: Community3DGenerator;
  compiled_at: string;
  /** Server-authored fingerprint of geometry and all authored 3D inputs. */
  source_hash?: string;
  /** Server-authored fingerprint of the exact mounted kit/model content. */
  representation_hash?: string;
}

export interface Community3DCaptureClaim {
  zone_id: string;
  source_hash: string;
  representation_hash: string;
  building_id?: string;
}

export interface Community3DBuildingRepresentation {
  schema_version: 1;
  zone_id: string;
  generator: Community3DGenerator;
  representation_hash: string;
  compiled_at: string;
}

/**
 * True only when a mounted Building is the exact representation owned by the
 * current persisted source zone. Older model-only records remain useful
 * project context, but must not inherit a paid Direct 3D proposal role.
 */
export function isCurrentCommunity3DBuildingRepresentation(
  zone: SiteZone,
  building: Building,
): boolean {
  if (
    resolveCommunity3DKind(zone) !== 'building'
    || zone.building_id !== building.id
    || !hasCommunity3DSourceFingerprint(zone)
  ) return false;

  const meta = getCommunity3DMeta(zone);
  const marker = building.specifications?.community3DRepresentation as
    | Community3DBuildingRepresentation
    | undefined;
  return Boolean(
    meta
    && marker
    && marker.schema_version === 1
    && marker.zone_id === zone.id
    && marker.generator === meta.generator
    && marker.representation_hash === meta.representation_hash
    && marker.compiled_at === meta.compiled_at,
  );
}

/** Building IDs safe to classify as editable Direct 3D proposal content. */
export function getCurrentCommunity3DBuildingIds(
  zones: SiteZone[],
  buildings: Building[],
): Set<string> {
  const buildingsById = new Map(buildings.map((building) => [building.id, building]));
  const ids = new Set<string>();
  for (const zone of zones) {
    if (!zone.building_id) continue;
    const building = buildingsById.get(zone.building_id);
    if (building && isCurrentCommunity3DBuildingRepresentation(zone, building)) {
      ids.add(building.id);
    }
  }
  return ids;
}

const BUILDING_ZONE_TYPES = new Set([
  'building',
  'residential',
  'development_area',
  'development',
]);

const PARK_ZONE_TYPES = new Set([
  'green_space',
  'park',
  'plaza',
  // The site-planner toolbar stores its user-facing Plaza tool as `parking`
  // for legacy API compatibility. Treat it as public realm here so a plaza
  // is not silently omitted from Community 3D compilation.
  'parking',
]);

const STREET_ZONE_TYPES = new Set(['road', 'street', 'path']);

function propertiesOf(zone: SiteZone): Record<string, unknown> {
  return (zone.properties ?? {}) as Record<string, unknown>;
}

/**
 * Resolve a planner polygon to the 3D system that owns it. Framework-height
 * overlays are deliberately excluded: they guide the plan but are not objects
 * that should become a second set of buildings.
 */
export function resolveCommunity3DKind(zone: SiteZone): Community3DKind | null {
  if (zone.zone_type === 'site_boundary') return null;

  const props = propertiesOf(zone);
  const role = typeof props._plan_role === 'string' ? props._plan_role : undefined;
  if (role === 'framework_height') return null;

  if (role === 'street' || STREET_ZONE_TYPES.has(zone.zone_type)) return 'street';
  if (role === 'open_space' || role === 'courtyard' || PARK_ZONE_TYPES.has(zone.zone_type)) {
    return 'park';
  }
  if (
    role === 'building'
    || BUILDING_ZONE_TYPES.has(zone.zone_type)
    || Boolean(props.development_archetype_id)
  ) {
    return 'building';
  }
  return null;
}

export function getCommunity3DMeta(zone: SiteZone): Community3DMeta | null {
  const raw = propertiesOf(zone).community_3d;
  if (!raw || typeof raw !== 'object') return null;
  const meta = raw as Partial<Community3DMeta>;
  if (
    meta.schema_version !== 1
    || meta.state !== 'compiled'
    || !['building', 'park', 'street'].includes(meta.kind ?? '')
    || typeof meta.generator !== 'string'
    || typeof meta.compiled_at !== 'string'
  ) {
    return null;
  }
  return meta as Community3DMeta;
}

export function isCommunity3DCompiled(zone: SiteZone): boolean {
  const kind = resolveCommunity3DKind(zone);
  const meta = getCommunity3DMeta(zone);
  return Boolean(kind && meta?.kind === kind);
}

/** Paid Direct 3D requires the stronger post-fingerprint compile contract.
 * Legacy compiled scenes remain visible but must be rebuilt once before they
 * can spend render credits. */
export function hasCommunity3DSourceFingerprint(zone: SiteZone): boolean {
  const meta = getCommunity3DMeta(zone);
  return Boolean(
    meta?.source_hash
    && /^[a-f0-9]{64}$/i.test(meta.source_hash)
    && meta.representation_hash
    && /^[a-f0-9]{64}$/i.test(meta.representation_hash),
  );
}

/** Bind a Direct capture to the exact compiled zone/model snapshot visible in
 * this browser render. The server recomputes both hashes under the project lock
 * before reserving credits, so a stale tab fails without spend. */
export function getCommunity3DCaptureClaims(
  zones: SiteZone[],
  buildings: Building[],
): Community3DCaptureClaim[] | null {
  const communityZones = zones.filter((zone) => resolveCommunity3DKind(zone) !== null);
  const buildingsById = new Map(buildings.map((building) => [building.id, building]));
  const claims: Community3DCaptureClaim[] = [];
  for (const zone of communityZones) {
    const kind = resolveCommunity3DKind(zone);
    const meta = getCommunity3DMeta(zone);
    if (!kind || !hasCommunity3DSourceFingerprint(zone) || !meta) return null;
    if (kind === 'building') {
      if (!zone.building_id) return null;
      const building = buildingsById.get(zone.building_id);
      if (!building || !Array.isArray(building.footprint_coordinates)
        || building.footprint_coordinates.length < 3) return null;
      if (!isCurrentCommunity3DBuildingRepresentation(zone, building)) return null;

      const hasGeneratedModel = Boolean(building.lod_urls?.['0'] ?? building.model_url);
      const specifications = building.specifications ?? {};
      if (
        (meta.generator === 'lego_assembly' && typeof specifications.legoAssembly !== 'object')
        || (
          meta.generator === 'planned_massing'
          && (typeof specifications.plannedMassing !== 'object' || hasGeneratedModel)
        )
        || (meta.generator === 'meshy' && !hasGeneratedModel)
      ) return null;
    }
    claims.push({
      zone_id: zone.id,
      source_hash: meta.source_hash!,
      representation_hash: meta.representation_hash!,
      ...(kind === 'building' ? { building_id: zone.building_id } : {}),
    });
  }
  return claims;
}

export type Community3DAction = 'generate' | 'complete' | 'rebuild';

/** User-facing action state for a mixed plan. Rebuild remains available after
 * completion so newly imported detailed building families can replace honest
 * planned massing, while the label prevents an already-built scene from
 * looking as if it has never been generated. */
export function resolveCommunity3DAction(zones: SiteZone[]): Community3DAction {
  const communityZones = zones.filter((zone) => resolveCommunity3DKind(zone) !== null);
  if (communityZones.length === 0) return 'generate';
  const compiledCount = communityZones.filter(isCommunity3DCompiled).length;
  if (compiledCount === 0) return 'generate';
  if (compiledCount === communityZones.length) return 'rebuild';
  return 'complete';
}

/** Resolve the exact transaction scope behind the user-facing action.
 * `Complete` is intentionally incremental: already-compiled buildings and
 * public-realm systems are left untouched. `Generate` and explicit `Rebuild`
 * own the whole community, with Rebuild providing the upgrade path when a
 * detailed module family replaces planned massing. */
export function selectCommunity3DCompileZones(
  zones: SiteZone[],
  action = resolveCommunity3DAction(zones),
): SiteZone[] {
  const communityZones = zones.filter((zone) => resolveCommunity3DKind(zone) !== null);
  if (action !== 'complete') return communityZones;
  return communityZones.filter((zone) => !isCommunity3DCompiled(zone));
}

/**
 * Planner-created ground zones stay as coloured planning polygons until the
 * user explicitly builds the community. Manually drawn ground zones retain
 * their historical immediate-preview behaviour.
 */
export function shouldRenderCommunityGround(zone: SiteZone): boolean {
  const kind = resolveCommunity3DKind(zone);
  if (kind !== 'park' && kind !== 'street') return false;
  const props = propertiesOf(zone);
  const isMasterPlanZone = typeof props._plan_scenario === 'string';
  if (!isMasterPlanZone) return true;
  // Existing AI park drapes are already authored 3D proposal content and must
  // not disappear when this schema is introduced to an older project.
  if (kind === 'park' && props.park_ground_texture) return true;
  return isCommunity3DCompiled(zone);
}

/**
 * Furniture, vegetation, structures, and other standing proposal objects are
 * generated content—not drawing previews. Even a manually drawn park keeps
 * only its flat planning polygon/ground drape until the user explicitly runs
 * Generate 3D (the LEGO Builder community compile), which stamps this meta.
 */
export function shouldRenderCommunityProps(zone: SiteZone): boolean {
  return isCommunity3DCompiled(zone);
}

/**
 * Public-realm ground normally drapes directly over Google terrain. Cutting a
 * separate stencil hole beneath it can expose the pale scene background when
 * the independently sampled mask and drape anchors differ by even a few
 * metres. Enable destructive tile replacement only for a zone that explicitly
 * declares source geometry must be removed; prepared site-boundary masks and
 * replacement buildings use their existing dedicated paths.
 */
export function shouldMaskCommunityGroundTiles(zone: SiteZone): boolean {
  const kind = resolveCommunity3DKind(zone);
  if (kind !== 'park' && kind !== 'street') return false;
  const props = propertiesOf(zone);
  return props.community_3d_mask_existing_tiles === true
    && (isCommunity3DCompiled(zone) || (kind === 'park' && Boolean(props.park_ground_texture)));
}

export function generatorForKind(
  kind: Community3DKind,
  buildingGenerator: Extract<Community3DGenerator, 'lego_assembly' | 'meshy'> = 'lego_assembly',
): Community3DGenerator {
  if (kind === 'park') return 'park_kit';
  if (kind === 'street') return 'street_section';
  return buildingGenerator;
}

export function withCommunity3DMeta(
  zone: SiteZone,
  generator = generatorForKind(resolveCommunity3DKind(zone) ?? 'building'),
  compiledAt = new Date().toISOString(),
): SiteZoneProperties {
  const kind = resolveCommunity3DKind(zone);
  if (!kind) return { ...(zone.properties ?? {}) };
  return {
    ...(zone.properties ?? {}),
    community_3d: {
      schema_version: 1,
      state: 'compiled',
      kind,
      generator,
      compiled_at: compiledAt,
    } satisfies Community3DMeta,
  };
}
