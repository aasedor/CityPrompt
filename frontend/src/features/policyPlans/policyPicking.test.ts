import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { zoningSurfaceGeometry } from '@/features/referenceLayers/zoningSurfaceGeometry';
import type { Position, ZoningOverlay } from '@/features/referenceLayers/zoningLabels';
import { pickPolicyMesh, policyInspectionAllowed } from './policyPicking';

function rectangle(w: number, s: number, e: number, n: number): Position[] {
  return [[w,s],[e,s],[e,n],[w,n],[w,s]];
}
const data: ZoningOverlay = { bounds: [-114.12,51.01,-114.116,51.012], loadedAt: '', districts: [
  { id: 'park', label: 'Parks and Open Space', color: '#70a355', anchor: [-114.119,51.011], polygon: [rectangle(-114.12,51.01,-114.118,51.012),rectangle(-114.1195,51.0105,-114.1185,51.0115)] },
  { id: 'local', label: 'Neighbourhood Local', color: '#fff4b2', anchor: [-114.117,51.011], polygon: [rectangle(-114.118,51.01,-114.116,51.012)] },
] };

describe('policy surface picking', () => {
  it('selects the displayed triangle in top and oblique views without enabling native raycasting', () => {
    const { fill } = zoningSurfaceGeometry(data, 1100);
    const mesh = new THREE.Mesh(fill, new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }));
    mesh.raycast = () => {}; // The renderer deliberately excludes normal terrain/model picking.
    const position = fill.attributes.position;
    for (const range of fill.userData.zoningFaceRanges) {
      const face = range.firstFace * 3;
      const center = new THREE.Vector3();
      for (let i=0; i<3; i++) center.add(new THREE.Vector3().fromBufferAttribute(position, face+i));
      center.divideScalar(3);
      for (const offset of [new THREE.Vector3(0,0,100), new THREE.Vector3(30,-70,100)]) {
        const ray = new THREE.Raycaster(center.clone().add(offset), offset.clone().negate().normalize());
        expect(pickPolicyMesh(mesh, ray)).toBe(range.id);
        expect(ray.intersectObject(mesh)).toHaveLength(0);
      }
    }
    // Centre of the park's hole lies ~70 m west of the combined origin.
    expect(pickPolicyMesh(mesh, new THREE.Raycaster(new THREE.Vector3(-70,0,100),new THREE.Vector3(0,0,-1)))).toBeNull();
    expect(pickPolicyMesh(mesh, new THREE.Raycaster(new THREE.Vector3(500,500,100),new THREE.Vector3(0,0,-1)))).toBeNull();
    const hidden = new THREE.Group(); hidden.add(mesh); hidden.visible = false;
    expect(pickPolicyMesh(mesh, new THREE.Raycaster(new THREE.Vector3(70,0,100),new THREE.Vector3(0,0,-1)))).toBeNull();
    fill.dispose(); mesh.material.dispose();
  });
  it('gives authoring, measurement, navigation and other picking modes priority', () => {
    const state = { enabled: true, opacity: .5, paused: false, drawing: false, placing: false, measuring: false, streetView: false, dragged: false };
    expect(policyInspectionAllowed(state)).toBe(true);
    for (const key of ['paused','drawing','placing','measuring','streetView','dragged'] as const) expect(policyInspectionAllowed({ ...state, [key]: true })).toBe(false);
    expect(policyInspectionAllowed({ ...state, enabled: false })).toBe(false);
    expect(policyInspectionAllowed({ ...state, opacity: 0 })).toBe(false);
  });
});
