import * as THREE from 'three';
import type { LegoMassingColoredMesh } from './legoMassingGeometry';

/**
 * Drawing primitives shared by the facade kits. A kit describes one
 * archetype's facade; these helpers only place coloured quads on a wall.
 * Coordinates are the massing prism's local ENU frame: X east, Y north, Z up.
 */
export interface KitMeshes<Tone extends string> {
  /** Opaque parts. */
  solid: LegoMassingColoredMesh;
  /** Glazing, drawn with its own smoother material. */
  glass: LegoMassingColoredMesh;
  /** Each tone as linear RGB, ready for a vertex colour attribute. */
  linear: Record<Tone, number[]>;
  /** One quad, wound counter-clockwise as seen from its visible side. */
  push(mesh: LegoMassingColoredMesh, tone: Tone, corners: number[][]): void;
}

export function createKitMeshes<Tone extends string>(colors: Record<Tone, string>): KitMeshes<Tone> {
  const solid: LegoMassingColoredMesh = { positions: [], indices: [], colors: [], vertexCount: 0 };
  const glass: LegoMassingColoredMesh = { positions: [], indices: [], colors: [], vertexCount: 0 };
  const linear = Object.fromEntries(Object.entries<string>(colors).map(([key, hex]) => {
    const color = new THREE.Color(hex);
    return [key, [color.r, color.g, color.b]];
  })) as Record<Tone, number[]>;
  const push = (mesh: LegoMassingColoredMesh, tone: Tone, corners: number[][]) => {
    const base = mesh.vertexCount;
    for (const corner of corners) { mesh.positions.push(corner[0], corner[1], corner[2]); mesh.colors.push(...linear[tone]); }
    mesh.indices.push(base, base + 1, base + 2, base, base + 2, base + 3);
    mesh.vertexCount += 4;
  };
  return { solid, glass, linear, push };
}

/** Painter for one wall: u runs along it, v out from it (negative is inside), z up. */
export function kitWall<Tone extends string>(meshes: KitMeshes<Tone>, start: readonly number[], along: readonly number[]) {
  const { solid, push } = meshes;
  // The ring runs counter-clockwise around built fabric, so open air is on the right.
  const normal = [along[1], -along[0]];
  const at = (u: number, v: number, z: number) =>
    [start[0] + along[0] * u + normal[0] * v, start[1] + along[1] * u + normal[1] * v, z];
  /** A vertical quad parallel to the wall. */
  const face = (mesh: LegoMassingColoredMesh, tone: Tone, u0: number, u1: number, z0: number, z1: number, v = 0) => {
    if (u1 - u0 > 1e-6 && z1 - z0 > 1e-6) push(mesh, tone, [at(u0, v, z0), at(u1, v, z0), at(u1, v, z1), at(u0, v, z1)]);
  };
  /** A horizontal quad, facing up or down. */
  const flat = (tone: Tone, u0: number, u1: number, v0: number, v1: number, z: number, up: boolean) =>
    push(solid, tone, up ? [at(u0, v0, z), at(u1, v0, z), at(u1, v1, z), at(u0, v1, z)]
      : [at(u0, v1, z), at(u1, v1, z), at(u1, v0, z), at(u0, v0, z)]);
  /** A vertical quad across the wall, facing either end. */
  const cheek = (tone: Tone, u: number, v0: number, v1: number, z0: number, z1: number, towardsEnd: boolean) =>
    push(solid, tone, towardsEnd ? [at(u, v0, z0), at(u, v1, z0), at(u, v1, z1), at(u, v0, z1)]
      : [at(u, v1, z0), at(u, v0, z0), at(u, v0, z1), at(u, v1, z1)]);
  /** A box standing off the wall: front, both ends, top and underside. */
  const box = (tone: Tone, u0: number, u1: number, v0: number, v1: number, z0: number, z1: number) => {
    face(solid, tone, u0, u1, z0, z1, v1);
    cheek(tone, u0, v0, v1, z0, z1, false); cheek(tone, u1, v0, v1, z0, z1, true);
    flat(tone, u0, u1, v0, v1, z1, true); flat(tone, u0, u1, v0, v1, z0, false);
  };
  return { at, face, flat, cheek, box };
}
