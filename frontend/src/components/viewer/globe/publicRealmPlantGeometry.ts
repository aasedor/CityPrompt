import * as THREE from 'three';

/** A reusable planted-room kit: metre-normalized, centred like the previous
 * placeholders, with no textures/network dependencies. Existing placement
 * envelopes and terrain transforms remain authoritative. */
export function createPublicRealmPlant(kind: 'shrub' | 'grass' | 'perennial'): THREE.BufferGeometry {
  const positions: number[] = [], colors: number[] = [];
  const tint = new THREE.Color();
  const triangle = (a: number[], b: number[], c: number[], color: string) => {
    positions.push(...a, ...b, ...c);
    tint.set(color);
    for (let j = 0; j < 3; j++) colors.push(tint.r, tint.g, tint.b);
  };
  const leaf = (x: number, y: number, z: number, angle: number, length: number, width: number, rise: number, color: string) => {
    const dx = Math.cos(angle), dy = Math.sin(angle);
    const a = [x, y, z], b = [x + dx * length, y + dy * length, z + rise];
    const left = [x + dx * length * .5 - dy * width, y + dy * length * .5 + dx * width, z + rise * .65];
    const right = [x + dx * length * .5 + dy * width, y + dy * length * .5 - dx * width, z + rise * .45];
    triangle(a, left, b, color); triangle(a, b, right, color);
  };
  if (kind === 'grass') {
    for (let i = 0; i < 52; i++) {
      const a = i * 2.399963, r = .14 * Math.sqrt((i + .5) / 52);
      const x = Math.cos(a) * r, y = Math.sin(a) * r;
      const height = .45 + (i % 9) * .058;
      const dx = Math.cos(a), dy = Math.sin(a), reach = .2 + (i % 4) * .025;
      const w = .008 + (i % 3) * .003;
      const p = [x, y, -.5], q = [x + dx * reach * .35, y + dy * reach * .35, -.5 + height * .72];
      const tip = [x + dx * reach, y + dy * reach, -.5 + height];
      const color = ['#788452', '#99a06c', '#b0ab78', '#617344'][i % 4];
      triangle(p, [q[0]-dy*w,q[1]+dx*w,q[2]], tip, color);
      triangle(p, tip, [q[0]+dy*w,q[1]-dx*w,q[2]], color);
    }
  } else {
    for (let i = 0; i < 110; i++) {
      const a = i * 2.399963, h = (i % 13) / 13;
      const r = Math.sqrt(1 - Math.pow(h * 1.6 - .65, 2)) * (.14 + (i % 5) * .045);
      const x = Math.cos(a) * r, y = Math.sin(a) * r, z = -.43 + h * .74;
      leaf(x, y, z, a + .4, .09, .03, .045,
        ['#657b48', '#819055', '#4f683e', '#96a267'][i % 4]);
      if (kind === 'perennial' && i % 8 === 0) {
        for (let p = 0; p < 5; p++) leaf(x,y,z+.08,p*Math.PI*2/5,.035,.018,.015,
          i % 16 === 0 ? '#c5b6cf' : '#dace9c');
      }
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geometry.computeVertexNormals(); geometry.computeBoundingBox();
  return geometry;
}
