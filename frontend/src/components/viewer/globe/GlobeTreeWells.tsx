import { useEffect, useLayoutEffect, useMemo, useRef } from 'react';
import * as THREE from 'three';
import { createTreeWellGeometry, TREE_WELL_SIZE_M, type TreeWellStyle } from './treeWellGeometry';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';

export interface TreeWellPlacement {
  x: number; y: number; z: number; yawRad: number;
  widthM?: number; lengthM?: number;
}

function WellInstances({ placements, style, renderOrder }: {
  placements: TreeWellPlacement[]; style: TreeWellStyle; renderOrder: number;
}) {
  const geometry = useMemo(() => createTreeWellGeometry(style), [style]);
  const ref = useRef<THREE.InstancedMesh>(null);
  useEffect(() => retainResourceForDeferredDisposal(geometry, g => g.dispose()), [geometry]);
  useLayoutEffect(() => {
    if (!ref.current) return;
    const matrix = new THREE.Matrix4(), p = new THREE.Vector3(), q = new THREE.Quaternion();
    const s = new THREE.Vector3(), up = new THREE.Vector3(0, 0, 1);
    placements.forEach((well, i) => {
      matrix.compose(p.set(well.x, well.y, well.z), q.setFromAxisAngle(up, well.yawRad),
        s.set((well.lengthM ?? TREE_WELL_SIZE_M) / TREE_WELL_SIZE_M,
          (well.widthM ?? TREE_WELL_SIZE_M) / TREE_WELL_SIZE_M, 1));
      ref.current!.setMatrixAt(i, matrix);
    });
    ref.current.count = placements.length;
    ref.current.instanceMatrix.needsUpdate = true;
    ref.current.computeBoundingSphere();
  }, [placements, geometry]);
  return <instancedMesh ref={ref} name={`tree-wells-${style}`} args={[geometry, undefined, placements.length]}
    renderOrder={renderOrder} receiveShadow castShadow>
    <meshStandardMaterial vertexColors roughness={.92} side={THREE.DoubleSide} />
  </instancedMesh>;
}

export function GlobeTreeWells({ placements, style = 'grate', renderOrder = 146 }: {
  placements: TreeWellPlacement[]; style?: TreeWellStyle; renderOrder?: number;
}) {
  return placements.length ? <WellInstances placements={placements} style={style} renderOrder={renderOrder} /> : null;
}
