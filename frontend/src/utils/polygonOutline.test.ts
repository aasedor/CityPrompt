import { describe, expect, it } from 'vitest';
import { polygonOutlineProblem } from './polygonOutline';

const ring = (points: number[][]) => points.map(([x, y]) => [-114 + x / 70000, 51 + y / 111320]);

describe('student site outlines', () => {
  it('rejects a crossed site before its drawing points are cleared', () => {
    expect(polygonOutlineProblem(ring([[0,0],[80,60],[80,0],[0,60]]), 'site boundary'))
      .toContain('site boundary crosses itself');
  });
  it('rejects a boundary that touches an earlier edge', () => {
    expect(polygonOutlineProblem(ring([[0,0],[80,0],[80,60],[40,0],[0,60]]), 'site boundary'))
      .toContain('crosses itself');
  });
  it('accepts a concave site in either winding direction', () => {
    const concave = ring([[0,0],[80,0],[80,25],[30,25],[30,60],[0,60]]);
    expect(polygonOutlineProblem(concave, 'site boundary')).toBeNull();
    expect(polygonOutlineProblem([...concave].reverse(), 'site boundary')).toBeNull();
  });
  it('rejects a duplicate corner and non-finite coordinates', () => {
    expect(polygonOutlineProblem(ring([[0,0],[0,0],[80,60],[0,60]]), 'site boundary')).toContain('space');
    expect(polygonOutlineProblem([[0,0],[1,0],[NaN,1]], 'site boundary')).toContain('corners');
  });
});
