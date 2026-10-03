# Natural road transitions: Calgary pilot

Follow-up: [constrained edges and automatic recovery](ROAD_TRANSITION_RETAINING_FIXES_2026-10-02.md)
records the next checkpoint. Results below describe the initial pilot.

## Result and release status

The clear-ground pilot produces a road with smooth terrain joins on real Google
Photorealistic 3D Tiles. It reshapes copies of the surrounding ground mesh while
retaining its imagery. A raised-road stress case also passed the measured joins.
Native walking across the road and verge passed in the browser.

**This is a local development pilot, not the general student street workflow.**
The constrained public-road connection still needs more transition space than
the selected corridor provides. It is rejected with the original scene intact.
Do not claim that arbitrary streets, intersections, trees, or urban road joins
are solved. No deployment or push is part of this change.

## What changed

- `roadTerrainTransition.ts` plans a bounded straight road with a smoothed DEM
  profile, crown, measured end cross sections, and a gradual falloff to the
  existing ground. Grading retains as much of the source profile as the allowed
  longitudinal grade supports.
- `roadTerrainTransitionMesh.ts` refines touching Google triangles to a maximum
  0.5 m horizontal edge length before deformation. It retains their original
  texture coordinates and transforms their normals. Original buffers remain
  available for restoration. Catalogue asphalt and aggregate shoulder materials
  are reused for the road itself.
- `roadTerrainRehearsal.ts` checks the whole corridor before installing anything.
  It installs the road, temporary tile geometry, and a mask confined to the road
  and shoulders. No broad grass rectangle or site-wide elevation shift is used.
- A development panel supports Build transition, Show original/proposal, and
  Walk road. Walk uses the proposal's physical heights inside the corridor.
- Tile load, disposal, and visibility changes invalidate affected proposals.
  Cached tiles becoming visible are handled as well as newly downloaded tiles.
  A changed visible tile set during measurement rejects the build. Invalidation
  restores originals and requires a fresh measurement before showing a proposal.
- Export is blocked while the unsaved rehearsal is visible. Toggling off,
  leaving the page, and disposal restore original geometry and material hooks.
- `calgary_corridor.py` creates the two finite local inputs using the prior
  Calgary alignment pipeline and exact WGS84 ECEF/ENU coordinates matching the
  viewer. It retains source hashes, frame/epoch provenance, and geoid metadata.

The renderer's `dispose-model` event precedes its resource disposal. The pilot
restores source geometry during that event; the renderer disposes its original
cached resources and the pilot owns/disposes its replacement geometries.

## Height interpretation

Three different things remain explicit:

1. The original Calgary DEM and official coordinate transformation.
2. A **local visual registration offset** estimated from five predetermined
   centreline samples. This places the proposal in the observed Google context;
   it is not a new geoid, a citywide datum correction, or survey validation.
3. Proposed road grading, including the explicit optional raised-road stress
   input. The source DEM is not changed to achieve a good-looking join.

The remaining one-metre grid is checked independently of the five controls.
The pilot requires stable samples, a bounded offset, consistent controls, and
ground residuals within the supported range. It also checks refined vertices
for narrow objects that the sample grid could miss. Tree and structure conflicts
are rejected; automatic tree removal is not implemented by this pilot.

The small footprint uses a centre GSD95 geoid value, recorded in the generated
input. Approximate WGS84 display and source accuracy limitations from the prior
alignment trial still apply.

## Real-site results

The accepted field route is 36 m long and 6 m wide, with 0.6 m shoulder planning
width, a 10 m lateral transition, and a 4 m end transition. It has 1,305 ground
probes and modifies copies of four tile meshes (142,251 replacement vertices).

| Measurement | Normal proposal | Raised-road stress case |
| --- | ---: | ---: |
| Local visual registration | -1.2904 m | -1.2904 m |
| Requested additional elevation | 0 m | 1.5 m |
| Maximum sampled ground change | 0.1803 m | 1.0087 m |
| Retained profile fraction | 1.0000 | 0.6441 |
| Maximum checked road grade | 2.471% | 10.000% |
| Maximum road-end join gap | 0.0367 mm | 0.0367 mm |
| Maximum outer lateral join gap | 0.0151 mm | 0.0555 mm |

These tiny gap values measure **rendered mesh continuity**, not real-world
elevation accuracy. The stress case's 10% road grade is not step-free access
certification. Acceptance limits are 25 mm at road ends, 15 mm at the outer
lateral seam, and 12% for the checked physical road grades; the centreline
planner itself is bounded to 10%.

Browser checks covered:

- Build, original/proposal toggle, walking about 15 m along the road, moving
  about 10 m across its verge, and returning. No stuck condition was observed.
- After the visibility safeguard was added, entering Walk loaded different
  detail and invalidated the proposal. A fresh build passed the walking test.
- The stress case restored original geometry identities and material callbacks.
  Input data and saved site-zone JSON remained unchanged.
- Reload left the original site visible; the trial is not persisted as a street.
- The constrained 32 m public-road case displayed “The verge needs more room to
  meet the existing ground.” It installed no proposal; navigation still worked.
- No uncaught browser errors or site-zone/building mutation requests were
  recorded during these checks. These observations do not certify every feature
  of the application.

## Verification

- 39 Vitest tests passed across the transition planner/mesh, rehearsal lifecycle,
  street capture, tile masking, authored camera ground, and walking navigation.
- TypeScript `npm run type-check` passed.
- Vite production build passed. A scan of the emitted JavaScript confirmed the
  development panel and rehearsal implementation are excluded. The build still
  reports large-chunk warnings; no bundle-size remediation was included here.
- 17 Python tests passed under `tools/elevation_trial`, including the official
  alignment grid integration and metric/heading/local-height checks.
- `git diff --check` passed before the checkpoint.

Local source is on `codex/calgary-elevation-trial`. The pre-existing main
workspace and catalogue work were not changed.

## Local reproduction and evidence

From this worktree's root, generate data outside the source tree:

```powershell
python -m tools.elevation_trial.calgary_corridor --data C:/dev-artifacts/CityPrompt/calgary-elevation-2026-10-02 --grid C:/dev-artifacts/CityPrompt/calgary-alignment-2026-10-02/ABCSRSV7.DAC --out C:/dev-artifacts/CityPrompt/road-transitions-2026-10-02
```

The isolated preview uses port 5195 because the existing development servers
and their workspaces were retained. Its environment is:

```powershell
$env:API_PROXY_TARGET='http://127.0.0.1:8018'
$env:VITE_ENV_DIR='C:/Users/andre/OneDrive/Documents/CityPrompt/frontend'
$env:CITYPROMPT_PUBLIC_DIR='C:/Users/andre/.codex/worktrees/reference-fourplex/CityPrompt/frontend/public'
$env:CITYPROMPT_TERRAIN_TRIAL_DIR='C:/dev-artifacts/CityPrompt/road-transitions-2026-10-02'
# From frontend:
node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5195 --strictPort
```

This middleware serves only the two named JSON inputs in development. The data
is not bundled or deployed. Open an authenticated local session at:

- Field: `http://localhost:5195/projects/a2f3a90a-52d3-42c1-8d45-8b4ae23bd5f7?terrainTrial=field`
- Constrained connection: `http://localhost:5195/projects/40e85c35-018f-43d3-afc6-32c292a7033f?terrainTrial=connection`

External evidence directory:
`C:/dev-artifacts/CityPrompt/road-transitions-2026-10-02/`

- `field-ui-walk.json`: normal proposal and native walking measurements.
- `stress-recovery.json`, `reload.json`: stress, restoration, persistence checks.
- `rejection-recovery.json`: constrained-site rejection and navigation recovery.
- `field-walk-start.png`, `field-walk-middle.png`, `field-walk-verge.png`:
  walking views after the final tile-visibility safeguard.
- `stress-before.png`, `stress-after.png`, `stress-oblique.png`: stress views.
- `connection-rejected-ui.png`: readable refusal with the original site intact.
- `ui-test.cjs`, `stress-recovery.cjs`, `rejection-recovery.cjs`: local browser
  harnesses using the existing private test login. Do not publish authentication
  storage with evidence.

Generated DEM grids, network responses, screenshots, local test harnesses, and
installed dependencies remain outside Git. The repository generator supersedes
the preliminary external `prepare.py`; older `field-result.json` and
`connection-result.json` are diagnostic history, not the final results above.

## Remaining work before student release

1. Solve constrained joins with asymmetric slopes, explicit protected objects,
   and designed retaining edges where there is insufficient space for grading.
2. Integrate curved and crossing streets, connected endpoints, route edits,
   undo, save/reload, export, and normal catalogue placement. The current pilot
   handles a single straight corridor with bounded local inputs.
3. Replace manual rebuilding on tile refinement with a controlled remeasurement
   lifecycle suitable for ordinary students, and validate larger scenes within
   an agreed frame-time and memory budget.
4. Test multiple sloping and built-up sites, road archetypes, and transitions
   into existing intersections before enabling the feature by default.

Preserving Google imagery avoids an obvious material rectangle around the road,
but cannot restore detail that is absent from the source photography. Distant
trees and close-up blurry textures in the screenshots are still Google context.
The successful result supports smooth clear-ground transitions; it does not
establish a seamless result at every urban edge.
