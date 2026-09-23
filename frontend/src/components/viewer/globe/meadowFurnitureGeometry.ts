import * as THREE from 'three';
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';
import { createPublicRealmPlant } from './publicRealmPlantGeometry';

export type MeadowFurnitureKind = 'bench' | 'picnic_table' | 'bin' | 'light' | 'backless_bench' | 'bike_rack' | 'planter';

/** Metres, Z up, feet at zero. Bounds stay inside the existing placement discs.
 * Merge the coloured parts once; the renderer instances one draw per kind. */
export function createMeadowFurniture(kind: MeadowFurnitureKind): THREE.BufferGeometry {
  const parts: THREE.BufferGeometry[] = [];
  const metal = '#343e3b';
  const timber = ['#95816a', '#a08a70', '#8b7965', '#aa9479'];
  const add = (source: THREE.BufferGeometry, x: number, y: number, z: number, color: string, tilt = 0) => {
    const geometry = source.index ? source.toNonIndexed() : source;
    if (geometry !== source) source.dispose();
    geometry.rotateX(tilt);
    geometry.translate(x, y, z);
    const tint = new THREE.Color(color);
    const colors = new Float32Array(geometry.getAttribute('position').count * 3);
    for (let i = 0; i < colors.length; i += 3) colors.set([tint.r, tint.g, tint.b], i);
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    parts.push(geometry);
  };
  const box = (x: number, y: number, z: number, w: number, d: number, h: number, color = metal, tilt = 0) =>
    add(new THREE.BoxGeometry(w, d, h), x, y, z, color, tilt);
  const cylinder = (z: number, top: number, bottom: number, h: number, color = metal) =>
    add(new THREE.CylinderGeometry(top, bottom, h, 16), 0, 0, z, color, Math.PI / 2);

  if (kind === 'bench') {
    // Slatted seat, gently reclined back, connected side frames and armrests.
    for (let i = 0; i < 5; i++) box(0, -.2 + i * .1, .46, 1.86, .086, .052, timber[i % 4]);
    for (let i = 0; i < 4; i++) box(0, .238 + i * .016, .62 + i * .1, 1.86, .05, .083, timber[(i + 1) % 4], -.16);
    for (const x of [-.68, .68]) {
      for (const y of [-.18, .2]) box(x, y, .22, .055, .055, .44);
      box(x, .242, .68, .045, .052, .55, metal, -.16);
      box(x, 0, .417, .07, .49, .052);
      box(x, 0, .024, .1, .54, .048);
      box(x, -.14, .57, .035, .035, .25);
      box(x, .04, .697, .065, .41, .035);
    }
    box(0, .2, .2, 1.39, .04, .04);
  } else if (kind === 'picnic_table') {
    // 2.2 m top overhangs the recessed frames; no parcel-dependent stretching.
    for (let i = 0; i < 7; i++) box(0, -.36 + i * .12, .755, 2.2, .106, .06, timber[i % 4]);
    for (const side of [-1, 1]) {
      for (let i = 0; i < 3; i++) box(0, side * (.61 + i * .09), .465, 1.9, .077, .055, timber[(i + 1) % 4]);
    }
    for (const x of [-.62, .62]) {
      for (const y of [-.3, .3]) box(x, y, .365, .065, .065, .73);
      box(x, 0, .704, .07, .84, .065);
      box(x, 0, .415, .085, 1.65, .065);
      for (const y of [-.72, .72]) box(x, y, .21, .07, .07, .42);
    }
    box(0, 0, .2, 1.3, .055, .07);
  } else if (kind === 'bin') {
    cylinder(.055, .255, .255, .11);
    cylinder(.46, .225, .225, .78);
    for (let i = 0; i < 18; i++) {
      const a = i * Math.PI / 9;
      const slat = new THREE.BoxGeometry(.061, .025, .69);
      slat.rotateZ(a - Math.PI / 2);
      add(slat, Math.cos(a) * .246, Math.sin(a) * .246, .465, timber[i % 4]);
    }
    // Real open rim, dark recessed liner; small cap protects the timber endgrain.
    add(new THREE.TorusGeometry(.194, .063, 6, 24), 0, 0, .86, metal);
    cylinder(.74, .13, .13, .012, '#1b2320');
  } else if (kind === 'backless_bench') {
    for (let i = 0; i < 6; i++) box(0, -.225 + i * .09, .455, 1.86, .078, .07, timber[i % 4]);
    for (const x of [-.66, .66]) {
      box(x, 0, .392, .075, .53, .065);
      for (const y of [-.18, .18]) box(x, y, .2, .055, .055, .4);
      box(x, 0, .021, .13, .52, .042);
    }
    box(0, 0, .21, 1.38, .045, .055);
  } else if (kind === 'bike_rack') {
    // Three rounded inverted-U stands: clear locking space, no solid wheel slots.
    for (const x of [-.6, 0, .6]) {
      for (const y of [-.32, .32]) {
        const leg = new THREE.CylinderGeometry(.026, .026, .58, 8);
        add(leg, x, y, .3, metal, Math.PI / 2);
        box(x, y, .012, .12, .13, .024);
      }
      const bend = new THREE.TorusGeometry(.32, .026, 6, 16, Math.PI);
      bend.rotateX(Math.PI / 2);
      bend.rotateZ(Math.PI / 2);
      add(bend, x, 0, .59, metal);
    }
  } else if (kind === 'planter') {
    // A real open container with recessed soil and native grasses; no green box.
    for (const x of [-.70, .70]) box(x, 0, .03, .12, .5, .06);
    box(0, 0, .09, 1.56, .56, .08);
    for (const y of [-.274, .274]) {
      for (let i = 0; i < 15; i++) box(-.714 + i * .102, y, .34, .09, .035, .46, timber[i % 4]);
      box(0, y, .585, 1.60, .055, .04);
    }
    for (const x of [-.78, .78]) {
      for (let i = 0; i < 5; i++) box(x, -.204 + i * .102, .34, .035, .09, .46, timber[(i + 1) % 4]);
      box(x, 0, .585, .055, .60, .04);
      for (const y of [-.274, .274]) box(x, y, .32, .045, .045, .53);
    }
    box(0, 0, .55, 1.48, .48, .03, '#49443a');
    for (let i = 0; i < 5; i++) {
      const plant = createPublicRealmPlant('grass');
      const height = .58 + (i % 3) * .055;
      plant.scale(.52, .52, height);
      plant.rotateZ(i * 2.4);
      plant.translate((i - 2) * .29, i % 2 ? .05 : -.04, .565 + height * .5);
      // Keep botanical colours and match the furniture's merge attributes.
      plant.setAttribute('uv', new THREE.Float32BufferAttribute(new Float32Array(plant.getAttribute('position').count * 2), 2));
      parts.push(plant);
    }
  } else {
    cylinder(.055, .13, .13, .11);
    cylinder(1.775, .046, .069, 3.55);
    cylinder(3.52, .16, .12, .12, '#d4d1b8');
    cylinder(3.61, .07, .29, .10);
    cylinder(3.665, .07, .07, .02);
  }
  const result = mergeGeometries(parts)!;
  parts.forEach(part => part.dispose());
  result.computeBoundingBox();
  result.computeBoundingSphere();
  return result;
}
