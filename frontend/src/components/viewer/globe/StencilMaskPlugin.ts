/**
 * StencilMaskPlugin.ts — Cuts Google 3D Tile buildings inside zone polygons.
 *
 * When a user draws a building zone, existing Google buildings inside that zone
 * should disappear, creating a clean void for the custom massing to occupy.
 *
 * Approach:
 * 1. For each zone polygon, extrude it into a tall invisible stencil volume
 * 2. Render stencil volumes first (stencilWrite, no color/depth)
 * 3. Patch incoming 3D tile materials to test against stencil buffer
 * 4. Tiles inside stencil volumes get discarded → clean void
 *
 * This is a TilesRenderer plugin that hooks into 'load-model' events.
 */

import * as THREE from 'three';

// Stencil reference value used for zone masking
const STENCIL_REF = 1;

const STENCIL_PATCH_STATE_KEY = '__siteforgeTileStencilPatch';

interface MaterialStencilState {
  stencilWrite: boolean;
  stencilWriteMask: number;
  stencilFunc: THREE.StencilFunc;
  stencilRef: number;
  stencilFuncMask: number;
  stencilFail: THREE.StencilOp;
  stencilZFail: THREE.StencilOp;
  stencilZPass: THREE.StencilOp;
}

export function shouldCreateTileStencilMask(_zoneType: string | null | undefined): boolean {
  return false;
}

export function getTileStencilVolumeHeight(
  _zoneType: string | null | undefined,
  extrudeHeight: number,
): number {
  return Math.max(extrudeHeight * 2, 200);
}

/**
 * Create a stencil volume (invisible extruded column) for a zone polygon.
 * The volume writes to the stencil buffer but doesn't render visually.
 *
 * @param localPts - Array of {x, y} in ENU local meters (X=East, Y=North)
 * @param height - Height of the stencil volume in meters
 */
export function createStencilVolume(
  localPts: { x: number; y: number }[],
  height: number = 500, // Tall enough to cover any building
): THREE.Mesh | null {
  if (localPts.length < 3) return null;

  // Triangulate the 2D polygon
  const indices = THREE.ShapeUtils.triangulateShape(
    localPts.map(p => new THREE.Vector2(p.x, p.y)),
    [],
  );

  const n = localPts.length;
  const verts: number[] = [];
  const idx: number[] = [];

  // Bottom face at Z = -10 (slightly below ground)
  for (const p of localPts) verts.push(p.x, p.y, -10);
  // Top face at Z = height
  for (const p of localPts) verts.push(p.x, p.y, height);

  // Bottom triangles
  for (const tri of indices) idx.push(tri[0], tri[1], tri[2]);
  // Top triangles (reversed)
  for (const tri of indices) idx.push(tri[0] + n, tri[2] + n, tri[1] + n);
  // Side walls
  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n;
    idx.push(i, j, j + n);
    idx.push(i, j + n, i + n);
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
  geo.setIndex(idx);
  geo.computeBoundingSphere();

  // Stencil-write material: invisible, writes stencil ref value
  const material = new THREE.MeshBasicMaterial({
    colorWrite: false,
    depthWrite: false,
    stencilWrite: true,
    stencilRef: STENCIL_REF,
    stencilFunc: THREE.AlwaysStencilFunc,
    stencilZPass: THREE.ReplaceStencilOp,
    stencilZFail: THREE.KeepStencilOp,
    stencilFail: THREE.KeepStencilOp,
    side: THREE.DoubleSide,
  });

  const mesh = new THREE.Mesh(geo, material);
  mesh.renderOrder = -1; // Render before everything else
  mesh.frustumCulled = false;
  mesh.name = 'stencil-volume';
  return mesh;
}

/**
 * Patch a material to respect the stencil buffer.
 * Fragments where stencil === STENCIL_REF will be discarded.
 */
export function patchMaterialForStencil(material: THREE.Material): void {
  if (!material.userData[STENCIL_PATCH_STATE_KEY]) {
    material.userData[STENCIL_PATCH_STATE_KEY] = {
      stencilWrite: material.stencilWrite,
      stencilWriteMask: material.stencilWriteMask,
      stencilFunc: material.stencilFunc,
      stencilRef: material.stencilRef,
      stencilFuncMask: material.stencilFuncMask,
      stencilFail: material.stencilFail,
      stencilZFail: material.stencilZFail,
      stencilZPass: material.stencilZPass,
    } satisfies MaterialStencilState;
  }

  // Three enables the stencil test from stencilWrite. A zero write-mask lets
  // tile materials test against zone masks without changing the stencil buffer.
  material.stencilWrite = true;
  material.stencilWriteMask = 0x00;
  material.stencilRef = STENCIL_REF;
  material.stencilFunc = THREE.NotEqualStencilFunc; // Only render where stencil !== ref
  material.stencilFuncMask = 0xff;
  material.stencilFail = THREE.KeepStencilOp;
  material.stencilZFail = THREE.KeepStencilOp;
  material.stencilZPass = THREE.KeepStencilOp;
  material.needsUpdate = true;
}

/**
 * Remove stencil patching from a material.
 */
export function unpatchMaterialStencil(material: THREE.Material): void {
  const previousState = material.userData[STENCIL_PATCH_STATE_KEY] as MaterialStencilState | undefined;
  if (previousState) {
    material.stencilWrite = previousState.stencilWrite;
    material.stencilWriteMask = previousState.stencilWriteMask;
    material.stencilFunc = previousState.stencilFunc;
    material.stencilRef = previousState.stencilRef;
    material.stencilFuncMask = previousState.stencilFuncMask;
    material.stencilFail = previousState.stencilFail;
    material.stencilZFail = previousState.stencilZFail;
    material.stencilZPass = previousState.stencilZPass;
    delete material.userData[STENCIL_PATCH_STATE_KEY];
  } else {
    material.stencilWrite = false;
  }

  material.needsUpdate = true;
}
