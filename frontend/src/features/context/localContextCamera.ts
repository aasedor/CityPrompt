import type { Matrix4, PerspectiveCamera } from 'three';

/** Context-only camera copy. All subtraction happens in CPU double precision. */
export function copyCameraToLocalFrame(source: PerspectiveCamera, target: PerspectiveCamera, worldToLocal: Matrix4): void {
  target.copy(source, false);
  target.matrixWorld.multiplyMatrices(worldToLocal, source.matrixWorld);
  target.matrixWorldInverse.copy(target.matrixWorld).invert();
  target.matrixWorld.decompose(target.position, target.quaternion, target.scale);
}
