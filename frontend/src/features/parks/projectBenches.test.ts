import { describe, it, expect } from "vitest";
import {
  projectBenchContext,
  projectBenchFrame,
  readProjectBenches,
  saveProjectBenches,
} from "./projectBenches";
import { benchPlacementProblem } from "./benchDetails";

describe("independent project benches", () => {
  it("allows open ground with no archetypes or site boundary, including outside the initial view", () => {
    const frame = projectBenchFrame([], [], {
      longitude: -114.1,
      latitude: 51.05,
    });
    const context = projectBenchContext(frame);
    expect(
      benchPlacementProblem(
        { id: "one", point: { x: -500, y: 900 }, yaw: 0 },
        [],
        context,
      ),
    ).toBeNull();
  });
  it("persists geographic positions independently of the editor frame or surrounding zones", () => {
    const saved = [{ id: "one", lng: -114.101, lat: 51.051, angle: 45 }];
    const one = projectBenchContext(
      projectBenchFrame([], saved, { longitude: -114.1, latitude: 51.05 }),
    );
    const two = projectBenchContext(
      projectBenchFrame(
        [projectBenchFrame([], [], { longitude: -114.2, latitude: 51.08 })],
        saved,
      ),
    );
    expect(one.fromWorld([saved[0].lng, saved[0].lat])).not.toEqual(
      two.fromWorld([saved[0].lng, saved[0].lat]),
    );
    expect(saveProjectBenches(readProjectBenches(saved, one), one)).toEqual(
      saved,
    );
    expect(saveProjectBenches(readProjectBenches(saved, two), two)).toEqual(
      saved,
    );
  });
});
