import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { computeFootprintFrame } from './buildingPlacement';
import {
  buildModelSelectionOutlinePoints,
  createModelSelectionOutlineLine,
} from './GlobeModelSelectionOutline';
import { isExcludedFromDirect3DCapture } from './direct3dCapture';

describe('buildModelSelectionOutlinePoints', () => {
  it('closes the footprint ring and raises it above the terrain', () => {
    const ring = [[-114, 51], [-113.9999, 51], [-113.9999, 51.0001], [-114, 51.0001]];
    const frame = computeFootprintFrame(ring)!;
    const points = buildModelSelectionOutlinePoints(ring, frame);

    expect(points).toHaveLength(ring.length + 1);
    expect(points[0].equals(points[points.length - 1])).toBe(true);
    expect(points.every((point) => point.z === 0.24)).toBe(true);
  });
});

describe('createModelSelectionOutlineLine', () => {
  it('is excluded from Direct 3D captures even under a role-tagged parent', () => {
    // A selected model's outline mounts under the building group that carries
    // the Direct 3D proposal role. Without the exclusion tag the capture
    // fails closed: "Visible Direct 3D building geometry is missing a stable
    // instance tag."
    const line = createModelSelectionOutlineLine(
      new THREE.BufferGeometry(),
      new THREE.LineBasicMaterial(),
    );

    expect(isExcludedFromDirect3DCapture(line)).toBe(true);
  });
});
