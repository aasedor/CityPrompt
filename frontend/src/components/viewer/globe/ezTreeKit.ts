/**
 * Runtime-generated EZ-Tree species for the park kit (pilot for the park
 * quality upgrade, 2026-07-11). Replaces the cone+cylinder placeholder tree
 * with three textured procedural species generated once per session.
 *
 * Production path (deferred): bake these to GLBs via the archetype-cache
 * pre-warm pipeline and serve through PARK_KIT_MANIFEST like other props.
 */
import * as THREE from 'three';
import { Tree } from '@dgreenheck/ez-tree';

export interface EzTreePart {
  geometry: THREE.BufferGeometry;
  material: THREE.Material;
}

/** One entry per species; each species is [branches, leaves] parts. */
export type EzTreeKit = EzTreePart[][];

// Calgary-plausible mixed stand. Preset native sizes vary, so each species
// is normalized to an explicit target height (metres).
const SPECIES: Array<{ preset: string; targetHeight: number; seed: number }> = [
  { preset: 'Aspen Medium', targetHeight: 9, seed: 11 },
  { preset: 'Ash Medium', targetHeight: 10, seed: 23 },
  { preset: 'Pine Medium', targetHeight: 12, seed: 37 },
];

let cached: EzTreeKit | null | undefined;

function buildSpecies(preset: string, targetHeight: number, seed: number): EzTreePart[] {
  const tree = new Tree();
  tree.loadPreset(preset);
  (tree.options as { seed?: number }).seed = seed;
  tree.generate();

  const meshes = [tree.branchesMesh, tree.leavesMesh].filter(
    (m): m is THREE.Mesh => Boolean(m && (m as THREE.Mesh).isMesh),
  );
  const leavesMesh = tree.leavesMesh as THREE.Mesh | undefined;

  // Shared normalization: uniform scale to targetHeight, base at y=0 kept at
  // origin, then glTF/three Y-up -> ENU Z-up (same convention as
  // GLBInstancedProp).
  const bbox = new THREE.Box3();
  for (const mesh of meshes) bbox.expandByObject(mesh);
  const height = bbox.max.y - bbox.min.y;
  const scale = height > 0 ? targetHeight / height : 1;
  const center = bbox.getCenter(new THREE.Vector3());
  const norm = new THREE.Matrix4()
    .makeRotationX(Math.PI / 2)
    .multiply(new THREE.Matrix4().makeScale(scale, scale, scale))
    .multiply(new THREE.Matrix4().makeTranslation(-center.x, -bbox.min.y, -center.z));

  return meshes.map((mesh) => {
    const geometry = mesh.geometry.clone();
    geometry.applyMatrix4(norm);
    geometry.computeBoundingSphere();
    const raw = Array.isArray(mesh.material) ? mesh.material[0] : mesh.material;
    // clone() drops EZ-Tree's instance-level onBeforeCompile wind shader —
    // it replaces project_vertex with no USE_INSTANCING guard, which
    // collapses every InstancedMesh leaf to the frame origin (invisible).
    // Static trees don't need wind anyway.
    const material = raw.clone();
    // Render in the transparent pass so renderOrder 145 beats the zone
    // ground washes (renderOrder 120–121, transparent, depthWrite:false).
    // Plan street/ground fills are FLAT planes at the zone's anchor height;
    // over sloping terrain they float above ground and, drawn after the
    // opaque pass, gray-wash any opaque prop behind them. depthWrite stays
    // true so foliage still self-occludes correctly.
    material.transparent = true;
    material.depthWrite = true;
    // Match the premultiplied leaf/bark textures (EZ-Tree uploads them with
    // premultiplyAlpha) so blending doesn't produce dark fringes.
    material.premultipliedAlpha = true;
    if (mesh === leavesMesh) {
      // EZ-Tree ships alphaTest 0.5, tuned for close-up cameras (mip 0).
      // At aerial distance leaf quads sample deep mips where the ~84%
      // transparent atlas dilutes alpha below 0.5 and every fragment is
      // discarded — trees render as bare branches. A low cutoff keeps
      // distant canopies; blending handles the soft edges.
      material.alphaTest = 0.06;
    }
    return { geometry, material };
  });
}

/**
 * Build (once) and return the species kit, or null if generation fails —
 * callers fall back to the placeholder cone tree.
 */
export function getEzTreeKit(): EzTreeKit | null {
  if (cached !== undefined) return cached;
  try {
    cached = SPECIES.map((s) => buildSpecies(s.preset, s.targetHeight, s.seed));
  } catch (err) {
    console.warn('[ezTreeKit] generation failed, using placeholder trees', err);
    cached = null;
  }
  return cached;
}

/**
 * Deterministically partition tree placements into one bucket per species.
 * Uses placement index (placements are seeded per zone, so stable), and
 * returns the index list per bucket so callers can subset per-instance Z.
 */
export function splitBySpecies<T>(items: T[], buckets: number): number[][] {
  const out: number[][] = Array.from({ length: buckets }, () => []);
  items.forEach((_, i) => out[i % buckets].push(i));
  return out;
}
