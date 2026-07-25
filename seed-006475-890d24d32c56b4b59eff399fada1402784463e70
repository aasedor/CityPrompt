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

export type EzTreeStyle = 'temperate' | 'riparian' | 'ornamental' | 'formal' | 'woodland' | 'botanical';

interface SpeciesDefinition {
  preset: string;
  targetHeight: number;
  seed: number;
}

// Style-specific stands keep the live Google scene legible before the final
// AI finishing pass. EZ-Tree has a compact preset library, so these are shape
// families rather than literal botanical claims.
const SPECIES_BY_STYLE: Record<EzTreeStyle, SpeciesDefinition[]> = {
  temperate: [
    { preset: 'Aspen Medium', targetHeight: 9, seed: 11 },
    { preset: 'Ash Medium', targetHeight: 10, seed: 23 },
    { preset: 'Pine Medium', targetHeight: 12, seed: 37 },
  ],
  // A restrained deciduous water-edge family blends with surrounding Google
  // photogrammetry more naturally than the default mixed conifer stand.
  riparian: [
    { preset: 'Aspen Medium', targetHeight: 9.5, seed: 109 },
    { preset: 'Ash Medium', targetHeight: 10.5, seed: 113 },
    { preset: 'Aspen Small', targetHeight: 7.5, seed: 127 },
  ],
  ornamental: [
    { preset: 'Pine Small', targetHeight: 7, seed: 43 },
    { preset: 'Aspen Small', targetHeight: 6, seed: 47 },
    { preset: 'Oak Small', targetHeight: 7.5, seed: 53 },
    { preset: 'Bush 2', targetHeight: 3.5, seed: 59 },
  ],
  formal: [
    { preset: 'Ash Medium', targetHeight: 10, seed: 61 },
    { preset: 'Oak Medium', targetHeight: 11, seed: 67 },
  ],
  woodland: [
    { preset: 'Oak Large', targetHeight: 15, seed: 71 },
    { preset: 'Pine Large', targetHeight: 17, seed: 73 },
    { preset: 'Aspen Large', targetHeight: 14, seed: 79 },
    { preset: 'Ash Large', targetHeight: 15, seed: 83 },
  ],
  botanical: [
    { preset: 'Oak Medium', targetHeight: 11, seed: 89 },
    { preset: 'Aspen Medium', targetHeight: 9, seed: 97 },
    { preset: 'Pine Medium', targetHeight: 12, seed: 101 },
    { preset: 'Ash Small', targetHeight: 7, seed: 103 },
    { preset: 'Bush 1', targetHeight: 3, seed: 107 },
  ],
};

const cached = new Map<EzTreeStyle, EzTreeKit | null>();

export function resolveEzTreeStyle(
  archetypeId: string | undefined,
  plantingStructure: string | undefined,
): EzTreeStyle {
  const id = String(archetypeId ?? '').toLowerCase();
  if (
    id.includes('reservoir')
    || id.includes('watershed')
    || id.includes('wetland')
    || plantingStructure === 'reservoir_perimeter'
  ) {
    return 'riparian';
  }
  if (id.includes('japanese') || id.includes('zen') || id.includes('contemplative')) {
    return 'ornamental';
  }
  if (id.includes('botanical') || id.includes('garden') || id.includes('arboretum')) {
    return 'botanical';
  }
  if (
    id.includes('forest')
    || id.includes('woodland')
    || id.includes('regional_park')
    || id.includes('olmsted')
    || plantingStructure === 'naturalistic_grove'
  ) {
    return 'woodland';
  }
  if (
    plantingStructure === 'formal_allee'
    || plantingStructure === 'formal_quad'
    || plantingStructure === 'paved_plaza'
  ) {
    return 'formal';
  }
  return 'temperate';
}

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
      material.alphaTest = 0;
      material.side = THREE.DoubleSide;
      // Deep mip levels average the mostly transparent atlas until deciduous
      // crowns disappear. Preserve the detailed source alpha at aerial scale;
      // linear filtering keeps it stable without the skeletal-tree failure.
      if ('map' in material && material.map instanceof THREE.Texture) {
        material.map.generateMipmaps = false;
        material.map.minFilter = THREE.LinearFilter;
        material.map.magFilter = THREE.LinearFilter;
        material.map.needsUpdate = true;
      }
    }
    return { geometry, material };
  });
}

/**
 * Build (once) and return the species kit, or null if generation fails —
 * callers fall back to the placeholder cone tree.
 */
export function getEzTreeKit(style: EzTreeStyle = 'temperate'): EzTreeKit | null {
  if (cached.has(style)) return cached.get(style) ?? null;
  try {
    const kit = SPECIES_BY_STYLE[style].map((species) => (
      buildSpecies(species.preset, species.targetHeight, species.seed)
    ));
    cached.set(style, kit);
    return kit;
  } catch (err) {
    console.warn('[ezTreeKit] generation failed, using placeholder trees', err);
    cached.set(style, null);
    return null;
  }
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
