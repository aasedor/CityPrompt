import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import { validMapCleanupBoxes, type MapCleanupBox } from './mapCleanup';
import { DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA } from './direct3dCapture';

export function MapCleanupPreview({ box }: { box: MapCleanupBox | null }) {
  if (!box || !validMapCleanupBoxes([box]).length) return null;
  return <EastNorthUpFrame lat={box.lat * Math.PI / 180} lon={box.lng * Math.PI / 180} height={box.altitude}>
    <mesh rotation={[0, 0, box.yaw * Math.PI / 180]} raycast={() => {}} userData={{ ...DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA }}>
      <boxGeometry args={[box.width, box.depth, box.height]} /><meshBasicMaterial color="#ff8c00" wireframe depthTest={false} />
    </mesh>
  </EastNorthUpFrame>;
}
