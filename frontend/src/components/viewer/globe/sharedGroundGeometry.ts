import * as THREE from 'three';
import type { SharedSiteGroundSnapshot } from './sharedSiteGround';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

export interface SharedGroundTriangulation {
  westX: number; southY: number; stepX: number; stepY: number; columns: number; rows: number;
}

/** Transform the snapshot's actual triangle boundaries into the mesh's frame. */
export function createSharedGroundTriangulation(
  snapshot: Pick<SharedSiteGroundSnapshot, 'grid'>, frameLng: number, frameLat: number, originX = 0, originY = 0,
): SharedGroundTriangulation {
  const grid = snapshot.grid, east = metersPerDegLon(frameLat);
  return { westX: (grid.west - frameLng) * east - originX,
    southY: (grid.south - frameLat) * METERS_PER_DEG_LAT - originY,
    stepX: grid.stepLng * east, stepY: grid.stepLat * METERS_PER_DEG_LAT,
    columns: grid.columns, rows: grid.rows };
}

type AttributeVertex = number[][];

/** Clip a convex authored face by a vertical plane. Attribute interpolation
 * retains original construction Z, UVs and any material/colour seams. */
function clipFace(vertices: AttributeVertex[], positionIndex: number, signedDistance: (point: number[]) => number): AttributeVertex[] {
  if (!vertices.length) return [];
  const result: AttributeVertex[] = [];
  for (let index = 0; index < vertices.length; index += 1) {
    const a = vertices[index], b = vertices[(index + 1) % vertices.length];
    const da = signedDistance(a[positionIndex]), db = signedDistance(b[positionIndex]);
    const insideA = da >= -1e-9, insideB = db >= -1e-9;
    if (insideA) result.push(a);
    if (insideA !== insideB) {
      const t = Math.max(0, Math.min(1, da / (da - db)));
      result.push(a.map((values, attribute) => values.map((value, component) => value + (b[attribute][component] - value) * t)));
    }
  }
  return result;
}

/** A second arbitrary mesh triangulation does not describe the same surface
 * between its sampled vertices. Intersect every authored face with the real
 * grid triangles instead. Each resulting face lies in ONE terrain plane, so
 * its interpolated interior has exactly the same ground as heightAt. */
function drapeGridGeometry(
  source: THREE.BufferGeometry, offsetAt: (x: number, y: number) => number | null,
  maxVertices: number, grid: SharedGroundTriangulation,
): THREE.BufferGeometry | null {
  if (!Object.values(grid).every(Number.isFinite) || grid.stepX <= 0 || grid.stepY <= 0
    || !Number.isInteger(grid.columns) || !Number.isInteger(grid.rows) || grid.columns < 2 || grid.rows < 2) return null;
  const attributes = Object.entries(source.attributes), positionIndex = attributes.findIndex(([name]) => name === 'position');
  if (positionIndex < 0) return null;
  const position = attributes[positionIndex][1];
  if (position.count > maxVertices || attributes.some(([, attribute]) => attribute.itemSize > 4 || attribute.count !== position.count)) return null;
  const input: AttributeVertex[] = Array.from({ length: position.count }, (_, index) => attributes.map(([, attribute]) =>
    Array.from({ length: attribute.itemSize }, (_, component) => [attribute.getX, attribute.getY, attribute.getZ, attribute.getW][component].call(attribute, index))));
  const sourceIndices = source.index ? Array.from(source.index.array) : Array.from({ length: position.count }, (_, index) => index);
  if (sourceIndices.length % 3) return null;
  const east = grid.westX + grid.stepX * (grid.columns - 1), north = grid.southY + grid.stepY * (grid.rows - 1);
  // Clipping must not silently remove an unsupported part of the proposal.
  if (input.some((vertex) => {
    const [x, y] = vertex[positionIndex];
    return !Number.isFinite(x) || !Number.isFinite(y) || x < grid.westX - 1e-5 || x > east + 1e-5
      || y < grid.southY - 1e-5 || y > north + 1e-5;
  })) return null;
  const output: AttributeVertex[] = [], indices: number[] = [], materials: number[] = [], cache = new Map<string, number>();
  let visitedCells = 0;
  const append = (vertex: AttributeVertex): number | null => {
    const key = vertex.map((values) => values.map((value) => value.toFixed(8)).join(',')).join(';');
    const previous = cache.get(key); if (previous !== undefined) return previous;
    if (output.length >= maxVertices) return null;
    const cloned = vertex.map((values) => [...values]), point = cloned[positionIndex];
    const offset = offsetAt(point[0], point[1]);
    if (offset === null || !Number.isFinite(offset)) return null;
    point[2] += offset;
    const index = output.length; output.push(cloned); cache.set(key, index); return index;
  };
  for (let start = 0; start < sourceIndices.length; start += 3) {
    const face = sourceIndices.slice(start, start + 3).map((index) => input[index]);
    if (face.some((vertex) => !vertex)) return null;
    const xs = face.map((vertex) => vertex[positionIndex][0]), ys = face.map((vertex) => vertex[positionIndex][1]);
    const minColumn = Math.min(grid.columns - 2, Math.max(0, Math.floor((Math.min(...xs) - grid.westX) / grid.stepX)));
    const maxColumn = Math.min(grid.columns - 2, Math.floor((Math.max(...xs) - grid.westX) / grid.stepX));
    const minRow = Math.min(grid.rows - 2, Math.max(0, Math.floor((Math.min(...ys) - grid.southY) / grid.stepY)));
    const maxRow = Math.min(grid.rows - 2, Math.floor((Math.max(...ys) - grid.southY) / grid.stepY));
    const material = source.groups.find((group) => start >= group.start && start < group.start + group.count)?.materialIndex ?? 0;
    for (let row = minRow; row <= maxRow; row += 1) for (let column = minColumn; column <= maxColumn; column += 1) {
      if (++visitedCells > maxVertices * 8) return null;
      const west = grid.westX + column * grid.stepX, south = grid.southY + row * grid.stepY;
      let polygon = clipFace(face, positionIndex, ([x]) => x - west);
      polygon = clipFace(polygon, positionIndex, ([x]) => west + grid.stepX - x);
      polygon = clipFace(polygon, positionIndex, ([, y]) => y - south);
      polygon = clipFace(polygon, positionIndex, ([, y]) => south + grid.stepY - y);
      if (polygon.length < 3) continue;
      const diagonal = ([x, y]: number[]) => (x - west) / grid.stepX - (y - south) / grid.stepY;
      // A vertical face on the diagonal belongs to one side, not both.
      const halves = polygon.every((vertex) => Math.abs(diagonal(vertex[positionIndex])) <= 1e-9)
        ? [polygon] : [clipFace(polygon, positionIndex, diagonal), clipFace(polygon, positionIndex, (point) => -diagonal(point))];
      for (const half of halves) for (let corner = 1; corner < half.length - 1; corner += 1) {
        const triangle = [half[0], half[corner], half[corner + 1]], [a, b, c] = triangle.map((vertex) => vertex[positionIndex]);
        const ab = new THREE.Vector3(b[0] - a[0], b[1] - a[1], b[2] - a[2]);
        const ac = new THREE.Vector3(c[0] - a[0], c[1] - a[1], c[2] - a[2]);
        if (ab.cross(ac).lengthSq() < 1e-16) continue;
        const ids = triangle.map(append);
        if (ids.some((index) => index === null)) return null;
        indices.push(...ids as number[]); materials.push(material);
      }
    }
  }
  const geometry = source.clone();
  attributes.forEach(([name, attribute], index) => geometry.setAttribute(name,
    new THREE.Float32BufferAttribute(output.flatMap((vertex) => vertex[index]), attribute.itemSize)));
  geometry.setIndex(indices); geometry.clearGroups();
  if (source.groups.length && materials.length) {
    let start = 0;
    for (let index = 1; index <= materials.length; index += 1) {
      if (index === materials.length || materials[index] !== materials[start]) {
        geometry.addGroup(start * 3, (index - start) * 3, materials[start]); start = index;
      }
    }
  }
  geometry.computeVertexNormals(); geometry.computeBoundingBox(); geometry.computeBoundingSphere();
  return geometry;
}

/** Conforming edge subdivision preserves material UVs, winding and construction
 * lifts. Sampling only the corners of a large park/junction spans terrain bumps.
 * Every split is shared by neighboring faces, so it cannot create a T crack. */
export function drapeSharedGroundGeometry(
  source: THREE.BufferGeometry,
  offsetAt: (x: number, y: number) => number | null,
  maxEdgeM = 4,
  maxVertices = 60000,
  grid?: SharedGroundTriangulation,
): THREE.BufferGeometry | null {
  if (grid) return drapeGridGeometry(source, offsetAt, maxVertices, grid);
  const position = source.getAttribute('position');
  if (!position || maxEdgeM <= 0 || position.count > maxVertices) return null;
  const attributes = Object.entries(source.attributes).map(([name, attribute]) => ({
    name, size: attribute.itemSize,
    values: Array.from({ length: attribute.count }, (_, index) =>
      Array.from({ length: attribute.itemSize }, (_, component) =>
        [attribute.getX, attribute.getY, attribute.getZ, attribute.getW][component].call(attribute, index))),
  }));
  const xyz = attributes.find((attribute) => attribute.name === 'position')!.values;
  const sourceIndices = source.index ? Array.from(source.index.array) : Array.from({ length: position.count }, (_, i) => i);
  if (sourceIndices.length % 3) return null;
  let triangles = Array.from({ length: sourceIndices.length / 3 }, (_, i) => ({
    ids: sourceIndices.slice(i * 3, i * 3 + 3),
    material: source.groups.find((group) => i * 3 >= group.start && i * 3 < group.start + group.count)?.materialIndex ?? 0,
  }));
  const key = (a: number, b: number) => `${Math.min(a, b)}:${Math.max(a, b)}`;
  for (let pass = 0; pass < 12; pass += 1) {
    const splits = new Map<string, number>();
    for (const { ids: [a, b, c] } of triangles) for (const [u, v] of [[a, b], [b, c], [c, a]]) {
      if (Math.hypot(xyz[u][0] - xyz[v][0], xyz[u][1] - xyz[v][1]) <= maxEdgeM + 1e-6) continue;
      const edge = key(u, v);
      if (splits.has(edge)) continue;
      if (xyz.length >= maxVertices) return null;
      const index = xyz.length;
      for (const attribute of attributes) attribute.values.push(attribute.values[u].map((value, j) => (value + attribute.values[v][j]) / 2));
      splits.set(edge, index);
    }
    if (!splits.size) break;
    triangles = triangles.flatMap(({ ids: [a, b, c], material }) => {
      const ab = splits.get(key(a, b)), bc = splits.get(key(b, c)), ca = splits.get(key(c, a));
      let faces: number[][];
      if (ab !== undefined && bc !== undefined && ca !== undefined) faces = [[a, ab, ca], [ab, b, bc], [ca, bc, c], [ab, bc, ca]];
      else if (ab !== undefined && bc !== undefined) faces = [[b, bc, ab], [a, ab, c], [ab, bc, c]];
      else if (bc !== undefined && ca !== undefined) faces = [[c, ca, bc], [a, b, ca], [b, bc, ca]];
      else if (ca !== undefined && ab !== undefined) faces = [[a, ab, ca], [ab, b, c], [ab, c, ca]];
      else if (ab !== undefined) faces = [[a, ab, c], [ab, b, c]];
      else if (bc !== undefined) faces = [[a, b, bc], [a, bc, c]];
      else if (ca !== undefined) faces = [[a, b, ca], [b, c, ca]];
      else faces = [[a, b, c]];
      return faces.map((ids) => ({ ids, material }));
    });
    if (pass === 11) return null;
  }
  for (const point of xyz) {
    const offset = offsetAt(point[0], point[1]);
    if (offset === null || !Number.isFinite(offset)) return null;
    point[2] += offset;
  }
  const geometry = source.clone();
  for (const attribute of attributes) geometry.setAttribute(attribute.name,
    new THREE.Float32BufferAttribute(attribute.values.flat(), attribute.size));
  geometry.setIndex(triangles.flatMap((triangle) => triangle.ids));
  geometry.clearGroups();
  if (source.groups.length) {
    let start = 0;
    for (let i = 1; i <= triangles.length; i += 1) {
      if (i === triangles.length || triangles[i].material !== triangles[start].material) {
        geometry.addGroup(start * 3, (i - start) * 3, triangles[start].material);
        start = i;
      }
    }
  }
  geometry.computeVertexNormals(); geometry.computeBoundingBox(); geometry.computeBoundingSphere();
  return geometry;
}
