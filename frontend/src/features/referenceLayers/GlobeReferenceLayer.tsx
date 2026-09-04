import { useEffect, useMemo } from 'react';
import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import { DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA } from '@/components/viewer/globe/direct3dCapture';
import { retainResourceForDeferredDisposal } from '@/components/viewer/globe/strictModeResourceDisposal';
import type { ReferenceLayer, ReferencePosition } from './api';
import { referenceGeometryPaths } from './referenceGeometry';

const NO_HIT = () => {};
const RAD = Math.PI / 180;

/** Cartographic outlines, independent of proposal geometry and Google tile masks.
 * Depth testing is disabled deliberately: zoning is an inspectable map overlay,
 * not a terrain/height assertion. Third coordinates remain in the stored data.
 * The whole group is excluded from scene renders and never intercepts drawing.
 */
export function GlobeReferenceLayer({ layers, terrainHeight }: { layers: ReferenceLayer[]; terrainHeight: number }) {
  return <group name="reference-overlays" userData={DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA}>
    {layers.map((layer) => <ReferenceOutline key={layer.id} layer={layer} terrainHeight={terrainHeight} />)}
  </group>;
}

function ReferenceOutline({ layer, terrainHeight }: { layer: ReferenceLayer; terrainHeight: number }) {
  const latitude = (layer.bounds[1] + layer.bounds[3]) * 0.5 * RAD;
  const longitude = (layer.bounds[0] + layer.bounds[2]) * 0.5 * RAD;
  const height = Number.isFinite(terrainHeight) ? terrainHeight + 1 : 1;
  const geometries = useMemo(() => {
    const origin = new THREE.Vector3();
    const east = new THREE.Vector3();
    const north = new THREE.Vector3();
    const up = new THREE.Vector3();
    WGS84_ELLIPSOID.getCartographicToPosition(latitude, longitude, height, origin);
    WGS84_ELLIPSOID.getEastNorthUpAxes(latitude, longitude, east, north, up);
    const world = new THREE.Vector3();
    const local = (position: ReferencePosition): number[] => {
      WGS84_ELLIPSOID.getCartographicToPosition(position[1] * RAD, position[0] * RAD, height, world);
      world.sub(origin);
      return [world.dot(east), world.dot(north), world.dot(up)];
    };
    const lines: number[] = [];
    const points: number[] = [];
    for (const feature of layer.feature_collection.features) {
      const paths = referenceGeometryPaths(feature.geometry);
      for (const path of paths.lines) {
        for (let index = 1; index < path.length; index++) lines.push(...local(path[index - 1]), ...local(path[index]));
      }
      for (const point of paths.points) points.push(...local(point));
    }
    const lineGeometry = new THREE.BufferGeometry();
    lineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(lines, 3));
    const pointGeometry = new THREE.BufferGeometry();
    pointGeometry.setAttribute('position', new THREE.Float32BufferAttribute(points, 3));
    return { lineGeometry, pointGeometry };
  }, [height, latitude, layer.feature_collection, longitude]);
  useEffect(() => retainResourceForDeferredDisposal(geometries, (value) => {
    value.lineGeometry.dispose();
    value.pointGeometry.dispose();
  }), [geometries]);
  return <EastNorthUpFrame lat={latitude} lon={longitude} height={height}>
    <lineSegments geometry={geometries.lineGeometry} raycast={NO_HIT} renderOrder={990} frustumCulled={false}>
      <lineBasicMaterial color={layer.color} opacity={layer.opacity} transparent depthTest={false} depthWrite={false} toneMapped={false} />
    </lineSegments>
    <points geometry={geometries.pointGeometry} raycast={NO_HIT} renderOrder={991} frustumCulled={false}>
      <pointsMaterial color={layer.color} size={7} sizeAttenuation={false} opacity={layer.opacity} transparent depthTest={false} depthWrite={false} toneMapped={false} />
    </points>
  </EastNorthUpFrame>;
}
