import { useEffect, useMemo } from 'react';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import { DoubleSide } from 'three';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { type PedestrianStrip, type ConnectionResult } from '@/features/pickPlace/pedestrianConnections';
import { useSharedSiteGround } from './SharedSiteGroundProvider';
import { createSharedGroundTriangulation } from './sharedGroundGeometry';
import { resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';
import { buildParkAccessBridgeGeometry } from './parkAccessBridgeGeometry';
import { streetConnectionCaptureUserData } from './pedestrianCapture';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';

function Strip({ strip, owner, zones, terrainHeight }: { strip: PedestrianStrip; owner: SiteZone; zones: SiteZone[]; terrainHeight: number }) {
  const ground = useSharedSiteGround();
  const [lng, lat] = strip.start;
  const prepared = resolvePreparedSiteTerrainForZone(owner, zones, terrainHeight);
  const height = ground.status === 'ready' ? ground.heightAt(lng, lat) : prepared;
  const geometry = useMemo(() => {
    if (height === null || (ground.status !== 'inactive' && ground.status !== 'ready')) return null;
    const local = ([x, y]: [number, number]): [number, number] => [(x-lng)*metersPerDegLon(lat), (y-lat)*METERS_PER_DEG_LAT];
    const groundAt = ground.status === 'ready' ? (x: number, y: number) => {
      const z = ground.heightAt(lng+x/metersPerDegLon(lat), lat+y/METERS_PER_DEG_LAT);
      return z === null ? null : z-height;
    } : undefined;
    return buildParkAccessBridgeGeometry({ start: [0,0], end: local(strip.end), widthM: strip.widthM,
      streetLiftM: strip.startLiftM, endLiftM: strip.endLiftM, groundAt,
      groundGrid: ground.snapshot ? createSharedGroundTriangulation(ground.snapshot,lng,lat) : undefined });
  }, [ground, height, lat, lng, strip]);
  useEffect(() => geometry ? retainResourceForDeferredDisposal(geometry, owned=>owned.dispose()) : undefined,[geometry]);
  if (!geometry || height === null) return null;
  return <EastNorthUpFrame lat={lat*Math.PI/180} lon={lng*Math.PI/180} height={height}>
    <mesh name={`pedestrian-${strip.id}`} geometry={geometry} renderOrder={145}>
      <meshStandardMaterial color={strip.color} roughness={0.94} side={DoubleSide} />
    </mesh>
  </EastNorthUpFrame>;
}

export function GlobePedestrianConnections({ results, zones, terrainHeight }: {
  results: ConnectionResult[]; zones: SiteZone[]; terrainHeight: number;
}) {
  const ground = useSharedSiteGround();
  return <>{results.map(result => {
    // On measured terrain the owning model draws its foundation-aware approach.
    // Retain this legacy drape for prepared sites and raised street crossings.
    if (result.kind === 'building' && ground.status !== 'inactive') return null;
    const owner=zones.find(z=>z.id===result.ownerId); if(!owner)return null;
    const captureData=streetConnectionCaptureUserData(owner,zones); if(!captureData)return null;
    return <group key={`${result.kind}:${result.id}`} userData={captureData}>
      {result.strips.map(strip=><Strip key={strip.id} strip={strip} owner={owner} zones={zones} terrainHeight={terrainHeight} />)}
    </group>;
  })}</>;
}
