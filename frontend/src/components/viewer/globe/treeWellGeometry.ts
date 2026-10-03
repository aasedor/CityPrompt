import * as THREE from 'three';
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';

export const TREE_WELL_STYLES = ['grate', 'planted', 'guarded'] as const;
export type TreeWellStyle = typeof TREE_WELL_STYLES[number];
export const TREE_WELL_SIZE_M = 1.8;
export const TREE_WELL_OPENING_RADIUS_M = 0.36;

/** Metric, Z-up tree surrounds. Soil stays visible through real grate openings.
 * A well's footprint is independent of tree/canopy scale. The owning surface
 * must reserve its complete footprint and seat it at the pavement datum. */
export function createTreeWellGeometry(style: TreeWellStyle): THREE.BufferGeometry {
  const parts: THREE.BufferGeometry[] = [];
  const add = (g: THREE.BufferGeometry, hex: string) => {
    const flat = g.index ? g.toNonIndexed() : g;
    if (flat !== g) g.dispose();
    flat.deleteAttribute('uv');
    const color = new THREE.Color(hex), values: number[] = [];
    for (let i = 0; i < flat.getAttribute('position').count; i++) values.push(color.r, color.g, color.b);
    flat.setAttribute('color', new THREE.Float32BufferAttribute(values, 3));
    parts.push(flat);
  };
  const box = (x: number, y: number, z: number, w: number, d: number, h: number, color: string, yaw = 0) => {
    const g = new THREE.BoxGeometry(w, d, h);
    g.rotateZ(yaw); g.translate(x, y, z); add(g, color);
  };
  const metal = '#414b48', stone = '#aaa28d';
  // Thin surface finish, not a raised planter obstructing the sidewalk.
  box(0, 0, .005, 1.8, 1.8, .01, '#4e3928');
  for (const side of [-1, 1]) {
    box(side * .855, 0, .025, .09, 1.8, .05, stone);
    box(0, side * .855, .025, 1.62, .09, .05, stone);
  }
  if (style === 'grate') {
    for (const r of [.37, .49, .61, .73]) {
      const g = new THREE.RingGeometry(r, r + .022, 48);
      g.translate(0, 0, .028); add(g, metal);
    }
    for (let i = 0; i < 32; i++) {
      const a = i * Math.PI / 16;
      const outer = .807 / Math.max(Math.abs(Math.cos(a)), Math.abs(Math.sin(a)));
      const mid = (outer + TREE_WELL_OPENING_RADIUS_M) / 2;
      box(Math.cos(a) * mid, Math.sin(a) * mid, .022,
        outer - TREE_WELL_OPENING_RADIUS_M, .018, .016, metal, a);
    }
  } else {
    // Low, folded leaves echo the meadow kit, with a clear mulch collar.
    for (let i = 0; i < 16; i++) {
      const a = i * 2.399, r = .53 + (i % 3) * .055;
      const x = Math.cos(a) * r, y = Math.sin(a) * r;
      for (let j = 0; j < 7; j++) {
        const t = a + j * 2.399, dx = Math.cos(t), dy = Math.sin(t), h = .14 + (j % 3) * .045;
        const g = new THREE.BufferGeometry();
        g.setAttribute('position', new THREE.Float32BufferAttribute([
          x-.035*dy,y+.035*dx,.015, x+.035*dy,y-.035*dx,.015,
          x+.15*dx,y+.15*dy,h, x+.25*dx,y+.25*dy,h*.75,
          x+.15*dx,y+.15*dy,h, x+.035*dy,y-.035*dx,.015,
        ], 3));
        g.computeVertexNormals(); add(g, ['#667c4d', '#859266', '#4f6948'][i % 3]);
      }
    }
    if (style === 'guarded') {
      for (const side of [-1, 1]) {
        for (const v of [-.79, -.395, 0, .395, .79]) {
          box(v, side*.79, .26, .025, .025, .47, metal);
          box(side*.79, v, .26, .025, .025, .47, metal);
        }
        for (const z of [.14, .49]) {
          box(0, side*.79, z, 1.61, .032, .03, metal);
          box(side*.79, 0, z, .032, 1.61, .03, metal);
        }
      }
    }
  }
  const result = mergeGeometries(parts)!;
  parts.forEach(g => g.dispose());
  result.computeBoundingBox(); result.computeBoundingSphere();
  return result;
}
