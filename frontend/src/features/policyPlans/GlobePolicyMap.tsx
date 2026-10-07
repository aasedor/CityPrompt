import { forwardRef, useImperativeHandle, useMemo, useRef } from 'react';
import * as THREE from 'three';
import { DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA } from '@/components/viewer/globe/direct3dCapture';
import { GlobeZoningSurface } from '@/features/referenceLayers/GlobeZoningSurface';
import type { LocalAreaPolicyState } from './useLocalAreaPolicy';
import { pickPolicyMesh } from './policyPicking';

export type GlobePolicyMapProps = Pick<LocalAreaPolicyState, 'data' | 'enabled' | 'opacity' | 'selected' | 'selectArea' | 'clearSelection'>;
export type PolicyMapHandle = { pick: (ndcX: number, ndcY: number, camera: THREE.Camera) => string | null };

/** Read-only cartography. Never changes terrain, site geometry or zoning studies. */
export const GlobePolicyMap = forwardRef<PolicyMapHandle, GlobePolicyMapProps & { terrainHeight: number }>(function GlobePolicyMap({ data, enabled, opacity, terrainHeight, selected }, ref) {
  const base = useRef<THREE.Group>(null);
  const raycaster = useMemo(() => new THREE.Raycaster(), []);
  useImperativeHandle(ref, () => ({ pick: (x, y, camera) => {
    if (!enabled || opacity <= 0) return null;
    const mesh = base.current?.getObjectByName('calgary-land-use-fill');
    if (!(mesh instanceof THREE.Mesh)) return null;
    raycaster.setFromCamera(new THREE.Vector2(x, y), camera);
    return pickPolicyMesh(mesh, raycaster);
  } }), [enabled, opacity, raycaster]);
  const highlight = useMemo(() => data && selected ? { ...data, districts: data.districts.filter(area => selected.featureId
    ? area.id === selected.featureId : area.label === selected.designation.name) } : undefined, [data, selected]);
  if (!enabled || !data || opacity <= 0) return null;
  return <group name="local-policy-map" userData={DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA}>
    <group ref={base}><GlobeZoningSurface data={data} terrainHeight={terrainHeight} lines={false} fill fillOpacity={opacity} /></group>
    {highlight && <group name="local-policy-selection"><GlobeZoningSurface data={highlight} terrainHeight={terrainHeight} lines fill={false} fillOpacity={0} /></group>}
  </group>;
});
