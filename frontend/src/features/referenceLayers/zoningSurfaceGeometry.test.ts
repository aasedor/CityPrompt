import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { zoningSurfaceGeometry } from './zoningSurfaceGeometry';
import { zoningColor } from './zoningAppearance';
import type { Position, ZoningOverlay } from './zoningLabels';

const ring: Position[] = [[-114.12,51.01],[-114.118,51.01],[-114.118,51.012],[-114.12,51.012],[-114.12,51.01]];
const data: ZoningOverlay = { bounds: [-114.12,51.01,-114.118,51.012], loadedAt: 'test', districts: [
  { id: 'park', code: 'S-SPR', label: 'S-SPR', anchor: [-114.119,51.011], polygon: [ring] },
] };
function area(geometry: THREE.BufferGeometry) {
  const p = geometry.attributes.position;
  let sum = 0;
  for (let i=0;i<p.count;i+=3) sum += Math.abs((p.getX(i+1)-p.getX(i))*(p.getY(i+2)-p.getY(i))-(p.getY(i+1)-p.getY(i))*(p.getX(i+2)-p.getX(i)))/2;
  return sum;
}
describe('globe district surfaces', () => {
  it('preserves polygon holes, uses legend colours, and leaves source data untouched', () => {
    const hole: Position[] = [[-114.1195,51.0105],[-114.1185,51.0105],[-114.1185,51.0115],[-114.1195,51.0115],[-114.1195,51.0105]];
    const withHole = { ...data, districts: [{...data.districts[0], polygon: [ring,hole]}] };
    const before = JSON.stringify(withHole);
    const solid = zoningSurfaceGeometry(data,1100), cut = zoningSurfaceGeometry(withHole,1100);
    expect(area(cut.fill)/area(solid.fill)).toBeCloseTo(0.75,3);
    expect(cut.lines.length/6).toBe(8);
    const colour = new THREE.Color(zoningColor(data.districts[0]));
    expect(cut.fill.attributes.color.getX(0)).toBeCloseTo(colour.r,6);
    expect(JSON.stringify(withHole)).toBe(before);
    solid.fill.dispose(); cut.fill.dispose();
  });
  it('deduplicates identical shared edges and handles no districts', () => {
    const nextRing: Position[] = [[-114.118,51.01],[-114.116,51.01],[-114.116,51.012],[-114.118,51.012],[-114.118,51.01]];
    const combined = zoningSurfaceGeometry({...data, districts: [...data.districts, {...data.districts[0], id:'next', polygon:[nextRing]}]},1100);
    expect(combined.lines.length/6).toBe(7);
    const empty = zoningSurfaceGeometry({...data,districts:[]},NaN);
    expect(empty.fill.attributes.position.count).toBe(0);
    expect(empty.lines).toHaveLength(0);
    expect(empty.height).toBe(1);
    combined.fill.dispose(); empty.fill.dispose();
  });
});
