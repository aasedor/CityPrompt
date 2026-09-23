# Route-based native street catalogue pilot

Branch: `codex/native-street-catalogue-pilot`. Date: 2026-09-23.

This is a bounded **candidate** checkpoint for two accepted offline street
concepts. It is not yet a student-picker release, an active Public Realm LEGO
family, a Currie project acceptance, or authorization to publish the other
eight streets. The source package still declares `runtime_approved: false`.

## Exact pilot sources

| Candidate | Width / source fixture | Separate modules / poses | Locked preview assembly SHA-256 |
| --- | --- | --- | --- |
| `student_main_street_v1` (`neighborhood_main_street`) | 23 m / 48 m | 8 / 30 | `e0e34bfde671aee925a2199d2845cdd3a49e2935cac587f9d7c2b845e36e2177` |
| `student_market_street_v1` (`pedestrian_only_street`) | 18 m / 48 m | 6 / 16 | `81f6715283b740536795300e0a7860c9757dcab77b8c4044b1ed3d99b507b88a` |

The [machine-readable pilot manifest](../frontend/src/data/nativeStreetPilots.json)
locks the source recipe, preview assembly and reference image hashes, ordered
metric bands, axis, native module hashes/bytes/URLs, exact fixture poses, tree
wells and junction finish. Only separate origin-based modules and the locked
reference image are staged in `frontend/public/street-kits/pilots`; the preview
assembly remains external. The new asset path uses Git LFS. The candidate
staging script verifies source and staged bytes and refuses changed existing
deliverables. Its finite dry-run / pilot / second-candidate sequence was:

```powershell
python tools/public_realm_assets/stage_street_pilots.py --pilot C:/dev-artifacts/CityPrompt/streets-ten-2026-09-22/pilot/main_street --public-root frontend/public --manifest frontend/src/data/nativeStreetPilots.json --dry-run
python tools/public_realm_assets/stage_street_pilots.py --pilot C:/dev-artifacts/CityPrompt/streets-ten-2026-09-22/pilot/main_street --pilot C:/dev-artifacts/CityPrompt/streets-ten-2026-09-22/batch/market_street --public-root frontend/public --manifest frontend/src/data/nativeStreetPilots.json --dry-run
```

The full source aerials were visually reviewed before each stage. The first
stage surfaced a real omission: `reference_assets` listed only five specially
reviewed props, while `placements` held all 30 actual main-street modules. The
staging contract now uses and validates every `placements` entry. It requires a
matching native tree and grate for each hardscape well.

The source references identify the existing catalogue parents shown in the
table. These pilots are new exact model identities, not the parents' existing
visual `v0` cards. `backend/app/services/native_street_candidate_contract.py`
compiles each staged identity into a **review-only** Public Realm LEGO recipe:
the recipe binds the source, assembly, reference and every module SHA-256, plus
the exact ROW width. Its catalogue is constructed only when a caller explicitly
passes the manifest; it is excluded from the active capability catalogue and
AI prompt vocabulary. This makes the future compiler selection inspectable
without implying that the production renderer or student picker supports it.

## Reusable runtime seam

`nativeStreetPilot.ts` projects native-size modules along a centreline without
stretching the preview assembly. It repeats *individual modules* over longer
routes, samples route height, rotates components with the tangent and clears
furniture at bends and junctions. `streetSectionProfiles.ts` uses the authored
bands for a development-only road zone carrying `native_street_pilot_id` and
the exact metric width; `GlobeStreetDetailLayer` then renders the reimported
modules above those bands, while suppressing duplicate generic furniture.
The marker remains DEV-only, outside ordinary student controls and the
production renderer. The isolated browser review page is
`/native-street-pilot-review.html` from this worktree's Vite server.
The page now exercises a rounded main-street S bend and a rounded pedestrian
market turn through the shared [curved route contract](STREET_CURVE_GEOMETRY_2026-09-23.md).

This seam is the pattern for later street archetypes: preserve the source
image/recipe/model hashes, ordered full-width bands, physical model axes,
component poses and wells; reconstruct ground on the live route; keep rigid
modules at native scale; clear junction/turn envelopes; and bind any eventual
student selection to a server-verified recipe. A screenshot or GLB alone never
establishes that contract.

## Mixed street node pilot

The shared graph now accepts an exact development-only pilot as a contributing
route when its marker, width and catalogue parent agree. The market promenade
joins the candidate main street at T and X nodes, and also joins an existing
compiled main street. The section junction uses its central 5 m pedestrian
promenade as circulation, keeps the rest of the 18 m paved, and draws crossings
only on vehicle approaches. It never draws a zebra across the car-free market
route. The node has separate vehicle-asphalt and market-paver surfaces in
either axis order, so the market entrance does not turn into an asphalt patch.
Tests check one continuous T/X footprint, the real three-arm
closure, both axis orders and a car-free market-to-market crossing. The separate local
`/native-street-mixed-junction-review.html` page renders the actual graph-owned
surface and rigid modules with a T/X toggle; both views loaded without browser
console errors or warnings. This is still a local DEV graph/surface check;
the backend has not been taught to attest or export these candidate nodes.

## Evidence and remaining gates

- Narrow frontend tests: 67 passed for the pilot, street profile and graph.
  The subsequent mixed-junction suite passed 89 focused tests. Staging tests:
  4 passed. Candidate compiler tests: 2 passed. Frontend type check, touched-file ESLint and
  production build passed. Pilot main/market module and reference URLs returned
  HTTP 200 with expected byte lengths.
- The route review page loaded a 96 m main street (two component cycles) and
  bent pedestrian market street. Native modules, trees, grates, stalls and
  fountain were visible; browser console errors/warnings: none. The mixed T/X
  review also showed the market pavers meeting asphalt, two vehicle crossings,
  clear furniture and a closed fourth arm on the T. These reviews
  uses an isolated neutral scene, not Google Tiles or a saved Currie project.
- S1 metric sections are exercised locally. S2 is partial: bend/junction
  furniture clearance and mixed T/X graph surfaces pass focused tests, but
  live compiled/native node ownership and server proof have not passed. S3
  prepared/irregular Currie terrain and public-road endpoints remain untested.
  S4 tree-root, crossing and clearance detail in the live globe remains open.
- C1–C9, editing/Undo/reload/export, paid-image fidelity and novice picker
  usability have not been claimed for these variants. The worktree's port 5177
  opened the saved Currie URL at the sign-in page, so this checkpoint did not
  alter or certify the protected Currie project. No paid image calls were used.

## Next bounded integration

Add exact vehicular and pedestrian selections to the authoritative front and
backend Public Realm LEGO catalogues, with immutable module identity in the
saved recipe. Then make the shared graph own their mixed T/X crossings and
grade/endpoint contracts. Test one disposable copy of the vacant Currie parcel
through ordinary student controls: place both, connect to an existing compiled
street, move/bend, Undo/Redo, save/reload, free Direct 3D capture and actual
file export. Complete each exact-variant review form before changing status
from candidate to pilot in the student picker. Only then consider the other
eight reviewed street packages.
