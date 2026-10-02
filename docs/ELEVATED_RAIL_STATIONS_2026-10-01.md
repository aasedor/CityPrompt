# Two elevated rail stations — local runtime review

This initiative adds two exact Streets → Transit catalogue variants:

| Variant | Parent archetype | Station design |
| --- | --- | --- |
| `skytrain_elevated_corridor_v0` | `skytrain_elevated_corridor` | Blue-glass modern station hub |
| `elevated_rail_transit_corridor_v0` | `elevated_rail_transit_corridor` | Pale, perforated civic-flow canopy |

Each uses a 26 m straight corridor on a prepared level site. The supported
route length is 48–288 m. The deck, two tracks, ground paths, planting, piers,
furniture, static train and lighting extend with the route. The editor's
**Add a station** control places a full rigid station at a chosen point. A
station includes two side platforms, canopy, wayfinding, seating, real stairs
on both outer sides and protected boarding edges. A route supports up to four
stations, each at least 24 m from either end and 52 m from another station.
The editor supports moving and removing stations, and the saved stations
survive reload. This is an architectural concept model: trains are static;
rail junctions, street crossings, natural/sloped terrain and accessible
station circulation are outside this variant's supported program.

## Exact delivery

- Generator: `tools/public_realm_assets/build_elevated_station_rail.py`.
- Registrar/hydrator: `scripts/elevated_rail_stations.py`.
- Immutable seeds: `seed/classroom-streets/skytrain-modern-station-v001` and
  `seed/classroom-streets/civic-flow-station-v001`.
- Machine-readable source hashes and review state:
  [ELEVATED_RAIL_STATIONS_2026-10-01.json](ELEVATED_RAIL_STATIONS_2026-10-01.json).
- External render and live-browser evidence:
  `C:/dev-artifacts/CityPrompt/elevated-rail-stations-2026-10-01`.

The finite batch used a dry run for both designs, then one exported and
reimported GLB pilot for each. The 48 m preview fixtures have 109,832 and
111,128 triangles respectively. Each has ten reusable GLB modules, including
the station module, with SHA-256 locks in its seed manifest. Detail and
overhead renders were inspected from the reimported geometry. Only these two
reviewed pilots were registered. Working render output is outside the source
tree; seed assets and intentional catalogue heroes are the deliverables.

## Live editor review

Both variants were placed through the ordinary student controls in the
disposable project at
`http://localhost:5186/projects/d52ba95f-f099-4e8e-a4b3-26142f28bdcd`.
Each saved route is about 152 m and mounts 153 required native components.
The SkyTrain station was added at 74.5 m, moved to 104.5 m, then Undo/Redo
restored each position under the same zone ID. The Civic Flow station was
added at 75.1 m. After a full page reload both persisted, every required
module reported ready and the scene had no grounding issues.

The Civic Flow stairs were traversed with the normal Walk keyboard controls:
ground entrance, up, across the platform and back down. The 11-waypoint loop
completed in 64.4 s with 1,603 samples and zero browser errors. Feet rose
from the prepared ground at 1097.045 m to the platform at 1105.018 m, then
returned to 1097.045 m. Both variants share the tested walking function;
the SkyTrain stair geometry was inspected in the exported GLB and has a
focused geometry/walking test, but a second full browser walk was not run.

| Gate | Result |
| --- | --- |
| C1 exact identity | PASS: exact seed, frontend/backend catalogue and native module locks agree. |
| C2 dimensions | PASS: rigid station and supports, continuous rails, bounded straight route, fixed 26 m width; arbitrary residual lengths have focused tests. |
| C3 ground | PASS on prepared level site; natural/sloped placement is unsupported. |
| C4 freshness | PASS: complete required modules after save and reload. |
| C5 walking | PASS for Civic Flow's ordinary-control ascent and descent; SkyTrain uses the same walking program and has focused tests. Public-road access is unsupported. |
| C6 edit/reopen | PASS: add, move, Undo, Redo and reload for SkyTrain; add and reload for Civic Flow. Remove has focused tests. |
| C7 recovery | PASS in focused tests for invalid station positions, spacing, overlap and changed package bytes. Forced network failure was not exercised live. |
| C8 visuals | PASS for actual reimported GLB render inspection and live 3D scene. Human visual approval and exact saved 3D export remain open. |
| C9 controls | PASS: catalogue selection, route drawing, right-click position, Add a station, move, Undo, Redo, reload and Walk used in the disposable project. |

This is an author review and local catalogue activation. Human visual
approval and publication remain separate. No push or deployment is included.
