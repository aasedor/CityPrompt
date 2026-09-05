import { describe, expect, it } from 'vitest';
import { referenceFeatureLabel, referenceGeometryPaths } from './referenceGeometry';
import type { ReferenceGeometry } from './api';

describe('Reference cartography', () => {
  it('retains polygon holes as independent rings and leaves the source unchanged', () => {
    const geometry: ReferenceGeometry = { type: 'Polygon', coordinates: [
      [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]],
      [[2, 2], [2, 3], [3, 3], [3, 2], [2, 2]],
    ] };
    const before = JSON.stringify(geometry);
    const paths = referenceGeometryPaths(geometry);
    expect(paths.lines).toHaveLength(2);
    expect(paths.points).toEqual([]);
    expect(JSON.stringify(geometry)).toBe(before);
  });
  it('keeps open lines and points instead of buffering them into design areas', () => {
    const paths = referenceGeometryPaths({ type: 'GeometryCollection', geometries: [
      { type: 'LineString', coordinates: [[0, 0], [1, 1]] },
      { type: 'MultiPoint', coordinates: [[2, 2], [3, 3]] },
    ] });
    expect(paths.lines).toEqual([[[0, 0], [1, 1]]]);
    expect(paths.points).toEqual([[2, 2], [3, 3]]);
  });
  it('handles disjoint multi-polygons without joining the parts', () => {
    const paths = referenceGeometryPaths({ type: 'MultiPolygon', coordinates: [
      [[[0, 0], [1, 0], [1, 1], [0, 0]]],
      [[[5, 5], [6, 5], [6, 6], [5, 5]]],
    ] });
    expect(paths.lines).toHaveLength(2);
    expect(paths.lines[1][0]).toEqual([5, 5]);
  });
  it('labels districts from attributes without inventing an archetype', () => {
    expect(referenceFeatureLabel({ ZONING: 'R-CG', height: 11 }, 3)).toBe('R-CG');
    expect(referenceFeatureLabel({}, 3)).toBe('Feature 4');
  });
});
