import { Component, Suspense, useEffect, useMemo, type ReactNode } from 'react';
import { useGLTF } from '@react-three/drei';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { useOwnParkAssemblyGround } from './ParkAssemblyGround';
import { direct3DInstanceUserData, direct3DProposalUserData, direct3DStreetJunctionInstanceDescriptor, direct3DZoneInstanceDescriptor } from './direct3dCapture';
import { publicRealmTrialAsset, publicRealmTrialGroundCells, publicRealmTrialPlacement } from './publicRealmTrial';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';
import { clipStreetGeometryOutsideJunction } from './streetJunctionGeometry';
import { buildNativeStreetJunctionGround, nativeLocalJunction, nativeStreetJunctions, type NativeStreetJunction } from './nativeStreetJunction';
import { trimNativeStreetModel } from './nativeStreetModelTrim';

const palette: Record<string, [number, number, number]> = {
  paving: [.53, .50, .43], grass: [.21, .28, .105], soil: [.105, .073, .045], cycle: [.33, .145, .085],
  asphalt: [.10, .115, .11],
};
class TrialBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed ? <group userData={{ publicRealmTrialStatus: 'unavailable' }} /> : this.props.children; }
}

function NativeModel({ zone, placement, junctions }: { zone: SiteZone; placement: NonNullable<ReturnType<typeof publicRealmTrialPlacement>>; junctions: NativeStreetJunction[] }) {
  const { scene } = useGLTF(placement.asset.url);
  const connected = useMemo(() => junctions.filter((item) => item.node.zoneIds.includes(zone.id)), [junctions, zone.id]);
  const model = useMemo(() => trimNativeStreetModel(scene, placement, connected), [scene, placement, connected]);
  useEffect(() => retainResourceForDeferredDisposal(model.owned, geometries => geometries.forEach(geometry => geometry.dispose())), [model]);
  const ground = useMemo(() => {
    const positions: number[] = [], colors: number[] = [];
    for (const cell of publicRealmTrialGroundCells(placement.asset)) {
      const x = cell.x, y = cell.y, w = cell.width / 2, d = cell.depth / 2;
      positions.push(x-w,y-d,0, x+w,y-d,0, x+w,y+d,0, x-w,y-d,0, x+w,y+d,0, x-w,y+d,0);
      for (let i = 0; i < 6; i++) colors.push(...palette[cell.material]);
    }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    geometry.computeVertexNormals();
    let trimmed = geometry;
    for (const junction of connected) {
      const { layout, centerX, centerY } = nativeLocalJunction(junction, placement);
      const next = clipStreetGeometryOutsideJunction(trimmed, layout, centerX, centerY);
      trimmed.dispose(); trimmed = next;
    }
    return trimmed;
  }, [placement, connected]);
  useEffect(() => retainResourceForDeferredDisposal(ground, () => ground.dispose()), [ground]);
  useOwnParkAssemblyGround(zone);
  return <EastNorthUpFrame lat={placement.lat * Math.PI / 180} lon={placement.lng * Math.PI / 180} height={placement.height}>
    <group rotation={[0, 0, placement.yaw]} userData={{ publicRealmTrialStatus: 'ready' }}>
      <mesh geometry={ground} receiveShadow renderOrder={145}><meshStandardMaterial vertexColors roughness={.9} side={THREE.DoubleSide} /></mesh>
      <group rotation={[Math.PI / 2, 0, 0]}><primitive object={model.clone} dispose={null} /></group>
    </group>
  </EastNorthUpFrame>;
}

function NativeJunctionGround({ junction }: { junction: NativeStreetJunction }) {
  const geometry = useMemo(() => buildNativeStreetJunctionGround(junction), [junction]);
  useEffect(() => retainResourceForDeferredDisposal(geometry, () => geometry.dispose()), [geometry]);
  return <group name={`siteforge-direct3d-junction-${junction.node.id}`} userData={{
    ...direct3DProposalUserData('street'),
    ...direct3DInstanceUserData(direct3DStreetJunctionInstanceDescriptor(junction.node.zoneIds)),
  }}>
    <EastNorthUpFrame lat={junction.node.latitude * Math.PI / 180} lon={junction.node.longitude * Math.PI / 180} height={junction.height}>
      <mesh geometry={geometry} receiveShadow renderOrder={146}>
        <meshStandardMaterial vertexColors roughness={.9} side={THREE.DoubleSide} />
      </mesh>
    </EastNorthUpFrame>
  </group>;
}

/** Unreleased fixed-size candidates, only enabled in local development. */
export function GlobePublicRealmTrialLayer({ zones, terrainHeight }: { zones: SiteZone[]; terrainHeight: number }) {
  const junctions = useMemo(() => nativeStreetJunctions(zones, terrainHeight), [zones, terrainHeight]);
  const placements = useMemo(() => new Map(zones.map(zone =>
    [zone.id, publicRealmTrialPlacement(zone, zones, terrainHeight)] as const)), [zones, terrainHeight]);
  return <>{zones.map(zone => {
    const asset = publicRealmTrialAsset(zone);
    if (!asset) return null;
    const placement = placements.get(zone.id);
    const kind = asset.kind === 'street' ? 'street' : 'park';
    return <group key={zone.id + ':' + zone.updated_at} name={'public-realm-trial-' + zone.id}
      userData={{ ...direct3DProposalUserData(kind), ...direct3DInstanceUserData(direct3DZoneInstanceDescriptor(zone.id, kind)) }}>
      <TrialBoundary><Suspense fallback={<group userData={{ publicRealmTrialStatus: 'loading' }} />}>
        {placement ? <NativeModel zone={zone} placement={placement} junctions={junctions} /> : <group userData={{ publicRealmTrialStatus: 'unsupported' }} />}
      </Suspense></TrialBoundary>
    </group>;
  })}{junctions.map(junction => <NativeJunctionGround key={junction.node.id} junction={junction} />)}</>;
}
