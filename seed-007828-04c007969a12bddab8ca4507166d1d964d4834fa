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
