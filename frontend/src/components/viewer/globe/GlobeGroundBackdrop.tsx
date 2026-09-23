import { DIRECT_3D_CAPTURE_CONTEXT_USER_DATA } from './direct3dCapture';
import { SITE_GRASS_BACKGROUND } from './sitePreparationSurface';

const noRaycast = () => {};

/** Colour only the missing terrestrial background. A recessed WGS84 shell
 * stays below real terrain, has no picking/support role, and leaves sky rays
 * untouched. Never use scene.background to disguise a ground gap. */
export function GlobeGroundBackdrop() {
  return <mesh
    name="siteforge-google-ground-backdrop"
    scale={[6378137 - 12000, 6378137 - 12000, 6356752.314245 - 12000]}
    renderOrder={-1000}
    raycast={noRaycast}
    userData={DIRECT_3D_CAPTURE_CONTEXT_USER_DATA}
  >
    <sphereGeometry args={[1, 256, 128]} />
    <meshBasicMaterial color={SITE_GRASS_BACKGROUND} fog={false} toneMapped={false} depthWrite={false} />
  </mesh>;
}
