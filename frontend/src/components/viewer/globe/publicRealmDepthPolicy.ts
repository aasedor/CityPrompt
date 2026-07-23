/**
 * Shared occlusion contract for authored park and street geometry.
 *
 * Public-realm surfaces are real scene geometry, never screen-space overlays:
 * they always test against Google Tiles and generated buildings. Authoritative
 * compiled/draped surfaces also write depth so later props seat against the
 * same visible ground. A tile mask controls what source geometry exists; it
 * must never control whether the proposal participates in occlusion.
 */

export interface PublicRealmGroundDepthInput {
  isCompiledGround: boolean;
  hasAuthoredGroundTexture: boolean;
  isPreparedBoundary: boolean;
  isSiteBoundary: boolean;
}

export interface PublicRealmDepthPolicy {
  depthTest: true;
  depthWrite: boolean;
  transparent: boolean;
}

/**
 * Shared physical lift for authored park/street ground above Google Tiles.
 * Fixed public-realm modules must derive their base elevation from this value
 * so the visible surface and the standing geometry cannot drift apart.
 */
export const PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS = 0.08;

/** Small reveal above the authored surface avoids coplanar footings without
 * making posts, playgrounds or fountain basins appear to float. */
export const PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS =
  PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS + 0.02;

/** Constructible street datum. The compiled ground is the prepared subgrade;
 * every street surface is expressed from the same reference so carriageways
 * cannot fall below the site mesh and paint cannot hover above it. */
export const PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS =
  PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS + 0.02;
export const PUBLIC_REALM_STREET_SHARED_SURFACE_LIFT_METERS =
  PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS + 0.01;
export const PUBLIC_REALM_STREET_MARKING_LIFT_METERS =
  PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS + 0.006;
export const PUBLIC_REALM_STREET_CURB_BASE_LIFT_METERS =
  PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS;
export const PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS =
  PUBLIC_REALM_STREET_CURB_BASE_LIFT_METERS + 0.145;
export const PUBLIC_REALM_STREET_TACTILE_LIFT_METERS =
  PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS + 0.006;

export function resolvePublicRealmGroundDepthPolicy({
  isCompiledGround,
  hasAuthoredGroundTexture,
  isPreparedBoundary,
  isSiteBoundary,
}: PublicRealmGroundDepthInput): PublicRealmDepthPolicy {
  return {
    depthTest: true,
    depthWrite: !isSiteBoundary && (
      isCompiledGround || hasAuthoredGroundTexture || isPreparedBoundary
    ),
    transparent: isSiteBoundary,
  };
}

/** Raised section bands and slabs own physical depth. */
export const PUBLIC_REALM_DETAIL_DEPTH = Object.freeze({
  depthTest: true as const,
  depthWrite: true,
});

/** Paint/marking layers test depth but do not occlude later geometry. */
export const PUBLIC_REALM_DECAL_DEPTH = Object.freeze({
  depthTest: true as const,
  depthWrite: false,
});
