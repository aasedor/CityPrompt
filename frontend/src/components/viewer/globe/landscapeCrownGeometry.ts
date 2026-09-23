import * as THREE from 'three';
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';

/** A sparse branching crown with small matte leaf clusters, not photographs
 * stretched over solid lobes. Generated once and instanced for the whole stand. */
export function createLandscapeCrownGeometry(): {
  foliage: THREE.BufferGeometry; branches: THREE.BufferGeometry;
} {
  const leaves: THREE.BufferGeometry[] = [];
  const branches: THREE.BufferGeometry[] = [];
  let seed = 731;
  const random = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
  const branch = (start: THREE.Vector3, end: THREE.Vector3, radius: number) => {
    const direction = end.clone().sub(start);
    const geometry = new THREE.CylinderGeometry(radius * 0.35, radius, direction.length(), 5, 1, true);
    geometry.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction.normalize()));
    geometry.translate(...start.clone().add(end).multiplyScalar(0.5).toArray());
    branches.push(geometry);
  };
  for (let limb = 0; limb < 9; limb += 1) {
    const angle = limb * 2.39996;
    const height = -0.12 + limb * 0.055;
    const radius = limb === 8 ? 0.04 : 0.30 - limb * 0.013;
    const tip = new THREE.Vector3(Math.cos(angle) * radius, Math.sin(angle) * radius, height);
    const fork = tip.clone().multiplyScalar(0.55); fork.z -= 0.14;
    branch(new THREE.Vector3(0, 0, -0.40 + limb * 0.035), fork, 0.014);
    branch(fork, tip, 0.008);
    for (let leaf = 0; leaf < 64; leaf += 1) {
      const azimuth = random() * Math.PI * 2;
      const z = random() * 2 - 1;
      const radius = Math.cbrt(random());
      const radial = Math.sqrt(1 - z * z);
      const center = tip.clone().add(new THREE.Vector3(
        Math.cos(azimuth) * radial * radius * 0.19,
        Math.sin(azimuth) * radial * radius * 0.19,
        z * radius * 0.18,
      ));
      const size = 0.055 + random() * 0.035;
      // Six-point folded leaf tuft: four triangles, no alpha overdraw or atlas.
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.Float32BufferAttribute([
        -0.5, 0, 0, -0.24, -0.34, 0, 0.28, -0.28, 0,
        0.5, 0, 0, 0.24, 0.34, 0, -0.28, 0.28, 0.12,
      ], 3));
      geometry.setIndex([0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5]);
      geometry.scale(size, size, size);
      geometry.rotateX(random() * Math.PI);
      geometry.rotateY(random() * Math.PI);
      geometry.rotateZ(random() * Math.PI * 2);
      geometry.translate(...center.toArray());
      const color = new THREE.Color().setHSL(0.25 + random() * 0.03, 0.18 + random() * 0.06, 0.33 + random() * 0.12).convertSRGBToLinear();
      geometry.setAttribute('color', new THREE.Float32BufferAttribute(Array.from({ length: 6 }, () => color.toArray()).flat(), 3));
      leaves.push(geometry);
    }
  }
  const foliage = mergeGeometries(leaves)!;
  const wood = mergeGeometries(branches)!;
  [...leaves, ...branches].forEach(geometry => geometry.dispose());
  foliage.computeBoundingBox();
  const center = foliage.boundingBox!.getCenter(new THREE.Vector3());
  const size = foliage.boundingBox!.getSize(new THREE.Vector3());
  for (const geometry of [foliage, wood]) {
    geometry.translate(-center.x, -center.y, -center.z);
    geometry.scale(1 / size.x, 1 / size.y, 1 / size.z);
    geometry.computeVertexNormals();
    geometry.computeBoundingBox();
    geometry.computeBoundingSphere();
  }
  return { foliage, branches: wood };
}

/** Stable across reload and placement-array reordering; restrained greens. */
export function landscapeTreeTint(x: number, y: number): THREE.Color {
  const seed = Math.sin(Math.round(x * 100) * 12.9898 + Math.round(y * 100) * 78.233) * 43758.5453;
  const variation = seed - Math.floor(seed);
  return new THREE.Color().setHSL(0.24 + variation * 0.035, 0.12, 0.90 + variation * 0.08);
}
