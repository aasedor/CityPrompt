import { describe, expect, it } from "vitest";
import { pavingGeometry, pavingProblem, pavingHeightAt } from "./pavingSurfaces";
import {
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from "@/components/viewer/mapEngine/geoUtils";
const world = (points: number[][]) =>
  points.map(([x, y]) => [
    -114 + x / metersPerDegLon(51),
    51 + y / METERS_PER_DEG_LAT,
  ]);
describe("custom paving", () => {
  it('keeps parking paint on the triangulated paving plane',()=>{
    const geometry=pavingGeometry(world([[0,0],[20,0],[20,10],[0,10]]),[100,100.4,100.4,100]);
    expect(pavingHeightAt(geometry,[10,5])).toBeCloseTo(.225,4);
    expect(pavingHeightAt(geometry,[5,8])).toBeCloseTo(.125,4);
    expect(pavingHeightAt(geometry,[30,5])).toBeNull();
    geometry.dispose();
  });
  it("accepts concave paved areas and rejects crossed, degenerate and oversized outlines", () => {
    expect(
      pavingProblem(
        world([
          [0, 0],
          [20, 0],
          [20, 10],
          [10, 10],
          [10, 20],
          [0, 20],
        ]),
      ),
    ).toBeNull();
    for (const points of [
      [
        [0, 0],
        [20, 20],
        [0, 20],
        [20, 0],
      ],
      [
        [0, 0],
        [10, 0],
        [20, 0],
      ],
      [
        [0, 0],
        [0.1, 0],
        [1, 1],
      ],
      [
        [0, 0],
        [600, 0],
        [600, 600],
        [0, 600],
      ],
    ])
      expect(pavingProblem(world(points))).not.toBeNull();
  });
  it("triangulates only the drawn concave surface and retains metric heights", () => {
    const geometry = pavingGeometry(
      world([
        [0, 0],
        [20, 0],
        [20, 10],
        [10, 10],
        [10, 20],
        [0, 20],
      ]),
      [100, 100, 100, 100, 100, 100],
    );
    const p = geometry.getAttribute("position"),
      index = geometry.getIndex()!;
    let area = 0;
    for (let i = 0; i < index.count; i += 3) {
      const a = index.getX(i),
        b = index.getX(i + 1),
        c = index.getX(i + 2);
      area +=
        Math.abs(
          (p.getX(b) - p.getX(a)) * (p.getY(c) - p.getY(a)) -
            (p.getY(b) - p.getY(a)) * (p.getX(c) - p.getX(a)),
        ) / 2;
    }
    expect(area).toBeCloseTo(300, 3);
    for (let i = 0; i < p.count; i++) expect(p.getZ(i)).toBeCloseTo(0.025, 5);
    geometry.dispose();
  });
});
