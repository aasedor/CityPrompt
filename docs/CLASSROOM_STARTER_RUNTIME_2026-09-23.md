# Classroom starter integration checkpoint — 2026-09-23

Scope: the nine exact entries and 47 byte-locked dependencies in
`seed/classroom-release/starter-v1.json`. This is local implementation evidence,
not publication approval, hosted verification or independent novice usability.

## Implemented

- The catalogue opens on three buildings, three parks and three streets.
  Explore more preserves the existing catalogue and labels it exploratory.
- New infill and bungalow placements use one native home. Saved repeated-home
  plots retain their old interpretation, including the infill's 15 m minimum.
  Fixed-native automatic entrances carry their source revision and remain
  attached to the building when the surrounding plot grows.
- Main Street (`student_main_street_v1`, 23 m) and Market Street
  (`student_market_street_v1`, 18 m) now compile through the backend catalogue.
  Their server recipes pin the profile, revision and every module hash. The
  production frontend validates those locks before loading native modules.
  Shared curved routes, furniture clearance, terrain and capture ownership
  remain the existing implementation. DEV-only pilot markers are not activation.
- Street settings retain native variant and width, including unchanged Apply.
  Type changes preserve the route and request a fresh server recipe.
- Endpoint assistance supports 45–135 degree approaches with width-dependent
  clearance. Real axis intersections take precedence over nearby sampled-point
  projections. Sub-metre terminal gaps can join only when their approach axes
  intersect accurately. Section streets never receive legacy crossing overlays
  when the full junction surface cannot be resolved.
- The deployment asset inventory includes native street and sports modules and
  every public dependency explicitly listed by the classroom roster. Sparse
  metadata checking is distinct from actual release hydration.

## Exact entrance evidence

The postwar bungalow is `bungalow_postwar_ranch`, clay-v005, SHA-256
`f601299cdb32072119e5484fe3206ddc4aa2263e88cea703a79158f018238153`.
Its authored porch/stairs are centred at X=-0.15 m, with four 0.29 m treads;
the outer toe is Y=-8.665 m. The delivered GLB horizontal bounds are
X=[-5.430000305,5.468323708], Z=[-7.385000229,8.664999962]. Applying the same
horizontal recentering and front-axis mapping as `centreNativeClayClone` gives
the runtime anchor X=-0.169161701, Y=-8.025 m; clear width 1.4 m. This is an
approach at the stair toe, not the door. Reference plot: 15×20 m, unscaled.
The authored evidence remains in the existing external ranch-v005 build script.
Source/geometry tests pass; final live entrance/grade/capture acceptance remains open.

## Bounded live evidence

Local browser, existing disposable Currie curved-street trial, 2106×1272 viewport,
Windows desktop, ordinary UI actions. Project:
`http://127.0.0.1:5178/projects/81da9efb-43bc-4a3f-8bf2-98d86126c50b`.

- Loaded all three starter building cards and all three street cards with images.
- Drew a three-control-point Main Street in vacant space, joined it to the curved
  local street, and inspected the close T-junction. Three connected approaches,
  clipped sidewalks, crossings, native furniture and tree wells were visible.
- Undo removed it; Redo restored it; reload retained the route and native models.
  The edit panel read the actual 23 m width and native variant.
- Changed that same route to the 18 m Market Street. Paving, stalls, tables,
  umbrellas and fountains loaded; the promenade did not acquire a vehicle zebra.
  Vehicle-road crossings remained. Local screenshot:
  `artifacts/classroom-runtime/market-junction.png` (ignored).
- Removed only the temporary test streets afterward. Existing buildings, roads,
  park and boundary were preserved. No paid image request; balance stayed 14.

The first placement exposed a genuine unsupported short-arm crossing near a
street end. It remains a retained regression fixture, not a claimed pass.
Sliding that particular endpoint would require changing another control point
and making an acute approach. The tool leaves the authored gesture intact and
does not fabricate crossing geometry. Guidance now asks for space away from
bends/endpoints. General arbitrary-angle, tight-bend and short-arm repair remains
outside the supported starter junction envelope; its usability is still part of
the final rehearsal. A second regression fixture checks the older Currie T's
sub-metre endpoint gap without changing its stored geometry.

## Verification and remaining gates

- 341 frontend tests across 40 relevant files pass.
- 166 backend catalogue/native/home tests pass; ten roster tests pass.
- TypeScript check passes.
- Exact starter preflight: 47/47 local files verified.
- Full inventory metadata: 4,480 required files recorded; missing/pointer assets
  are explicitly not called hydrated. Release hydration is a separate gate.

| Exact starter group | Evidence | Still open |
| --- | --- | --- |
| Native Main / Market | Compiler parity, production recipe validation, live curved T, swap, Main Undo/Redo/reload | Low grade, native mixed X in final scene, capture ownership/export, failure/recovery, full release matrix |
| Calgary Local | Existing trial plus repaired live angled T | Final mixed starter rehearsal and public-road grade |
| Infill v006 / bungalow v005 | Single-home compilation, legacy preservation, measured entrance metadata and resize/revision tests | Fresh single-home placement and entrance/grade/export review |
| Beltline / three parks | Existing asset records retained and exact dependencies verified | Current integrated rehearsal; no new visual readiness claim |

All unlisted applicable gates from `ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md` remain
NOT TESTED for this release revision. Building-specific gates do not apply to
streets; street-specific gates do not apply to buildings/parks. The roster's
release status intentionally remains integration-in-progress.
