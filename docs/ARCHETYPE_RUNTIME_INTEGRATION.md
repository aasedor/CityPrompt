# Runtime integration for every archetype

Version: 2026-09-20. Applies to every new or materially revised building,
street/path, and park/open-space variant intended for the student catalogue.
Read this before authoring the asset, not only when installing its picker card.

This is the shared runtime acceptance checklist. RLASM 6.1 remains the building
construction and visual-review authority. Existing catalogue publication,
independent review, and human activation requirements remain in force.
This checklist adds site integration evidence; it does not grant asset approval.

## Classroom acceptance scope

The user clarified the release target on 20 September: students must be able to
create their own designs and strong visuals without glaring errors. Prioritize
usable authoring, faithful identity and scale, plausible ground/connections,
recoverable edits and presentation. Fine railing joins, construction detailing,
comprehensive accessibility assessment and exhaustive edge cases are follow-up
work unless an advertised classroom feature depends on them. Do not imply code
compliance or hide a visible defect. This clarification changes prioritization;
it does not grant catalogue publication or RLASM asset approval.

Classify each open finding as a classroom blocker or a recorded follow-up.
Minor concept limitations do not automatically prevent a classroom pilot or
bounded catalogue expansion. Missing models, impossible access, lost edits,
unusable advertised controls and misleading captures remain blockers. See
[the practical readiness plan](CLASSROOM_READINESS_PLAN_2026-09-20.md).

## Use on every delivery

1. Copy [the review template](ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md) into the
   candidate's evidence package. Identify the exact archetype, variant, model
   hash or procedural recipe revision, and runtime source commit.
2. Define supported plot sizes, transformations, terrain modes, and connection
   behavior before building. Record unsupported cases explicitly. Do not expose
   a control whose output the runtime cannot render and validate.
3. Reuse the shared implementations below. Fix a reproduced general defect in
   the owning shared module with a regression; do not fork terrain or route
   logic for each archetype, bake in Currie offsets, or relax checks to pass.
4. Dry run, install one isolated local pilot, then inspect it in a disposable
   vacant-site project. Use the protected vacant Currie layout as a reference;
   use copies for edits. Choose another genuinely vacant, appropriately sized
   site if the archetype cannot fit Currie. Preserve occupied-land exclusion.
5. Record PASS, FAIL, NOT TESTED, or N/A for every applicable check. PASS requires
   evidence; N/A requires a reason tied to the advertised capability. A missing
   advertised feature is a failure or untested item, never N/A.
6. Include the completed record in the delivery/PR alongside asset review.
   Keep failed or untested applicable checks open with their classroom impact.
   Scale only after classroom blockers are resolved, remaining limitations are
   recorded, and the existing publication requirements are met.

These are contributor and reviewer requirements. The existing publication CLI
does **not** yet enforce this whole checklist. Its success does not establish
these checks passed. The review template is evidence, not a runtime schema.

## Shared requirements

| ID | Required behavior and evidence |
| --- | --- |
| C1 Identity | Picker, placed object, saved recipe, reopened project, and capture show the same exact variant. Keep stable saved IDs and old project bindings. Model/recipe changes invalidate affected evidence. |
| C2 Dimensions | Declare metres, axes, origin, base datum, full occupied footprint, rigid components, and allowed reshape behavior. Plot resize must not stretch a native house, regulation court, or fixed street section. |
| C3 Ground | Use current measured ground and complete footprint coverage, including disjoint pads and narrow/concave boundary crossings. Missing or partial support stays unresolved; do not invent heights or flatten the site to conceal failures. |
| C4 Freshness | Move/resize/rotate, variant/property edits, boundary/context changes, and tile refinement invalidate affected results. Late callbacks must not overwrite newer edits or restore deleted objects. Show a coherent draft or last safe proposal while pending. |
| C5 Circulation | Review actual model entrance → approach → sidewalk/crossing → park path continuity at pedestrian height. A connected plan line or supported foundation alone is insufficient. |
| C6 Editing | Place, select, move, supported resize/rotate, Undo/Redo, save/reload, and reopen preserve geometry and identity. Deleting/restoring a route target must not strand links by changing IDs. |
| C7 Recovery | Exercise unavailable measurement, interrupted navigation, and failed/conflicting saves. Keep the design editable, preserve drafts, bound retries, and provide an actionable recovery. Capture waits for current verified geometry. |
| C8 Visibility | Inspect low views from several directions plus aerial and exact 3D capture. No persistent proxy, duplicate surface, floating base, buried path, hidden gap, or furniture obstructing a route. Preserve surrounding context and capture ownership. |
| C9 Student use | Complete the advertised placement/connection workflow through ordinary controls, without API-authored geometry or numeric offsets supplied by a developer. Check keyboard, pointer, and supported viewport behavior; report touch separately if not tested. |

For local natural-ground recovery, a ready interactive snapshot may include
`excludedCells`. All variants must use shared `heightAt` and reject null throughout
their footprint/face; never interpolate `snapshot.heights` directly, span an
excluded cell using distant corners, or substitute a stored/frame elevation.
`contains` indicates boundary ownership, not verified support. Preserve local
holes when extending/reusing ground, and include coverage in freshness identity.
Captures currently reject any partial snapshot. A ready interactive status is
not sufficient export evidence. Test both an unaffected placement and an affected
placement, plus recovery, reload and capture rejection. See the bounded
`CURRIE_LOCAL_GROUND_RECOVERY_2026-09-20.md` evidence; do not inherit its visual
acceptance for a new archetype.

Ground-review problem markers must use the same slope and local-residual tests
as the actual ground validator, including boundary-support cells. A separate
fixed height-jump threshold can show an apparently clean map while rejecting
alignment. Offer boundary adjustment without silently preparing a level surface.
Boundary edits must preserve contained objects or explain how to move them first.
See the [fresh workflow pilot](CURRIE_STUDENT_WORKFLOW_PILOT_2026-09-20.md).

For each pilot, test a level case, a slope, an edge/unsupported case with
recovery, and an edit while ground is pending. Keep the matrix finite. Shared
algorithm tests may be cited across candidates when the implementation is
unchanged, but new geometry/variant assumptions need their own runtime proof.
Do not transfer a model's visual approval or a different site's measured result.

## Buildings

| ID | Required integration |
| --- | --- |
| B1 Native placement | Record the actual transformed envelope and all support pads. Preserve native scale and authored frontage through full-turn rotation and supported plot resize/repetition. Test minimum and maximum advertised plot sizes. |
| B2 Entrance evidence | Measure and record the visible door, lowest authored step/landing edge, native coordinate frame, base datum, width, and route direction for each supported entrance. Tie measurements to exact asset bytes and evidence views. Do not copy another variant's anchor. |
| B3 Authoring | For supported native-house picking, test visible low-step selection, wrong-house/high-surface rejection, foreground occlusion including transparent foliage, camera drag, Escape/Cancel, preserved unsaved settings, explicit Save, and reload. Exact offsets remain an alternative; do not claim automatic door detection. |
| B4 Approach | Reserve the level building landing before sizing the stair flight. Check native steps meet it and every landing/tread clears measured terrain without crossing another pad or obstacle. Exercise a route that fits bare stairs but not the landing, then recover by moving the plot. Test descending as well as raised routes where supported. |
| B5 Architectural review | Inspect exposed foundation height, stair length, landings, guards, route width, accessible alternatives, and frontage furniture. Ground-ready status and current concept stair limits do not establish accessibility or construction suitability. Record unresolved design items. |

Natural ground and explicit prepared ground must use the surface actually
rendered under the native pads. A prepared site's authored boundary and level
supply interactive contact and 3D picking; it does not require a live Google
snapshot. Review revisions must match that boundary and level. Export must check
unresolved entrance issues in both modes. Test an actual low-step pick, rejected
stale/mismatched ground, and a complete route on the exact new variant. A valid
step pick may still yield an unresolved route if the door faces away from its
sidewalk. See `CURRIE_PREPARED_ENTRANCE_2026-09-20.md`.

If one model has both front and rear low steps, test both picks against the
selected sidewalk. Street-facing placement is an initial orientation; the
rendered step and route solver decide whether the connection works. A rear pick
must explain the facing problem and leave the saved front connection intact
when canceled. Record both entrances per exact variant in B2 evidence. The
[fresh Currie route pilot](CURRIE_STUDENT_ENTRANCE_ROUTE_2026-09-20.md) verifies
this shared recovery without variant-specific offsets in the solver.

Current saved entrance data is `pedestrian_building_entrance` version 1 in
plot properties: `xM`, `yM`, `referenceWidthM`, `referenceDepthM`,
`scaleWithPlot`, `streetId`, `widthM`, and optional `heightAboveBaseM`.
Use the existing parser and transformations rather than duplicating these rules.
For unscaled native houses, offsets normally stay unscaled. Height is measured
above the rendered building base, never multiplied by plot size.

The current direct-pick pilot requires a rectangular `native_home_plot` and a
native clay model hit. It snaps a manually chosen low surface to a nearby pad
edge, then checks the current route. It does not prove that the selected point
is a door. Imported models, multiple entrances, and one independently connected
entrance per repeated house are not established by this pilot. Do not set
`native_home_plot` just to expose the button on an incompatible asset. Extend
and test the shared integration when a new archetype needs those capabilities.
Measured entrance evidence is presently a review record; there is no automatic
catalogue entrance-metadata importer in this checkpoint.

Native steps may be merged into a stone mesh, a foundation mesh, or another
material group. Preserve the real transform and surface hit; do not identify
entrances from mesh names. Record both the lowest tread top and the outer
step-foot/base datum so the generated approach does not acquire a duplicate
rise. The [Craftsman/Edwardian pilots](CURRIE_ENTRANCE_FAMILY_PILOTS_2026-09-20.md)
verify this distinction with actual model bytes and browser edits.

The shared approach currently reserves a 1.2 m building-end landing for rises
over 0.04 m, then sizes the flight with 0.28–0.40 m concept goings and up to
0.18 m rise per step. Remaining street-end space stays level; nearly level
connections remain walks. These are display-layout choices, not construction
or accessible-route certification. Each landing uses the same complete-footprint
terrain checks as the treads. A previously ready route can become unresolved
when its landing will not fit; retain the saved anchor, explain the failure,
and verify move/Undo/Redo/reload recovery. Inspect high and low rises separately.
See the [landing pilot](CURRIE_ENTRANCE_LANDING_PILOT_2026-09-20.md).
Review guards, structural support, exposed foundations and accessible alternatives
separately; do not transfer a clear solver issue list into B5 approval.

The [side-detail pilot](CURRIE_ENTRANCE_EDGE_PILOT_2026-09-20.md) adds concept
side rails and measured landing posts in the shared approach. Rails stay inside
the validated corridor and reserve 0.08 m on each side; check usable width, not
only total width. Both route ends must stay open. Landings/posts need measured
footprint coverage, including sloped post feet; do not guess a flat support
plane or extend accessories outside an already validated envelope. Check every
detail's capture ownership and retirement when a route becomes unresolved.
Native steps and exposed foundation edges outside the approach remain separate
review items. Do not infer complete edge protection from the added rails.

The [entrance review panel pilot](CURRIE_ENTRANCE_REVIEW_PILOT_2026-09-20.md)
exposes actual approach step count, signed rise, clear width and maximum foundation
support height per saved plot. Use detailed rendered measurements tied to the
current verified surface. Display ground may retain geometry during tile refresh;
its revision format differs from verification. Match snapshot source/signature,
then publish the verification revision. Hide measurements while pending, obsolete,
unloaded or blocked; never turn absent evidence into a pass. Exercise the visible
review → select plot → Connections → edit → Undo/Redo/reload journey.

The runtime's whole-model support envelope is conservative, not evidence of an
authored terrace or pedestrian area. Do not auto-rail its perimeter or claim its
edges are usable without exact-variant evidence. Keep native-step joins, rail ends,
furniture and step-free access to the actual door open independently of a nearly
level generated approach. Review/export UI must preserve this distinction for
future building, street and park connections; it does not grant asset approval.

Entrance-only edits must update runtime geometry without recompiling native
houses. `useAutomatic3D` excludes `pedestrian_building_entrance` from its rebuild
trigger, matching the backend building-source contract; its full authored-state
comparison still protects revision tracking. Exercise Save/Undo/Redo/reload
with unchanged model markers and no model plan/place requests. Keep genuine
footprint/variant edits on the compilation path. This distinction is required
when extending runtime details to future archetypes; do not blindly exclude
other properties that may be actual compiler inputs.

## Streets and paths

| ID | Required integration |
| --- | --- |
| S1 Section | Use the authoritative metric section: total width, ordered bands, curb/flush treatment, sidewalks, cycling and planting. Verify asymmetric and reversed sections. Fixed sections keep their width while their route changes. |
| S2 Network | Test straight and bent routes, advertised junction types, endpoint connection, crossings and curb openings. Surfaces must join without overlapping pavement or sealing a pedestrian route. |
| S3 Shared grade | Connect building/park approaches to the actual pedestrian band and measured elevation. Public-road extensions use the existing bounded outside-site validation and measured extension; never enlarge the whole site to pass. |
| S4 Clearance and identity | Keep trees, benches, signs and planters out of approaches, junctions and crossings. Detailed geometry owns the visible surface; editor hit targets must not appear in the scene/capture. Preserve target IDs through delete/Undo. |

Do not assume every section has a raised sidewalk. Flush shared streets and
paths must use their actual section semantics. A mapped public route is context,
not proof of precise curb height or safe pedestrian access.

## Parks and open spaces

| ID | Required integration |
| --- | --- |
| P1 Program | Preserve exact variant topology, connected paths, gateways, amenities and metric envelopes. Rigid equipment and courts remain rigid; terrain-following landscape does not bend them. Declare incompatible footprints. |
| P2 Terrain | Supported lawns, paths and details use the same current measured triangles. Do not place the whole park on a flat table to hide a slope. Preserve explicit prepared-site choices and clearly identify modes the variant supports. |
| P3 Remeasurement | Supported move/resize/rotate remeasure automatically with bounded work. Retired samples after edits, delete, pause/resume, or navigation cannot write back. Background saves preserve current properties and Undo history. |
| P4 Access | Test gateway-to-internal-path and gateway-to-street connections at ground level. Missing or unsuitable connections stay unresolved. Review bridge/pad edges, furniture clearance and route grades separately from landscape slope acceptance. |

Neighbourhood-park terrain behavior is not automatically inherited by every
new open-space recipe. Register the actual geometry with the shared terrain and
access systems, or document the unsupported capability until integration passes.

## Shared implementation map

Paths below are relative to `frontend/src/`. Read their focused tests too.

| Concern | Existing implementation |
| --- | --- |
| Ground selection, measurement, freshness | `components/viewer/globe/SharedSiteGroundProvider.tsx`, `sharedSiteGround.ts`, `sharedGroundSelection.ts` |
| Complete building support and approach | `components/viewer/globe/buildingGroundContact.ts`, `buildingEntranceApproach.ts`, `BuildingEntranceApproaches.tsx` |
| Entrance state, route and picking | `features/pickPlace/pedestrianConnections.ts`, `ConnectionEditor.tsx`, `pickBuildingEntrance.ts` |
| Native model surface hits | `components/viewer/globe/GlobeLegoAssemblyLayer.tsx`, `GlobeSitePlannerMap.tsx` |
| Street section and terrain | `components/viewer/globe/streetSectionProfiles.ts`, `streetSharedGround.ts`, `streetGroundExtension.ts` |
| Park measurement and persistence | `components/viewer/globe/AutomaticParkGround.tsx`, `parkTerrain.ts`, `features/pickPlace/saveAutomaticParkGround.ts` |
| Park access | `components/viewer/globe/parkAccessConnections.ts`, `parkAccessBridgeGeometry.ts` |
| Capture gating | `components/viewer/globe/sharedGroundCapture.ts`, `streetGroundCapture.ts`, `pedestrianCapture.ts` |

## Evidence and maintenance

The [Currie 3D-picking pilot](CURRIE_3D_ENTRANCE_PICK_BROWSER_QA_2026-09-20.md)
passed on one modern infill. The [seven-house review](CURRIE_SEVEN_ENTRANCE_BROWSER_QA_2026-09-20.md)
established connected routes in one disposable layout; high foundations,
stairs and accessibility remain open. Read the [grounding continuation](CURRIE_GROUNDING_CONTINUATION_2026-09-19.md),
[park race handoff](GROUNDING_EDIT_RACE_HANDOFF_2026-09-19.md),
[automatic park alignment](AUTOMATIC_PARK_GROUND_2026-09-07.md), and
[street junction pilot](STREET_JUNCTION_GROUNDING_PILOT_2026_09_07.md) for the
specific failures and bounded evidence behind these requirements.

Every subsequent generalizable finding must update this checklist and its
template in the same coherent change, with the reproducer/regression and
evidence link. Keep site measurements in the candidate report, not shared
defaults. If the RLASM method or executable building-quality rules change,
update their human and machine companions together under their existing policy.
Do not silently turn a runtime checklist into a new building method.

Keep heavyweight screenshots, models and browser scripts external. Commit the
concise review, exact hashes, durable evidence references, limitations and
next action. Local-only paths are not a collaborator-accessible evidence backup.
Do not mark historical candidates passed retroactively: review changed assets
and integrations explicitly before advertising those capabilities.
