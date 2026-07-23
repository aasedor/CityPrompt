export interface TerrainGroundPoint {
  x: number;
  y: number;
}

export interface TerrainGroundMesh {
  /** Boundary vertices first, followed by one safe interior vertex per face. */
  vertices: TerrainGroundPoint[];
  indices: number[];
  boundaryVertexCount: number;
}

/**
 * Add terrain-sampling vertices without changing a polygon's footprint.
 *
 * The former implementation made smaller copies of the entire boundary around
 * the arithmetic centroid. For concave parcels that centroid can sit outside
 * the polygon, so the connecting triangles produced large green starbursts
 * over adjacent buildings and roads. A triangle centroid is always inside its
 * source triangle, so splitting each already-triangulated face into three
 * gives us interior terrain probes while preserving the exact parcel.
 */
export function buildContainedTerrainGroundMesh(
  boundary: TerrainGroundPoint[],
  triangles: number[][],
): TerrainGroundMesh {
  const vertices = boundary.map((point) => ({ ...point }));
  const indices: number[] = [];

  for (const triangle of triangles) {
    if (triangle.length < 3) continue;
    const [aIndex, bIndex, cIndex] = triangle;
    const a = boundary[aIndex];
    const b = boundary[bIndex];
    const c = boundary[cIndex];
    if (!a || !b || !c) continue;

    const interiorIndex = vertices.length;
    vertices.push({
      x: (a.x + b.x + c.x) / 3,
      y: (a.y + b.y + c.y) / 3,
    });
    indices.push(
      aIndex, bIndex, interiorIndex,
      bIndex, cIndex, interiorIndex,
      cIndex, aIndex, interiorIndex,
    );
  }

  return {
    vertices,
    indices,
    boundaryVertexCount: boundary.length,
  };
}
