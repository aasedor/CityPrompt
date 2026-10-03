import { createContext, useContext, useEffect, useMemo, type ReactNode } from 'react';
import * as THREE from 'three';
import { createSitePreparationTexture } from './sitePreparationSurface';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';
import { useSiteLandscapeTexture } from '@/features/siteLandscape/useSiteLandscapeTexture';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { getResidualLandscapeRecipe, residualLandscapeBounds } from './residualLandscape';
import { resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';
import type { SiteZone } from '@/types';
import type { FootprintFrame } from './buildingPlacement';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '../mapEngine/geoUtils';

const GroundFinish = createContext<{ boundary: SiteZone; zones: SiteZone[]; texture: THREE.Texture | null } | null>(null);
function PreparedGroundFinish({ boundary, zones, children }: { boundary: SiteZone; zones: SiteZone[]; children: ReactNode }) {
  const recipe = getResidualLandscapeRecipe(boundary);
  const texture = useSiteLandscapeTexture(boundary, recipe, true, zones);
  useEffect(() => texture ? retainResourceForDeferredDisposal(texture, t => t.dispose()) : undefined, [texture]);
  const value = useMemo(() => ({ boundary, zones, texture }), [boundary, zones, texture]);
  return <GroundFinish.Provider value={value}>{children}</GroundFinish.Provider>;
}
export function BuildingLandscapeSurfaceProvider({ zones, children }: { zones: SiteZone[]; children: ReactNode }) {
  const boundary = getActiveSiteBoundary(zones);
  return boundary ? <PreparedGroundFinish boundary={boundary} zones={zones}>{children}</PreparedGroundFinish> : <>{children}</>;
}

/** Keep taller retaining faces concrete. Ground cover follows horizontal caps
 * and shallow prepared edges; authored stairs and walks remain above them. */
export function landscapedFoundationGeometry(source: THREE.BufferGeometry, coverShallowSides = false) {
  const geometry = source.clone();
  const p = geometry.getAttribute('position'), index = geometry.getIndex();
  geometry.computeBoundingBox();
  const shallow = coverShallowSides && geometry.boundingBox !== null
    && geometry.boundingBox.max.z - geometry.boundingBox.min.z <= .15;
  const uv = new THREE.Float32BufferAttribute(p.count * 2, 2);
  for (let i = 0; i < p.count; i++) uv.setXY(i, p.getX(i) / 6, p.getY(i) / 6);
  geometry.setAttribute('uv', uv);
  geometry.clearGroups();
  const count = index?.count ?? p.count;
  for (let i = 0; i < count; i += 3) {
    const a = index ? index.getX(i) : i, b = index ? index.getX(i + 1) : i + 1, c = index ? index.getX(i + 2) : i + 2;
    const cap = Math.max(p.getZ(a), p.getZ(b), p.getZ(c)) - Math.min(p.getZ(a), p.getZ(b), p.getZ(c)) < .0001;
    const materialIndex = cap || shallow ? 1 : 0;
    const previous = geometry.groups[geometry.groups.length - 1];
    if (previous?.materialIndex === materialIndex) previous.count += 3;
    else geometry.addGroup(i, 3, materialIndex);
  }
  return geometry;
}

export function BuildingFoundationSurface({ geometry, renderOrder, userData, frame, zone }: {
  geometry: THREE.BufferGeometry; renderOrder: number; userData?: Record<string, unknown>; frame?: FootprintFrame; zone?: SiteZone;
}) {
  const ground = useContext(GroundFinish);
  const matched = ground && frame && zone && resolvePreparedSiteTerrainForZone(zone, ground.zones, 0) !== null ? ground : null;
  const resources = useMemo(() => {
    const result = { geometry: landscapedFoundationGeometry(geometry, Boolean(matched)), texture: createSitePreparationTexture('building-foundation', 128, 'grass') };
    if (matched && frame) {
      const bounds = residualLandscapeBounds(matched.boundary.coordinates), recipe = getResidualLandscapeRecipe(matched.boundary);
      const east = metersPerDegLon(frame.centroidLat), width = (bounds.east - bounds.west) * east,
        depth = (bounds.north - bounds.south) * METERS_PER_DEG_LAT, short = Math.max(.01, Math.min(width, depth));
      const repeatX = recipe ? 1 : Math.max(4, width / short * 4), repeatY = recipe ? 1 : Math.max(4, depth / short * 4);
      const p = result.geometry.getAttribute('position'), uv = result.geometry.getAttribute('uv');
      for (let i = 0; i < p.count; i++) uv.setXY(i,
        ((frame.centroidLng - bounds.west) * east + p.getX(i)) / Math.max(.01, width) * repeatX,
        ((frame.centroidLat - bounds.south) * METERS_PER_DEG_LAT + p.getY(i)) / Math.max(.01, depth) * repeatY);
    }
    return result;
  }, [geometry, matched, frame]);
  useEffect(() => retainResourceForDeferredDisposal(resources, r => { r.geometry.dispose(); r.texture.dispose(); }), [resources]);
  return <mesh name="landscaped-building-foundation" geometry={resources.geometry} renderOrder={renderOrder} userData={userData}>
    <meshStandardMaterial attach="material-0" color="#8f8c84" roughness={.95} side={THREE.DoubleSide}/>
    <meshStandardMaterial attach="material-1" map={matched?.texture ?? resources.texture} roughness={1} side={THREE.DoubleSide}/>
  </mesh>;
}
