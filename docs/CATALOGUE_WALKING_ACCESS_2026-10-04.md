# Catalogue entrance walking

The local City Prompt app on port 5176 now offers **Walk inside** for selected
buildings and **Walk in park** for selected parks. WASD moves, dragging turns,
Return to entrance recovers the camera, and Exit walk restores the design view.

## Runtime changes

- Twenty-nine older exact building revisions now use recorded source door
  coordinates and floor material selectors in `buildingWalkDoors.json`.
  Ground and collision surfaces come from the loaded model's actual triangles.
  Existing authored walking networks remain in use for five older buildings
  and the ten sealed temporary trials.
- Walking opens the measured door leaves on owned scene clones. Shared glazing
  retains its fixed panels. Exiting or unmounting restores the original geometry.
  The Fourplex and Plateau duplex receive small visible steel thresholds during
  walking to bridge measured gaps at their entrances. Original GLBs and hero
  images are unchanged.
- Older saved library recipes without revision stamps verify served GLB bytes
  with SHA-256 before applying a recorded door plan. Changed or unavailable bytes
  cannot inherit door coordinates by name. Every current standard catalogue
  building revision must have an exact walking binding in the regression test.
- Flat native parks use their visible dry surface faces and solid barriers.
  Pond water blocks the ground beneath it; actual boardwalk tops above water
  remain available. Woodland Stream Garden now selects its gravel, moss and
  timber surfaces. Existing stepped parks keep their stairs, bridges and lifts.
  Walking starts facing an available first step and waits for exact park assets.

## Verification

External evidence directory:
`C:/dev-artifacts/CityPrompt/student-community-trial-2026-10-04`.

| Check | Result | Scope |
| --- | --- | --- |
| Older measured building pilot and finite groups | 29 PASS | Connected primary entry, doorway geometry rays, short interior route and outward transition |
| Embedded building networks | 15 PASS | Valid entrance and connected first 1.6 m; five older buildings plus ten trials |
| Native park layouts | 29 PASS | Valid dry entrance and connected first movement; complete routes remain unverified |
| Main app | PASS | Fourplex and Buff-brick interiors, older library office lobby, flexible pocket park and native dog park walking/recovery/exit |
| Full local delivery | 105 choices, 359 dependencies, zero failures | Exact model/image HTTP readback; 19 Model Library SHA readbacks |
| Standard source delivery | 95 choices, 329 dependencies, zero failures | Fresh restart packet v004 |
| Narrow frontend tests | 51 passed | Measured doors, byte identity, floor/barrier movement, entry transforms, recovery and ground lifecycle |
| Backend park tests | 44 passed | Mirrored park metadata |
| TypeScript and touched-file lint | PASS | Current source |

Screenshots include `fourplex-interior-walking.png`, `buff-interior-walking.png`,
`legacy-office-lobby-walking.png`, `park-walking.png` and
`native-dog-park-walking.png`. The consolidated receipt is
`walking-access-results.json`. Intermediate failed experiments remain preserved.

The checked standard delivery packet is
`C:/dev-artifacts/CityPrompt/catalogue-delivery-2026-10-04-v004`.
The owned trial launcher points to it and a freshly verified 160-file legacy
binding receipt. A clean launcher restart was checked, including the ten-fixture
seal. Source guards remain active. This prevents the metadata change from leaving
a stale packet that would reject the next startup.

## Limits

This is ground-floor entrance access. It does not certify every room, secondary
unit entrance, park branch, street-to-door connection or upper storey. Upper
floors require authored circulation; new fallback networks do not invent stairs
or lift connections. Detailed native placements require verified ground and
their native scale. Unsupported imported geometry and unavailable detailed
models cannot be described as walkable.

The browser samples above supplement the finite geometry/network audits; all
44 buildings were not individually driven through in the browser. This work is
runtime integration and does not change sealed architectural review decisions
or grant keeper approval. Original projects were preserved. No paid generation
calls were made; the 20-building automation remains paused.
