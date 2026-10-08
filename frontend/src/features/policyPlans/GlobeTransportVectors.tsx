import { useEffect, useLayoutEffect, useMemo } from 'react';
import { useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { LineSegments2 } from 'three/examples/jsm/lines/LineSegments2.js';
import { LineSegmentsGeometry } from 'three/examples/jsm/lines/LineSegmentsGeometry.js';
import { LineMaterial } from 'three/examples/jsm/lines/LineMaterial.js';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { retainResourceForDeferredDisposal } from '@/components/viewer/globe/strictModeResourceDisposal';
import { transportStyle, type TransportCategory, type TransportSnapshot } from './transportVectors';

const NO_HIT = () => {};
export function disposeTransportObjects(objects: Array<LineSegments2 | THREE.InstancedMesh>) {
  objects.forEach(object => {
    object.geometry.dispose();
    (object.material as THREE.Material).dispose();
    // R3F's primitive dispose={null} shadows the instance method; still release
    // renderer-owned instance buffers through Three's disposal event.
    if (object instanceof THREE.InstancedMesh) THREE.InstancedMesh.prototype.dispose.call(object);
  });
}
/** A few batched line draws per network; no per-frame geometry rebuilding. */
export function GlobeTransportVectors({ data, mapId, height, opacity, order }: {
  data: TransportSnapshot; mapId: string; height: number; opacity: number; order: number;
}) {
  const size = useThree(state => state.size);
  const resources = useMemo(() => {
    const origin = WGS84_ELLIPSOID.getCartographicToPosition(51.05 * Math.PI / 180, -114.07 * Math.PI / 180,
      height + 3, new THREE.Vector3());
    const point = (c: number[]) => WGS84_ELLIPSOID.getCartographicToPosition(c[1] * Math.PI / 180,
      c[0] * Math.PI / 180, height + 3, new THREE.Vector3()).sub(origin);
    const categories = new Map<TransportCategory, { positions: number[]; ids: string[]; points: THREE.Vector3[]; pointIds: string[] }>();
    for (const f of data.features) {
      let batch = categories.get(f.properties.category);
      if (!batch) { batch = { positions: [], ids: [], points: [], pointIds: [] }; categories.set(f.properties.category, batch); }
      if (f.geometry.type === 'Point') { batch.points.push(point(f.geometry.coordinates)); batch.pointIds.push(f.id); continue; }
      const lines = f.geometry.type === 'LineString' ? [f.geometry.coordinates] : f.geometry.coordinates;
      for (const line of lines) for (let i = 1; i < line.length; i++) {
        batch.positions.push(...point(line[i - 1]).toArray(), ...point(line[i]).toArray());
        batch.ids.push(f.id);
      }
    }
    const objects: Array<LineSegments2 | THREE.InstancedMesh> = [];
    for (const [category, batch] of categories) {
      const style = transportStyle(category);
      if (batch.positions.length) {
        const geometry = new LineSegmentsGeometry().setPositions(batch.positions);
        const material = new LineMaterial({ color: style.color, linewidth: 4, transparent: true, depthTest: false,
          depthWrite: false, toneMapped: false, dashed: style.dashed, dashSize: 30, gapSize: 20 });
        const object = new LineSegments2(geometry, material);
        object.computeLineDistances();
        object.userData = { cityPolicyId: mapId, transportIds: batch.ids, policyRaycast: object.raycast.bind(object) };
        object.raycast = NO_HIT;
        object.renderOrder = order;
        objects.push(object);
      }
      if (batch.points.length) {
        const material = new THREE.MeshBasicMaterial({ color: style.color, transparent: true, depthTest: false,
          depthWrite: false, toneMapped: false, side: THREE.DoubleSide });
        const object = new THREE.InstancedMesh(new THREE.CircleGeometry(category === 'service-stop' ? 6 : category === 'transit-centre' ? 17 : 28, 20), material, batch.points.length);
        batch.points.forEach((position, index) => {
          const normal = position.clone().add(origin).normalize();
          object.setMatrixAt(index, new THREE.Matrix4().compose(position,
            new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal), new THREE.Vector3(1, 1, 1)));
        });
        object.userData = { cityPolicyId: mapId, transportIds: batch.pointIds, policyRaycast: object.raycast.bind(object) };
        object.raycast = NO_HIT;
        object.renderOrder = order + .5;
        objects.push(object);
      }
    }
    return { origin, objects };
  }, [data, mapId, height, order]);
  useEffect(() => retainResourceForDeferredDisposal(resources, value => disposeTransportObjects(value.objects)), [resources]);
  useLayoutEffect(() => {
    for (const object of resources.objects) {
      (object.material as THREE.Material).opacity = opacity;
      if (object instanceof LineSegments2) object.material.resolution.set(size.width, size.height);
    }
  }, [resources, opacity, size.width, size.height]);
  return <group position={resources.origin} name={`transport-vector:${mapId}`}>
    {resources.objects.map((object, i) => <primitive key={i} object={object} dispose={null} />)}
  </group>;
}
