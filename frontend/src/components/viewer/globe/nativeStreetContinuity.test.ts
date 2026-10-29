import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { nativeStreetPilot } from './nativeStreetPilot';
import { buildNativeStreetProgram } from './nativeStreetProgram';
import { buildSectionJunctionGeometry, clipStreetGeometryOutsideJunction, type StreetJunctionLayout } from './streetJunctionGeometry';

function covers(geometry: THREE.BufferGeometry, x: number, y: number) {
  const material = new THREE.MeshBasicMaterial({ side: THREE.DoubleSide });
  const ray = new THREE.Raycaster(new THREE.Vector3(x, y, 10), new THREE.Vector3(0, 0, -1));
  const hit = ray.intersectObject(new THREE.Mesh(geometry, material)).length > 0;
  material.dispose();
  return hit;
}

describe('native street travel surface continuity', () => {
  const pilot = nativeStreetPilot('student_cycle_avenue_v1')!;

  it.each([240, 253])('keeps the complete native travel widths through source repeats and route ends at %s m', length => {
    for (const reversed of [false, true]) {
      const route = reversed ? [{ x: 0, y: length }, { x: 0, y: 0 }] : [{ x: 0, y: 0 }, { x: 0, y: length }];
      const meshes = buildNativeStreetProgram(pilot.program!, 24, 48, route);
      const ground = (name: string) => meshes.find(item => item.material === name)!.geometry;
      try {
        // Source fixture centres have a 3 m full-ROW link; neither they nor
        // the 48 m module seams may replace the road/cycle travel surface.
        const stations = [.01, 22.6, 24, 25.4, 47.9, 48.1, 72, 96, 120, 144, 168, 192, 216, 239.99, length - .01];
        for (const station of stations) for (const [material, offsets] of [
          ['asphalt', [-.49, 1, 2.6, 5.49]], ['cycle', [-6.49, -5, -3.1, -2.51]],
        ] as const) for (const offset of offsets) {
          const x = reversed ? -offset : offset, y = reversed ? length - station : station;
          expect(covers(ground(material), x, y), `${material} at offset ${offset}, station ${station}, reversed ${reversed}`).toBe(true);
          expect(covers(ground('paving'), x, y)).toBe(false);
        }
        // Retain the real pedestrian link across the planted separator and
        // paving on both sidewalks, without broadening either travel band.
        for (const offset of [-10, -1.5, 10]) expect(covers(ground('paving'), reversed ? -offset : offset, reversed ? length - 24 : 24)).toBe(true);
        expect(covers(ground('asphalt'), reversed ? -5.6 : 5.6, length / 2)).toBe(false);
        expect(covers(ground('asphalt'), reversed ? -2.5 : 2.5, -.01)).toBe(false);
        expect(covers(ground('asphalt'), reversed ? -2.5 : 2.5, length + .01)).toBe(false);
      } finally { meshes.forEach(item => item.geometry.dispose()); }
    }
  });

  it.each([6, 24])('retains an authored %s m local crossing and the source paint details', width => {
    const program = { ...pilot.program!, surfaceRegions: [...pilot.program!.surfaceRegions,
      { x: width === 24 ? 0 : 2.5, y: 8, width, depth: 2, material: 'paving' }],
    };
    const meshes = buildNativeStreetProgram(program, 24, 48, [{ x: 0, y: 0 }, { x: 0, y: 96 }]);
    try {
      expect(covers(meshes.find(item => item.material === 'paving')!.geometry, 2.5, 32)).toBe(true);
      expect(covers(meshes.find(item => item.material === 'asphalt')!.geometry, 2.5, 32)).toBe(false);
      expect(meshes.find(item => item.material === 'paint')!.geometry.getIndex()!.count).toBeGreaterThan(0);
    } finally { meshes.forEach(item => item.geometry.dispose()); }
  });

  it.each([0, 1 / Math.sqrt(3)])('still yields to an explicit junction with real crossings, shear %s', shear => {
    const layout: StreetJunctionLayout = {
      bearing: Math.PI / 2, shear, rowA: 12, rowB: 6.5, roadA: 6.5, roadB: 2.5, sidesB: [-1, 1],
      bounds: [{ minX: -10.5, maxX: 10.5, minY: -12, maxY: 12 }, { minX: -6.5, maxX: 6.5, minY: -16, maxY: 16 }],
      sections: [{ low: -5.5, high: 6.5, raised: false, roadZ: .025, edgeZ: .025 },
        { low: -2.5, high: 2.5, raised: false, roadZ: .025, edgeZ: .025 }],
    };
    const source = buildNativeStreetProgram(pilot.program!, 24, 48, [{ x: 0, y: 0 }, { x: 0, y: 240 }]);
    const trimmed = source.map(item => clipStreetGeometryOutsideJunction(item.geometry, layout, 0, 120));
    const junction = buildSectionJunctionGeometry(layout);
    try {
      expect(trimmed.every(geometry => !covers(geometry, 2.5, 120))).toBe(true);
      expect(covers(trimmed[source.findIndex(item => item.material === 'asphalt')], 2.5, 72)).toBe(true);
      expect(covers(junction.pavement, 2.5, 0)).toBe(true);
      expect(junction.crosswalks.getAttribute('position').count).toBeGreaterThan(0);
    } finally {
      source.forEach(item => item.geometry.dispose());
      trimmed.forEach(geometry => geometry.dispose());
      Object.values(junction).forEach(geometry => geometry.dispose());
    }
  });
});
