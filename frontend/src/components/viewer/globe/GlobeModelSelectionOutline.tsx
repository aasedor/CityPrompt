import { useEffect, useMemo } from 'react';
import * as THREE from 'three';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import type { FootprintFrame } from './buildingPlacement';
import { DIRECT_3D_CAPTURE_EXCLUDE_KEY } from './direct3dCapture';

const DEG_TO_RAD = Math.PI / 180;
const METRES_PER_DEG_LAT = 111_320;

export function buildModelSelectionOutlinePoints(
  ring: number[][],
  frame: FootprintFrame,
): THREE.Vector3[] {
  const metresPerDegreeLongitude = METRES_PER_DEG_LAT * Math.cos(frame.centroidLat * DEG_TO_RAD);
  const points = ring.map(([longitude, latitude]) => new THREE.Vector3(
    (longitude - frame.centroidLng) * metresPerDegreeLongitude,
    (latitude - frame.centroidLat) * METRES_PER_DEG_LAT,
    0.24,
  ));
  if (points.length > 0) points.push(points[0].clone());
  return points;
}

export function createModelSelectionOutlineLine(
  geometry: THREE.BufferGeometry,
  material: THREE.LineBasicMaterial,
): THREE.Line {
  const line = new THREE.Line(geometry, material);
  line.renderOrder = 1000;
  // Editor chrome: the outline mounts under role-tagged building groups, so
  // without this tag the Direct 3D capture classifies it as untagged proposal
  // geometry and fails closed ("missing a stable instance tag") whenever a
  // model is selected at render time.
  line.userData[DIRECT_3D_CAPTURE_EXCLUDE_KEY] = true;
  return line;
}

export function GlobeModelSelectionOutline({
  ring,
  frame,
  terrainHeight,
}: {
  ring: number[][];
  frame: FootprintFrame;
  terrainHeight: number;
}) {
  return (
    <EastNorthUpFrame
      lat={frame.centroidLat * DEG_TO_RAD}
      lon={frame.centroidLng * DEG_TO_RAD}
      height={terrainHeight}
    >
      <LocalModelSelectionOutline ring={ring} frame={frame} />
    </EastNorthUpFrame>
  );
}

export function LocalModelSelectionOutline({
  ring,
  frame,
}: {
  ring: number[][];
  frame: FootprintFrame;
}) {
  const geometry = useMemo(
    () => new THREE.BufferGeometry().setFromPoints(buildModelSelectionOutlinePoints(ring, frame)),
    [frame, ring],
  );
  const material = useMemo(() => new THREE.LineBasicMaterial({
    color: '#b7ff3c',
    depthTest: false,
    depthWrite: false,
  }), []);
  const outline = useMemo(
    () => createModelSelectionOutlineLine(geometry, material),
    [geometry, material],
  );
  useEffect(() => () => geometry.dispose(), [geometry]);
  useEffect(() => () => material.dispose(), [material]);

  return <primitive object={outline} />;
}
