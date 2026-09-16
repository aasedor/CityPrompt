# Gold Standard: Currie learning community

Baseline source: `1172db1ef`. Definition, fixed cameras, route and measurements
are in `docs/benchmarks/`. Local project:
`e18c8436-2612-4548-990e-0fa506748efd`.

This reproducible fictional redevelopment is API-authored from the current
canonical placement registry. It is not a survey or evidence of the novice
authoring journey. Its 270 × 250 m Calgary site contains 16 native buildings
(detached homes, civic hall, two mixed-use mid-rises, motel and residential
tower), three street types with two four-way intersections, and two reviewed
parks. Geometry was checked for containment and unintended overlap before
creation. All 16 models compiled through the existing application workflow.

Five ENU cameras are frozen: AERIAL, MAIN_STREET, PARK, RESIDENTIAL and
INTERSECTION. The eight-second, 24 fps eastbound street route is defined;
guide video capture remains pending. Preserve geometry and cameras when
comparing later phases. Do not remodel the fixture to conceal defects.

## Local evidence

Root: `C:/dev-artifacts/CityPrompt/student-design-transformation/`.

- `FROZEN-BEFORE-*.png`: five scene views and building catalogue; inspected.
- `baseline-direct3d-aerial.{json,png}`: existing deterministic capture v2,
  exact camera and geometry passes; inspected. No AI finishing requested.
- `benchmark-frozen-export.json`, `benchmark-reloaded-export.json`: complete
  local snapshots; all 22 zones retained identical coordinates and properties.
- `baseline-reload.json`: warm reload reached settled state in 8.81 seconds
  including CLI overhead; zero new browser errors.
- `runtime-hydration.json`: 207 assets / 124,903,218 bytes materialized from
  exact checkpoint Git/LFS objects, with size and hash verification.
- `local-before.dump`: isolated test database backup before fixture creation.
- `api-test-ledger.json`: paid image/video validation remains US $0.

Older `BEFORE-*`, `BASELINE-*` and `asset-recovery-*` pictures diagnose missing
local assets and are not the comparison baseline. The reused public directory
lacked current park GLBs and textures; Vite returned HTML for missing files.
After complete hydration and restart, park structures and materials load.
Cumulative browser errors include these setup failures; the clean reload added
none. No production renderer patch was required for this setup correction.

## Measurements and limits

At 1600 × 1000, DPR 1, five-second stationary samples in aerial and main-street
views gave median 16.7 ms and p95 16.8 ms rAF intervals, with no interval over
50 ms. JS heap samples were 380 MB and 445 MB. Visible scene traversal estimated
1.23M / 1.39M triangles and 575 / 635 meshes. These are not GPU timing, draw calls,
GPU memory or total network traffic. Resource timing has cross-origin and buffer
limits. No performance improvement is claimed.

This fixture uses a declared concept ellipsoid grade of 1102 m. Its exposed
prepared-site edge is a baseline defect, not an accepted terrain transition.
Natural-slope coverage requires the independent Salisbury fixture
`f289f565-1a52-43ec-accc-38cb5ac24ea2` and additional mixed-object cases.
Townhouse/rowhouse detail is not represented in the current placement registry.
Existing projects were preserved; full compatibility, novice journey, slope,
context-switch and final media acceptance remain open.

Current-source narrow verification: Community 3D, shared ground and deterministic
video clock, three suites / 26 passing tests. Earlier audit checks remain in the
architecture report. This benchmark enables implementation; it does not accept
the mission's final grounding or visual-quality gates.
