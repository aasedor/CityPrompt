import { Component, Suspense, useMemo, type ReactNode } from 'react';
import { useGLTF } from '@react-three/drei';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import type { SiteZone } from '@/types';
import { computeCentroid } from '../mapEngine/geoUtils';
import { centreNativeClayClone } from '@/features/legoAssembly/nativeClayPlacement';
import { rectangleDimensions } from '@/features/pickPlace/geometry';
import { resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';
import { resolveZoneTerrainHeight } from './globeTerrainUtils';
import { direct3DInstanceUserData, direct3DZoneInstanceDescriptor } from './direct3dCapture';

/** Isolated local-review GLB. A bad candidate leaves a visible fallback and
 * never takes down the project view or another building. */
class ReviewBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed
    ? <mesh name="review-building-error" userData={{ reviewBuildingStatus: 'error' }} position={[0, 0, 4]}>
        <boxGeometry args={[22, 14, 8]}/><meshBasicMaterial color="#e86a40" wireframe/>
      </mesh>
    : this.props.children; }
}

function BuildingGLB({ url, zone }: { url: string; zone: SiteZone }) {
  const { scene } = useGLTF(url);
  const model = useMemo(() => centreNativeClayClone(scene.clone(true)), [scene]);
  return <group name="review-building-loaded" userData={{ reviewBuildingStatus: 'ready',
    ...direct3DInstanceUserData(direct3DZoneInstanceDescriptor(zone.id, 'building',
      zone.building_id ? { building_id: zone.building_id } : {})) }}
    rotation={[Math.PI / 2, 0, 0]} dispose={null}><primitive object={model}/></group>;
}

export function GlobeReviewBuilding({ zone, zones, terrainHeight }: {
  zone: SiteZone; zones: SiteZone[]; terrainHeight: number;
}) {
  const url = String(zone.properties?.validation_native_url || '');
  const [lng, lat] = computeCentroid(zone.coordinates);
  const storedTerrain = Number(zone.properties?.terrain_elevation_m);
  const height = resolvePreparedSiteTerrainForZone(zone, zones, terrainHeight)
    ?? resolveZoneTerrainHeight(null, Number.isFinite(storedTerrain) ? storedTerrain : null, terrainHeight);
  const degrees = rectangleDimensions(zone.coordinates).degrees;
  if (!url || zone.coordinates.length < 4) return null;
  return <EastNorthUpFrame lat={lat * Math.PI / 180} lon={lng * Math.PI / 180} height={height + .12}>
    <group name={`review-building-${zone.id}`} rotation={[0, 0, degrees * Math.PI / 180]}>
      <ReviewBoundary><Suspense fallback={
        <mesh name="review-building-loading" userData={{ reviewBuildingStatus: 'loading' }} position={[0, 0, 4]}>
          <boxGeometry args={[22, 14, 8]}/><meshBasicMaterial color="#64748b" wireframe/>
        </mesh>
      }><BuildingGLB url={url} zone={zone}/></Suspense></ReviewBoundary>
    </group>
  </EastNorthUpFrame>;
}
