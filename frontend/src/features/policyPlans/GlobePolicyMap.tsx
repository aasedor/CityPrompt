import { DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA } from '@/components/viewer/globe/direct3dCapture';
import { GlobeZoningSurface } from '@/features/referenceLayers/GlobeZoningSurface';
import type { RileyPolicyState } from './useRileyPolicy';

export type GlobePolicyMapProps = Pick<RileyPolicyState, 'data' | 'enabled' | 'opacity'>;

/** Read-only cartography. Never changes terrain, site geometry or zoning studies. */
export function GlobePolicyMap({ data, enabled, opacity, terrainHeight }: GlobePolicyMapProps & { terrainHeight: number }) {
  if (!enabled || !data || opacity <= 0) return null;
  return <group name="riley-policy-map" userData={DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA}>
    <GlobeZoningSurface data={data} terrainHeight={terrainHeight} lines={false} fill fillOpacity={opacity} />
  </group>;
}
