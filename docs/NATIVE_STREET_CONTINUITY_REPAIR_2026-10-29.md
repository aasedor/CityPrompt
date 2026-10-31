# Native street continuity repair — 29 October 2026

Scope: shared runtime ground reconstruction, with Protected Cycle Avenue
`student_cycle_avenue_v1` / `protected_bike_lane_bidirectional` as the reproducer.
This is a source-code regression checkpoint; native browser visual acceptance,
new asset approval and publication are separate gates.

- Runtime base: `baf5af30fbb3912ac2dc2b2425205d3cc69c6776`; shared branch
  `codex/student-final-fixes-20261029`, plus the reviewed working-tree patch.
- Immutable source programme SHA-256:
  `99ef1a25957d986e7e79af8c69bffa983ff5ab9f7e9d9cb981ddd336d7f4e07b`.
- Native section: 24 m total, 6 m asphalt lane and 4 m cycle band; source
  furniture repetition 48 m. Source catalogue JSON, module locks and GLB bytes
  are unchanged.
- Reproducer screenshot:
  `D:/CityPrompt-review-artifacts/storage-and-stress-20261029/01-street-intersections-overhead.png`.
- Test logs (local evidence, not a shared delivery):
  `D:/CityPrompt-review-artifacts/student-final-fixes-20261029/streets/`.

The pale bars came from the source builder's `link()` region: a 3 m deep,
full-width paving access footprint at each fixture centre. Repeating the entire
ground ownership partition replaced both travel bands every 48 m. The bars were
fixture-centre links, rather than GLB endcaps or a junction snapping failure.

`nativeStreetProgram.ts` now splits that full-width paving overlay around the
source's continuous asphalt/cycle bands. Pedestrian access through the planted
separator and sidewalks remains paved. Local crossing regions, source markings,
rigid furniture and actual network-junction ownership remain intact. The raw
`nativeStreetGroundCells` source-study partition is unchanged.

| Gate | Status | Evidence / limitation |
| --- | --- | --- |
| S1 native metric section and repeated travel surfaces | PASS, geometry only | Material-aware rays across full 6 m asphalt / 4 m cycle widths at source centres, 48 m seams, route ends and partial final modules; 240/253 m, both directions. Bounds retain the native widths. |
| S2 actual junction ownership | PASS, geometry only | 90-degree and 60-degree-layout clipping removes all source geometry from the owned node, retains downstream travel surfaces, and preserves node pavement/crosswalk geometry. |
| Pedestrian links / authored local crossing / markings | PASS, geometry only | Separator and sidewalk paving retained; narrow and full-ROW explicitly located local crossings retain paving ownership; source paint geometry remains. Existing shared-lane and classroom source programme tests pass. |
| C1 source locks / asset identity | PASS, source scope only | No source JSON or GLB changes; existing production-recipe/runtime tests are outside this narrow run. |
| C3 / S3 prepared or natural terrain and public-road grade | NOT TESTED | No new browser or terrain measurements in this checkpoint. |
| C6 student edit / Undo / reload | NOT TESTED | Root review must verify the complete scene through ordinary controls. |
| C8 native low/aerial visual review and exact capture | PASS, bounded browser case | Root reviewed the original roughly 240 m avenue overhead and oblique, with 90° and angled junctions; repeated pale travel bands are absent. Free exact capture preview succeeds. Screenshot evidence in the October 29 student-final-fixes folder; original PNG download remains unverified. No paid image/video generation. |
| Catalogue activation / publication | N/A | Shared renderer fix; no archetype activation or publication requested. |

Test-first evidence: `nativeStreetContinuity.test.ts` initially failed four of
five tests at the reproduced source-centre travel gap (22.6 m into the route)
and downstream junction approach. After the fix, six targeted files passed:
79 tests covering continuity, native/source programmes, long routes and native
junction geometry. `red.log` and `green.log` retain the actual outputs.
An additional failing-first crossing guard (`crossing-red.log`) established
that the access-link rule must apply at the fixture centre only; a separately
located full-width crossing remains authored paving. Type-check ran and reported
two unrelated incomplete `SiteZone` fixture casts in
`frontend/src/features/pickPlace/rotationProbe.test.ts`, lines 16 and 30;
`type-check.log` retains the diagnostics for the owning fix.

Remaining classroom blocker: review the repaired native scene at overhead and
pedestrian height before declaring the visible false-sidewalk defect closed.
The source programmes do not provide a semantic crossing registry; this repair
recognizes the specific fixture-centred full-ROW short paving access footprint over continuous
asphalt/cycle bands. An intentionally full-ROW paved crossing in a future source
programme needs explicit ownership semantics before it can share that pattern.
