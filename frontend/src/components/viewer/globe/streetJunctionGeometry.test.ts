import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { buildSectionJunctionGeometry, buildStreetJunctionSurface, clipStreetGeometryOutsideJunction, streetJunctionContainsPoint, type StreetJunctionLayout } from './streetJunctionGeometry';
import { buildAccessibleFourWayIntersectionGeometry } from './streetMesh3D';

const tee: StreetJunctionLayout = {
  bearing: 0, rowA: 8, rowB: 7, roadA: 4, roadB: 3.5, sidesB: [1],
  bounds: [{ minX: -11, maxX: 11, minY: -8, maxY: 8 }, { minX: -7, maxX: 7, minY: 0, maxY: 12 }],
};

describe('catalogue cross-section junctions', () => {
  it('clears furniture from the full rotated junction and its ramp approaches', () => {
    const rotated = {...tee,bearing:Math.PI/2};
    expect(streetJunctionContainsPoint(rotated,-11,0,2)).toBe(true);
    expect(streetJunctionContainsPoint(rotated,-15,0,2)).toBe(false);
    expect(streetJunctionContainsPoint(tee,0,-11,0)).toBe(false);
  });
  const layout: StreetJunctionLayout = { ...tee, sections: [
    { low: -2, high: 4, roadZ: 0.1, edgeZ: 0.245, raised: true },
    { low: -2.7, high: 2.7, roadZ: 0.11, edgeZ: 0.09, raised: false },
  ] };
  it.each([-.6, .6])('joins skew surfaces and clips the same footprint, shear=%s', shear => {
    const skew = { ...layout, shear }, geometry = buildSectionJunctionGeometry(skew);
    const x = (u: number, v: number) => u + shear * v;
    expect(covers(geometry.pavement, x(0, 10), 10)).toBe(true);
    expect(covers(geometry.pavement, x(4, 10), 10)).toBe(false);
    expect(covers(geometry.sidewalks, x(0, -6), -6)).toBe(true);
    expect(covers(geometry.pavement, x(0, -10), -10)).toBe(false);
    expect(streetJunctionContainsPoint(skew, x(0, 11), 11)).toBe(true);
    const source = new THREE.PlaneGeometry(100, 100);
    const clipped = clipStreetGeometryOutsideJunction(source, skew);
    expect(covers(clipped, x(0, 10), 10)).toBe(false);
    expect(covers(clipped, 40, 40)).toBe(true);
    const plain = buildSectionJunctionGeometry(layout);
    expect(area(geometry.pavement)).toBeCloseTo(area(plain.pavement), 4);
    Object.values(geometry).forEach(g => g.dispose()); Object.values(plain).forEach(g => g.dispose()); source.dispose(); clipped.dispose();
  });
  it('keeps an offset carriageway, cuts six ramps and does not invent a fourth arm', () => {
    const g = buildSectionJunctionGeometry(layout);
    expect(covers(g.pavement, -8, 3.8)).toBe(true);
    expect(covers(g.pavement, -8, -3)).toBe(false);
    expect(covers(g.sidewalks, -8, -3)).toBe(true);
    expect(covers(g.pavement, 0, -10)).toBe(false);
    expect(covers(g.sidewalks, -5.6, 4.8)).toBe(false);
    expect(covers(g.curbRamps, -5.6, 4.8)).toBe(true);
    // Six warning pads, two upward-facing triangles each.
    expect(g.tactilePads.getAttribute('position').count).toBe(36);
    const normals = g.tactilePads.getAttribute('normal');
    for (let i = 0; i < normals.count; i++) expect(normals.getZ(i)).toBeGreaterThan(0.9);
    Object.values(g).forEach(item => item.dispose());
  });
  it('keeps shared/shared junctions level, with no fake ramps or raised curb', () => {
    const section = {low: -2.7, high: 2.7, roadZ: 0.11, edgeZ: 0.09, raised: false};
    const g = buildSectionJunctionGeometry({...layout, sections: [section, section]});
    expect(g.curbRamps.getAttribute('position').count).toBe(0);
    expect(g.crosswalks.getAttribute('position').count).toBe(3 * 7 * 6);
    const p = g.pavement.getAttribute('position');
    for (let i = 0; i < p.count; i++) expect(p.getZ(i)).toBeCloseTo(0.11, 6);
    Object.values(g).forEach(item => item.dispose());
  });
});
function area(geometry: THREE.BufferGeometry) {
  const vertices = geometry.getAttribute('position'); const index = geometry.getIndex();
  let sum = 0;
  for (let i = 0; i < (index?.count ?? vertices.count); i += 3) {
    const [a, b, c] = [0, 1, 2].map((j) => index ? index.getX(i + j) : i + j);
    sum += Math.abs((vertices.getX(b) - vertices.getX(a)) * (vertices.getY(c) - vertices.getY(a))
      - (vertices.getY(b) - vertices.getY(a)) * (vertices.getX(c) - vertices.getX(a))) / 2;
  }
  return sum;
}
function covers(geometry: THREE.BufferGeometry, x: number, y: number) {
  const ray = new THREE.Raycaster(new THREE.Vector3(x, y, 10), new THREE.Vector3(0, 0, -1));
  const material = new THREE.MeshBasicMaterial({ side: THREE.DoubleSide });
  const result = ray.intersectObject(new THREE.Mesh(geometry, material)).length > 0;
  material.dispose(); return result;
}

describe('node-owned orthogonal flatwork', () => {
  it('has a continuous back sidewalk, pavement in three arms and no fourth stub', () => {
    const result = buildStreetJunctionSurface(tee);
    expect(covers(result.sidewalks, 0, -6)).toBe(true);
    expect(covers(result.pavement, 0, -6)).toBe(false);
    expect(covers(result.pavement, 0, 10)).toBe(true);
    expect(covers(result.pavement, -10, 0)).toBe(true);
    expect(covers(result.pavement, 10, 0)).toBe(true);
    for (const geometry of Object.values(result)) expect(covers(geometry, 0, -10)).toBe(false);
    // Exact union area 408 m², with six real ramp openings in sidewalk.
    expect(area(result.pavement) + area(result.sidewalks)).toBeCloseTo(408 - 6 * 1.8 * 1.8, 1);
    Object.values(result).forEach((geometry) => geometry.dispose());
  });

  it('retains all four X approaches and cuts only three T crossings', () => {
    const x = buildAccessibleFourWayIntersectionGeometry(0, Math.PI / 2, 4, 3.5)!;
    const t = buildAccessibleFourWayIntersectionGeometry(0, Math.PI / 2, 4, 3.5, [[-1, 1], [1]])!;
    expect(t.crosswalks.getIndex()!.count).toBe(x.crosswalks.getIndex()!.count * 3 / 4);
    expect(t.curbRamps.getIndex()!.count).toBe(x.curbRamps.getIndex()!.count * 3 / 4);
    const positions = t.crosswalks.getAttribute('position');
    expect(Math.min(...Array.from({ length: positions.count }, (_, i) => positions.getY(i)))).toBeGreaterThanOrEqual(-4);
    [...Object.values(t), ...Object.values(x)].forEach((geometry) => geometry.dispose());
  });

  it('joins an X without covering its fourth arm with a sidewalk', () => {
    const result = buildStreetJunctionSurface({ ...tee, sidesB: [-1, 1], bounds: [tee.bounds[0], { ...tee.bounds[1], minY: -12 }] });
    expect(covers(result.pavement, 0, -10)).toBe(true);
    expect(covers(result.sidewalks, 0, -6)).toBe(false);
    Object.values(result).forEach((geometry) => geometry.dispose());
  });
});

describe('exact street triangle ownership clipping', () => {
  it('cuts the union out of a long segment, preserves UVs/grade and never mutates source', () => {
    const source = new THREE.PlaneGeometry(200, 20);
    const vertices = source.getAttribute('position');
    for (let i = 0; i < vertices.count; i += 1) vertices.setZ(i, vertices.getX(i) * 0.1 + vertices.getY(i) * 0.2);
    const before = Array.from(vertices.array);
    const clipped = clipStreetGeometryOutsideJunction(source, tee);
    expect(area(clipped)).toBeCloseTo(4000 - 380, 2);
    expect(Array.from(vertices.array)).toEqual(before);
    const positions = clipped.getAttribute('position'); const uv = clipped.getAttribute('uv');
    for (let i = 0; i < positions.count; i += 1) {
      expect(positions.getZ(i)).toBeCloseTo(positions.getX(i) * 0.1 + positions.getY(i) * 0.2, 4);
      expect(uv.getX(i)).toBeCloseTo(positions.getX(i) / 200 + 0.5, 4);
    }
    expect(covers(clipped, 0, 0)).toBe(false);
    expect(covers(clipped, 50, 0)).toBe(true);
    source.dispose(); clipped.dispose();
  });

  it('clips vertical curb faces and supports rotated/local-offset node frames', () => {
    const source = new THREE.PlaneGeometry(200, 1);
    source.rotateX(Math.PI / 2); source.rotateZ(Math.PI / 4); source.translate(20, 30, 0.5);
    const result = clipStreetGeometryOutsideJunction(source, { ...tee, bearing: Math.PI / 4 }, 20, 30);
    const positions = result.getAttribute('position');
    for (let i = 0; i < positions.count; i += 3) {
      const x = [0, 1, 2].reduce((sum, j) => sum + positions.getX(i + j), 0) / 3 - 20;
      const y = [0, 1, 2].reduce((sum, j) => sum + positions.getY(i + j), 0) / 3 - 30;
      expect(Math.abs((x + y) / Math.sqrt(2))).toBeGreaterThanOrEqual(11 - 1e-4);
    }
    source.dispose(); result.dispose();
  });
});


it.each([3, 4])('faces every tactile pad and ramp top upward for a %s-arm junction', (arms) => {
  const result = buildAccessibleFourWayIntersectionGeometry(0, Math.PI / 2, 4, 3.5,
    [[-1, 1], arms === 3 ? [1] : [-1, 1]])!;
  for (const [geometry, trianglesPerAssembly] of [[result.tactilePads, 2], [result.curbRamps, 10]] as const) {
    const index = geometry.getIndex()!; const p = geometry.getAttribute('position');
    for (let i = 0; i < index.count; i += trianglesPerAssembly * 3) {
      const [a, b, c] = [0, 1, 2].map((offset) => new THREE.Vector3().fromBufferAttribute(p, index.getX(i + offset)));
      expect(b.clone().sub(a).cross(c.clone().sub(a)).z).toBeGreaterThan(0);
    }
  }
  Object.values(result).forEach((geometry) => geometry.dispose());
});


it('keeps metre UV scale and the through-street phase on node surfaces', () => {
  const surfaces = buildStreetJunctionSurface({ ...tee, uvFrame: { bearing: Math.PI / 2, u: 11, v: 7 } });
  for (const geometry of [surfaces.pavement, surfaces.sidewalks]) {
    const p = geometry.getAttribute('position'); const uv = geometry.getAttribute('uv');
    for (let i = 0; i < p.count; i += 1) {
      expect(uv.getX(i)).toBeCloseTo(p.getY(i) + 11, 4);
      expect(uv.getY(i)).toBeCloseTo(-p.getX(i) + 7, 4);
    }
  }
  Object.values(surfaces).forEach((geometry) => geometry.dispose());
});
