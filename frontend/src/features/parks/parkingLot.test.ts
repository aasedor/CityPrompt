import { describe, expect, it } from 'vitest';
import { parkingLayout, parkingMarkingGeometry, type ParkingRecipe } from './parkingLot';

const recipe: ParkingRecipe = { version: 1, rowAngle: 0 };
const rectangle = [[0, 0], [40, 0], [40, 18], [0, 18]];

describe('drawn parking layout', () => {
  it('fits two rows around a real drive aisle and a clear side connector', () => {
    const lot = parkingLayout(rectangle, recipe);
    expect(lot.spaces).toHaveLength(24);
    expect(lot.aisles).toHaveLength(2);
    const first = lot.spaces[0].corners;
    expect(Math.hypot(first[1][0] - first[0][0], first[1][1] - first[0][1])).toBeCloseTo(2.7);
    expect(Math.hypot(first[2][0] - first[1][0], first[2][1] - first[1][1])).toBeCloseTo(5.5);
    expect(Math.min(...lot.spaces.flatMap(s => s.corners.map(p => p[0])))).toBeGreaterThanOrEqual(6.5);
    expect(lot.aisles[1][2][1] - lot.aisles[1][1][1]).toBeCloseTo(6);
  });
  it('recalculates capacity instead of stretching spaces when the boundary changes', () => {
    expect(parkingLayout([[0,0],[30,0],[30,18],[0,18]], recipe).spaces).toHaveLength(16);
    expect(parkingLayout([[0,0],[40,0],[40,35],[0,35]], recipe).spaces).toHaveLength(48);
    expect(parkingLayout([[0,0],[8,0],[8,8],[0,8]], recipe).spaces).toHaveLength(0);
  });
  it('omits bays and their aisle where a concave notch would cut the module', () => {
    const lot = parkingLayout([[0,0],[40,0],[40,18],[20,18],[20,35],[0,35]], recipe);
    expect(lot.spaces).toHaveLength(32);
    expect(lot.spaces.every(s => s.corners.every(([x,y]) => x <= 20 || y <= 18))).toBe(true);
    // A notch crossing the drive connector cannot be bridged by painted bays.
    const interrupted = parkingLayout([[0,0],[40,0],[40,35],[0,35],[0,20],[10,20],[10,15],[0,15]], recipe);
    expect(interrupted.aisles.every(aisle => aisle.every(([x,y]) => x >= 10 || y <= 15 || y >= 20))).toBe(true);
  });
  it('keeps metre dimensions under rotated outlines and changes row direction independently', () => {
    const rotated = rectangle.map(([x,y]) => [-y+80,x+20]);
    expect(parkingLayout(rotated, recipe).spaces).toHaveLength(24);
    const turned = parkingLayout(rectangle, {...recipe, rowAngle:90});
    expect(turned.spaces).toHaveLength(16);
    const first = turned.spaces[0].corners;
    expect(Math.abs(first[1][0]-first[0][0])).toBeCloseTo(0);
    expect(Math.abs(first[1][1]-first[0][1])).toBeCloseTo(2.7);
  });
  it('fits a slightly tapered outline while keeping a continuous interior side aisle',()=>{
    const lot=parkingLayout([[0,0],[40,0],[40,18],[1,18]],recipe);
    expect(lot.problem).toBeNull();
    expect(lot.spaces.length).toBeGreaterThan(0);
    expect(lot.aisles[0][0][0]).toBeGreaterThanOrEqual(1);
  });
  it('rejects unsupported intermediate row angles explicitly',()=>{
    expect(parkingLayout(rectangle,{...recipe,rowAngle:15}).problem).toMatch(/along or across/);
  });
  it('rejects invalid or oversized parking inputs without unbounded geometry work', () => {
    expect(parkingLayout([[0,0],[40,18],[40,0],[0,18]],recipe).problem).toBeTruthy();
    expect(parkingLayout(rectangle,{...recipe,rowAngle:NaN}).problem).toBeTruthy();
    expect(parkingLayout([[0,0],[500,0],[500,500],[0,500]],recipe).problem).toBeTruthy();
  });
  it('builds one bounded marking mesh with no opaque backing across the drive aisle', () => {
    const lot = parkingLayout(rectangle,recipe);
    const mesh = parkingMarkingGeometry(lot);
    const position = mesh.getAttribute('position');
    expect(position.count).toBeGreaterThan(0);
    expect(position.count).toBeLessThanOrEqual(24*18);
    let area = 0;
    for(let i=0;i<position.count;i+=3){
      area+=Math.abs((position.getX(i+1)-position.getX(i))*(position.getY(i+2)-position.getY(i))-(position.getY(i+1)-position.getY(i))*(position.getX(i+2)-position.getX(i)))/2;
    }
    expect(area).toBeLessThan(40); // only thin paint, never a second lot surface
    mesh.dispose();
  });
  it('places paint just above the actual paving height instead of burying sloped markings',()=>{
    const lot=parkingLayout(rectangle,recipe);
    const mesh=parkingMarkingGeometry(lot,([x])=>.025+x*.02);
    const p=mesh.getAttribute('position');
    for(let i=0;i<p.count;i++)expect(p.getZ(i)).toBeCloseTo(.03+p.getX(i)*.02,5);
    mesh.dispose();
  });
});
