import type { Building, SiteZone } from '@/types';
import { getCommunity3DCaptureClaims, resolveCommunity3DKind } from '@/features/community3d/community3d';
import type { Direct3DCaptureBundle } from './globe/direct3dCapture';

export interface VideoCaptureScene {
  projectId: string | undefined;
  zones: SiteZone[];
  buildings: Building[];
}

type InitialVideoCapture = Pick<Direct3DCaptureBundle, 'beautyImageBase64' | 'instanceIdManifest'>;

function currentClaims(scene: VideoCaptureScene) {
  const claims = getCommunity3DCaptureClaims(scene.zones, scene.buildings);
  if (!scene.projectId || !claims?.length) {
    throw new Error('Run Generate to 3D again before capturing your video.');
  }
  return claims;
}

function revision(scene: VideoCaptureScene, claims: ReturnType<typeof currentClaims>): string {
  return JSON.stringify([scene.projectId,
    claims.map((claim) => [claim.zone_id, claim.building_id, claim.source_hash, claim.representation_hash]).sort(),
    scene.zones.map((zone) => [zone.id, zone.updated_at]).sort(),
  ]);
}

/** Initial Single frame video has no later route pass to restore hidden models.
 * Require the mounted authored scene inventory before releasing its beauty
 * image. The manifest comes from scene traversal, NOT visible pixel counts:
 * ordinary occlusion and off-camera geometry remain valid and unchanged. */
export async function captureCompleteVideoFrame(
  capture: () => Promise<InitialVideoCapture>, getScene: () => VideoCaptureScene,
): Promise<string> {
  const initial = getScene(), claims = currentClaims(initial), before = revision(initial, claims);
  const result = await capture();
  const current = getScene(), currentSceneClaims = currentClaims(current);
  if (before !== revision(current, currentSceneClaims)) {
    throw new Error('Your plan changed while the video image was captured. Capture it again.');
  }
  const instances = Object.values(result.instanceIdManifest);
  const zonesById = new Map(current.zones.map((zone) => [zone.id, zone]));
  for (const claim of currentSceneClaims) {
    const kind = resolveCommunity3DKind(zonesById.get(claim.zone_id)!);
    const primary = instances.filter((instance) => instance.zone_id === claim.zone_id && instance.semantic_class === kind);
    if (primary.length !== 1 || (kind === 'building' && primary[0].building_id !== claim.building_id)) {
      throw new Error('Turn on 3D models and wait for your scene to finish loading, then capture your video again.');
    }
  }
  return result.beautyImageBase64;
}
