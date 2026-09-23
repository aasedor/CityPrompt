import { Component, Suspense, useEffect, useMemo, type ReactNode } from 'react';
import { useGLTF } from '@react-three/drei';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { useOwnParkAssemblyGround } from './ParkAssemblyGround';
import { direct3DInstanceUserData, direct3DProposalUserData, direct3DZoneInstanceDescriptor } from './direct3dCapture';
import { publicRealmTrialAsset, publicRealmTrialGroundCells, publicRealmTrialPlacement, TRIAL_GROUND_MATERIALS } from './publicRealmTrial';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';

const palette: Record<string, [number, number, number]> = {
  paving: [.53, .50, .43], grass: [.21, .28, .105], soil: [.105, .073, .045], cycle: [.33, .145, .085],
};
class TrialBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed ? <group userData={{ publicRealmTrialStatus: 'unavailable' }} /> : this.props.children; }
}

function NativeModel({ zone, placement }: { zone: SiteZone; placement: NonNullable<ReturnType<typeof publicRealmTrialPlacement>> }) {
  const { scene } = useGLTF(placement.asset.url);
  const model = useMemo(() => {
    const clone = scene.clone(true);
    const remove: THREE.Object3D[] = [];
    clone.traverse(object => {
      if (!(object instanceof THREE.Mesh)) return;
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      // The preview slabs are discarded. Ground is rebuilt from the recipe on
      // the authoritative prepared datum; rigid courts and all props stay native.
      if (materials.every(m => TRIAL_GROUND_MATERIALS.has(m.name))) remove.push(object);
      object.castShadow = true; object.receiveShadow = true; object.renderOrder = 148;
    });
    remove.forEach(object => object.removeFromParent());
    return clone;
  }, [scene]);
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
    return geometry;
  }, [placement.asset]);
  useEffect(() => retainResourceForDeferredDisposal(ground, () => ground.dispose()), [ground]);
  useOwnParkAssemblyGround(zone);
  return <EastNorthUpFrame lat={placement.lat * Math.PI / 180} lon={placement.lng * Math.PI / 180} height={placement.height}>
    <group rotation={[0, 0, placement.yaw]} userData={{ publicRealmTrialStatus: 'ready' }}>
      <mesh geometry={ground} receiveShadow renderOrder={145}><meshStandardMaterial vertexColors roughness={.9} side={THREE.DoubleSide} /></mesh>
      <group rotation={[Math.PI / 2, 0, 0]}><primitive object={model} dispose={null} /></group>
    </group>
  </EastNorthUpFrame>;
}

/** Unreleased fixed-size candidates, only enabled in local development. */
export function GlobePublicRealmTrialLayer({ zones, terrainHeight }: { zones: SiteZone[]; terrainHeight: number }) {
  return <>{zones.map(zone => {
    const asset = publicRealmTrialAsset(zone);
    if (!asset) return null;
    const placement = publicRealmTrialPlacement(zone, zones, terrainHeight);
    const kind = asset.kind === 'street' ? 'street' : 'park';
    return <group key={zone.id + ':' + zone.updated_at} name={'public-realm-trial-' + zone.id}
      userData={{ ...direct3DProposalUserData(kind), ...direct3DInstanceUserData(direct3DZoneInstanceDescriptor(zone.id, kind)) }}>
      <TrialBoundary><Suspense fallback={<group userData={{ publicRealmTrialStatus: 'loading' }} />}>
        {placement ? <NativeModel zone={zone} placement={placement} /> : <group userData={{ publicRealmTrialStatus: 'unsupported' }} />}
      </Suspense></TrialBoundary>
    </group>;
  })}</>;
}
