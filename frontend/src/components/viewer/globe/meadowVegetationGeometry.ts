import * as THREE from 'three';

export const MEADOW_VEGETATION_SPECS = {
  shade_tree: { label: 'Spreading shade tree', radiusM: 3.8, maxHeightM: 8.5, maxTriangles: 14000 },
  grove_tree: { label: 'Pale-bark grove tree', radiusM: 2.2, maxHeightM: 9, maxTriangles: 14000 },
  ornamental_tree: { label: 'Multi-stem ornamental', radiusM: 2.9, maxHeightM: 6, maxTriangles: 14000 },
  silver_shrub: { label: 'Silver-green shrub', radiusM: .85, maxHeightM: 1.6, maxTriangles: 4000 },
  meadow_grass: { label: 'Meadow grass', radiusM: .65, maxHeightM: 1.4, maxTriangles: 4000 },
  flowering_perennial: { label: 'Flowering perennial', radiusM: .65, maxHeightM: 1.2, maxTriangles: 4000 },
} as const;
export type MeadowVegetationKind = keyof typeof MEADOW_VEGETATION_SPECS;

type Point = [number, number, number];

/** Actual metre-scale, Z-up prototypes with visible branch structure. No crown
 * solids, alpha textures or network resources. Seed selects a reusable prototype;
 * instances can vary yaw without rebuilding geometry. */
export function createMeadowVegetation(kind: MeadowVegetationKind, seed = 17) {
  let state = seed >>> 0;
  const random = () => {
    state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
    return state / 4294967296;
  };
  const woodPositions: number[] = [], woodColors: number[] = [];
  const leafPositions: number[] = [], leafColors: number[] = [];
  const color = new THREE.Color();
  const triangle = (positions: number[], colors: number[], a: Point, b: Point, c: Point, tint: string) => {
    positions.push(...a, ...b, ...c);
    color.set(tint);
    for (let j = 0; j < 3; j++) colors.push(color.r, color.g, color.b);
  };
  const mix = (a: Point, b: Point, t: number): Point => a.map((v, i) => v + (b[i] - v) * t) as Point;
  const stem = (a: Point, b: Point, base: number, tip: number, tint: string, sides = 5) => {
    const axis = new THREE.Vector3(...b).sub(new THREE.Vector3(...a)).normalize();
    const u = new THREE.Vector3(0, 0, 1);
    if (Math.abs(axis.z) > .95) u.set(1, 0, 0);
    u.cross(axis).normalize();
    const v = axis.clone().cross(u).normalize();
    const ring = (p: Point, r: number, angle: number): Point => [
      p[0] + r * (u.x * Math.cos(angle) + v.x * Math.sin(angle)),
      p[1] + r * (u.y * Math.cos(angle) + v.y * Math.sin(angle)),
      p[2] + r * (u.z * Math.cos(angle) + v.z * Math.sin(angle)),
    ];
    for (let i = 0; i < sides; i++) {
      const a0 = i * Math.PI * 2 / sides, a1 = (i + 1) * Math.PI * 2 / sides;
      const p = ring(a, base, a0), q = ring(a, base, a1), r = ring(b, tip, a1), s = ring(b, tip, a0);
      triangle(woodPositions, woodColors, p, q, r, tint);
      triangle(woodPositions, woodColors, p, r, s, tint);
      triangle(woodPositions, woodColors, b, s, r, tint);
    }
  };
  const leaf = (p: Point, angle: number, length: number, width: number, lift: number, tint: string) => {
    const dx = Math.cos(angle), dy = Math.sin(angle);
    const tip: Point = [p[0] + dx * length, p[1] + dy * length, p[2] + lift];
    const l: Point = [p[0] + dx * length * .48 - dy * width, p[1] + dy * length * .48 + dx * width, p[2] + lift * .6 + width * .25];
    const r: Point = [p[0] + dx * length * .48 + dy * width, p[1] + dy * length * .48 - dx * width, p[2] + lift * .6 - width * .25];
    triangle(leafPositions, leafColors, p, l, tip, tint);
    triangle(leafPositions, leafColors, p, tip, r, tint);
  };
  const greens = kind === 'silver_shrub'
    ? ['#879484', '#a6b09b', '#71846e', '#94a18d']
    : ['#657951', '#829368', '#506945', '#94a176', '#718758'];
  const bark = kind === 'grove_tree' ? '#bab9a8' : '#766d5b';

  const spray = (base: Point, radius: number, height: number, twigCount: number, leafSize: number, silver = false) => {
    for (let j = 0; j < twigCount; j++) {
      const angle = j * 2.399963 + random() * .5;
      const distance = radius * (.4 + random() * .6);
      const tip: Point = [base[0] + Math.cos(angle) * distance, base[1] + Math.sin(angle) * distance, base[2] + height * (.1 + random() * .9)];
      stem(base, tip, .009, .002, bark, 4);
      for (let n = 1; n <= 6; n++) {
        const p = mix(base, tip, n / 7);
        for (const side of [-1, 1]) {
          const a = angle + side * (.7 + random() * .8);
          leaf(p, a, leafSize * (.75 + random() * .5), leafSize * (silver ? .12 : .3), (random() - .2) * leafSize, greens[(j + n) % greens.length]);
        }
      }
    }
  };

  if (kind.endsWith('_tree')) {
    const grove = kind === 'grove_tree', multi = kind === 'ornamental_tree';
    const height = grove ? 7.4 : multi ? 4.25 : 6.4;
    const trunks = multi ? 3 : 1;
    for (let t = 0; t < trunks; t++) {
      const angle = t * Math.PI * 2 / trunks + .4;
      const lean = multi ? .8 : grove ? .18 : .34;
      const trunk = (z: number): Point => [Math.cos(angle) * lean * Math.pow(z / height, 1.3), Math.sin(angle) * lean * z / height, z];
      for (let i = 0; i < 7; i++) {
        const a = trunk(height * i / 7), b = trunk(height * (i + 1) / 7);
        stem(a, b, (multi ? .082 : grove ? .115 : .2) * (1 - i / 8), (multi ? .082 : grove ? .115 : .2) * (1 - (i + 1) / 8), bark, 7);
        if (grove && i > 0) {
          const scar = mix(a, b, .43);
          stem([scar[0] - .04, scar[1] - .075, scar[2]], [scar[0] + .045, scar[1] - .075, scar[2] + .025], .015, .007, '#666d60', 4);
        }
      }
      const branchCount = multi ? 8 : 23;
      for (let i = 0; i < branchCount; i++) {
        const f = i / branchCount;
        const z = height * (grove || multi ? .34 + .61 * f : .30 + .5 * f);
        const a = trunk(z);
        const direction = i * 2.399963 + t * 1.7 + random() * .35;
        const reach = (grove ? 1.02 : multi ? 1.22 : 2.12) * Math.sin((.18 + .75 * f) * Math.PI) * (.8 + random() * .2);
        const tipZ = grove || multi ? z + (grove ? .55 : .42) : height * (.76 + .26 * f) + random() * .24;
        const b: Point = [a[0] + Math.cos(direction) * reach * .56, a[1] + Math.sin(direction) * reach * .56, z + (tipZ - z) * .55];
        const c: Point = [a[0] + Math.cos(direction) * reach, a[1] + Math.sin(direction) * reach, tipZ];
        stem(a, b, multi ? .036 : grove ? .045 : .065, .023, bark);
        stem(b, c, .023, .008, bark);
        // Several attached leafy sprays per limb create gaps and an irregular
        // silhouette without isolated balls or a single opaque crown shell.
        for (let s = 0; s < 2; s++) {
          const start = mix(b, c, .4 + s * .6);
          spray(start, grove ? .45 : multi ? .6 : .78, grove ? .68 : .6, 6, grove ? .14 : .21);
        }
      }
      spray(trunk(height), grove ? .32 : .52, .45, 12, .16);
    }
  } else if (kind === 'silver_shrub') {
    for (let i = 0; i < 12; i++) {
      const a = i * 2.399963;
      const tip: Point = [Math.cos(a) * .36, Math.sin(a) * .36, .42 + random() * .32];
      stem([0, 0, .012], tip, .018, .004, '#817c68');
      spray(tip, .24, .32, 7, .12, true);
    }
  } else if (kind === 'meadow_grass') {
    for (let i = 0; i < 100; i++) {
      const a = i * 2.399963, r = .16 * Math.sqrt(random());
      const base: Point = [Math.cos(a) * r, Math.sin(a) * r, 0];
      const height = .4 + random() * .57, reach = .22 + random() * .18;
      const middle: Point = [base[0] + Math.cos(a) * reach * .32, base[1] + Math.sin(a) * reach * .32, height * .77];
      const tip: Point = [base[0] + Math.cos(a) * reach, base[1] + Math.sin(a) * reach, height];
      const edge = (p: Point, width: number): Point => [p[0] - Math.sin(a) * width, p[1] + Math.cos(a) * width, p[2]];
      const left = edge(base, .009), right = edge(base, -.009);
      const midLeft = edge(middle, .007), midRight = edge(middle, -.007);
      // Follow the curved centreline with a narrow ribbon. A single triangle
      // across this bend makes an unintended broad, spear-shaped leaf.
      triangle(leafPositions, leafColors, left, right, midRight, greens[i % greens.length]);
      triangle(leafPositions, leafColors, left, midRight, midLeft, greens[i % greens.length]);
      triangle(leafPositions, leafColors, midLeft, midRight, tip, greens[i % greens.length]);
      if (i % 7 === 0) {
        const head: Point = [base[0] + Math.cos(a) * .12, base[1] + Math.sin(a) * .12, height + .18];
        stem(base, head, .004, .002, '#969575', 3);
        for (let n = 0; n < 5; n++) leaf([head[0], head[1], head[2] - n * .023], a + n * 2.4, .065, .012, .05, '#b0a484');
      }
    }
  } else {
    for (let i = 0; i < 27; i++) {
      const a = i * 2.399963, r = .36 * Math.sqrt(random());
      const tip: Point = [Math.cos(a) * r, Math.sin(a) * r, .35 + random() * .4];
      const base: Point = [tip[0] * .4, tip[1] * .4, .008];
      stem(base, tip, .007, .002, '#6d7955', 4);
      for (let n = 1; n < 5; n++) leaf(mix(base, tip, n / 5), a + n * 2.4, .16, .035, .07, greens[n]);
      for (let p = 0; p < 7; p++) leaf(tip, p * Math.PI * 2 / 7, .07, .025, .018, i % 4 ? '#b0a0b9' : '#dacfae');
      stem(tip, [tip[0], tip[1], tip[2] + .025], .022, .018, '#ad9461', 6);
    }
  }
  const geometry = (positions: number[], colors: number[]) => {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    g.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    g.computeVertexNormals(); g.computeBoundingBox(); g.computeBoundingSphere();
    return g;
  };
  return { wood: geometry(woodPositions, woodColors), foliage: geometry(leafPositions, leafColors) };
}
