import { describe, it, expect } from "vitest";
import {
  projectBenchContext,
  projectBenchFrame,
  readProjectBenches,
  saveProjectBenches,
  readProjectDetails,
  saveProjectDetails,
} from "./projectBenches";
import { benchPlacementProblem } from "./benchDetails";

describe("independent project benches", () => {
  it('does not invalidate an existing close bench arrangement when a distant tree is added', () => {
    const context = projectBenchContext(projectBenchFrame([], []));
    const first = {id:'one',point:{x:0,y:0},yaw:0};
    const second = {id:'two',point:{x:0,y:1.5},yaw:0};
    expect(benchPlacementProblem(first,[first,second],context)).toBeNull();
    expect(benchPlacementProblem(first,[first,second,{id:'tree',point:{x:20,y:20},yaw:0,treeVariant:'oak-0'}],context)).toBeNull();
  });
  it("round trips mixed furniture, preserving tree type, coordinates and existing benches", () => {
    const benches = [{ id: "bench-1", lng: -114.1, lat: 51.05, angle: 0 }];
    const trees = [
      {
        id: "tree-1",
        lng: -114.101,
        lat: 51.051,
        angle: 30,
        variant: "oak-2" as const,
      },
    ];
    const context = projectBenchContext(
      projectBenchFrame([], [...benches, ...trees]),
    );
    expect(
      saveProjectDetails(
        readProjectDetails(
          { version: 1, revision: 3, can_edit: true, benches, trees },
          context,
        ),
        context,
      ),
    ).toEqual({ benches, trees });
    expect(
      readProjectDetails(
        { version: 1, revision: 0, can_edit: true, benches },
        context,
      ),
    ).toHaveLength(1);
    expect(
      benchPlacementProblem(
        {
          id: "tree",
          point: { x: 1000, y: 1000 },
          yaw: 0,
          treeVariant: "oak-0",
        },
        [],
        context,
      ),
    ).toBeNull();
  });
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
