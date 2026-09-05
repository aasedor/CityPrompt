import * as THREE from 'three';

/** A shared metre-scale meadow patch. Layout supplies the planting bed;
 * this mesh supplies grass, broad leaves and small flowers within 1 m. */
export function createMeadowPatch(): THREE.BufferGeometry {
  const positions: number[] = [], colors: number[] = [];
  const color = new THREE.Color();
  type Point = [number, number, number];
  function triangle(a: Point, b: Point, c: Point, tint: string) {
    positions.push(...a, ...b, ...c);
    color.set(tint);
    for (let i = 0; i < 3; i++) colors.push(color.r, color.g, color.b);
  }
  for (let i = 0; i < 18; i++) {
    const angle = i * 2.39996, radius = Math.sqrt((i + .5) / 18) * .76;
    const x = Math.cos(angle) * radius, y = Math.sin(angle) * radius;
    for (let leaf = 0; leaf < 4; leaf++) {
      const a = angle + leaf * 1.7, reach = .13 + (i % 3) * .025;
      const h = .18 + ((i + leaf) % 5) * .055;
      const dx = Math.cos(a), dy = Math.sin(a), w = .018;
      const left: Point = [x - dy * w, y + dx * w, .01];
      const right: Point = [x + dy * w, y - dx * w, .01];
      const midLeft: Point = [x + dx * reach * .45 - dy * w, y + dy * reach * .45 + dx * w, h * .75];
      const midRight: Point = [x + dx * reach * .45 + dy * w, y + dy * reach * .45 - dx * w, h * .75];
      const tip: Point = [x + dx * reach, y + dy * reach, h];
      const tint = ['#667d43', '#718544', '#536c3b'][(i + leaf) % 3];
      triangle(left, right, midRight, tint); triangle(left, midRight, midLeft, tint);
      triangle(midLeft, midRight, tip, tint);
    }
    if (i % 3 !== 0) continue;
    const z = .37 + (i % 5) * .045;
    // Crossed narrow stems keep depth from either camera direction.
    for (const a of [angle, angle + Math.PI / 2]) {
      const dx = Math.cos(a) * .003, dy = Math.sin(a) * .003;
      triangle([x - dx, y - dy, 0], [x + dx, y + dy, 0], [x, y, z], '#627945');
    }
    for (let petal = 0; petal < 5; petal++) {
      const a = petal * Math.PI * 2 / 5, b = a + .75;
      // 50–60 mm blooms, instead of the old 200 mm polygon flowers.
      const r = .025 + (i % 2) * .005;
      const tip: Point = [x + Math.cos(a + .375) * r, y + Math.sin(a + .375) * r, z + .007];
      const left: Point = [x + Math.cos(a) * r * .6, y + Math.sin(a) * r * .6, z];
      const right: Point = [x + Math.cos(b) * r * .6, y + Math.sin(b) * r * .6, z];
      const tint = i % 2 === 0 ? '#dfc758' : '#e5dfc2';
      triangle([x, y, z - .004], left, tip, tint); triangle([x, y, z - .004], tip, right, tint);
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geometry.computeVertexNormals(); geometry.computeBoundingBox();
  return geometry;
}
