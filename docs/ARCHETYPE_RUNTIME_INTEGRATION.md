# Runtime integration for every archetype

Version: 2026-09-20. Applies to every new or materially revised building,
street/path, and park/open-space variant intended for the student catalogue.
Read this before authoring the asset, not only when installing its picker card.

This is the shared runtime acceptance checklist. RLASM 6.1 remains the building
construction and visual-review authority. Existing catalogue publication,
independent review, and human activation requirements remain in force.
This checklist adds site integration evidence; it does not grant asset approval.
For variants within a shared parent, verify search opens the intended variant,
the housing-category filter includes it, and the displayed classification follows
the selected detailed model. Count and measure every intended public entrance;
multi-home models must not inherit a single detached-home entrance by default.
The [September 22 duplex checkpoint](CATALOGUE_RESTART_2026-09-22.md) records the
first local trial and the remaining multiple-entrance work.
The [Currie building/street/park rehearsal](CLASSROOM_CATALOGUE_ENTRY_REHEARSAL_2026-09-20.md)
is an example of recording classroom passes and explicit variant-specific gaps.
The [September 22 empty-lot catalogue trial](CURRIE_EMPTY_LOT_CATALOGUE_TRIAL_2026-09-22.md)
adds a mixed neighbourhood, a separate oversized-building parcel, residual
landscape, real download and paid-image review evidence.

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

### Site landscape compatibility

Every new building, street and park must work with the shared
[Generate 3D Site Landscape feature](SITE_LANDSCAPE_2026-09-20.md). Declare the
complete occupied plot and use the shared building-approach / park-access route
resolvers. Landscape masks subtract those plots and buffered route corridors;
do not bake a private ground sticker across neighbouring objects or access.
If a new property changes entrance position, route width, variant footprint or
park access, include it in landscape invalidation as well as route freshness.
For the first exact variant, verify preset Apply, move/route-edit invalidation,
Undo/Redo, reload and exact export. Custom images must use the authenticated
surface loader and capture readiness check; do not export a silent fallback.
Generated ground artwork is flat. New physical amenities still require their
own reviewed 3D geometry. Prepared-site validation does not establish support
for landscape surfaces on natural terrain.
Custom AI landscape must receive both the authoritative parcel template and
the real captured development with surrounding Google tiles. Reuse the shared
automatic context framing and camera restoration; do not substitute an empty
mask, catalogue photograph or generic location prompt for the scene reference.
Verify the new archetype is visibly represented in that reference and that
context generation retains its protected footprint and access routes.

### Common gates

| ID | Required behavior and evidence |
| --- | --- |
| C1 Identity | Picker, placed object, saved recipe, reopened project, and capture show the same exact variant. Keep stable saved IDs and old project bindings. Model/recipe changes invalidate affected evidence. |
| C2 Dimensions | Declare metres, axes, origin, base datum, full occupied footprint, rigid components, and allowed reshape behavior. Plot resize must not stretch a native house, regulation court, or fixed street section. |
| C3 Ground | Use current measured ground and complete footprint coverage, including disjoint pads and narrow/concave boundary crossings. Missing or partial support stays unresolved; do not invent heights or flatten the site to conceal failures. |
| C4 Freshness | Move/resize/rotate, variant/property edits, boundary/context changes, and tile refinement invalidate affected results. Late callbacks must not overwrite newer edits or restore deleted objects. Show a coherent draft or last safe proposal while pending. |
| C5 Circulation | Review actual model entrance → approach → sidewalk/crossing → park path continuity at pedestrian height. A connected plan line or supported foundation alone is insufficient. For a vehicular street, distinguish an internal route from a proposed public-road junction; check its endpoint against the real map and do not infer access from a marker alone. |
| C6 Editing | Place, select, move, supported resize/rotate, Undo/Redo, save/reload, and reopen preserve geometry and identity. Deleting/restoring a route target must not strand links by changing IDs. |
| C7 Recovery | Exercise unavailable measurement, interrupted navigation, and failed/conflicting saves. Keep the design editable, preserve drafts, bound retries, and provide an actionable recovery. Capture waits for current verified geometry. |
| C8 Visibility | Inspect low views from several directions plus aerial and exact 3D capture. No persistent proxy, duplicate surface, floating base, buried path, hidden gap, or furniture obstructing a route. Preserve surrounding context and capture ownership. When AI imagery is used, compare it with the exact same-camera source for count, location, outline, scale, function, access and invented elements; record automatic pass, human review or fallback. A visually attractive image alone is not faithful evidence. |
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

A park-specific repeatable profile does not certify the house, street, access
route or the rest of a hillside site. `terrain_strategy: landscape` keeps the
original tiles visible and must retain shared-site verification and capture
guards. The [natural Currie park check](CURRIE_NATURAL_PARK_CAPTURE_CHECK_2026-09-20.md)
shows a park moved onto clear ground while the site's eight uncertain cells and
house approach still block exact export. Review the programme at minimum size;
the supported 30 m park can omit its play equipment.

Ground-review problem markers must use the same slope and local-residual tests
as the actual ground validator, including boundary-support cells. A separate
fixed height-jump threshold can show an apparently clean map while rejecting
alignment. Offer boundary adjustment without silently preparing a level surface.
Boundary edits must preserve contained objects or explain how to move them first.
See the [fresh workflow pilot](CURRIE_STUDENT_WORKFLOW_PILOT_2026-09-20.md).
When an edit excludes an unnamed object, the server must identify its type,
ordinal and available variant/size in the rejection. Do not surface UUIDs as
the only recovery clue. Verify the failed edit leaves the saved boundary and
objects intact; see the [Currie label check](CURRIE_BOUNDARY_EXCLUSION_LABELS_2026-09-20.md).

For a native-house plot, verify that the visible Move handle actually moves the
selected plot, then Undo/Redo and reload it. Model-body dragging may pan the
camera; do not instruct students to use that gesture unless it is implemented
for the exact runtime. See the
[Currie control check](CURRIE_NATIVE_MOVE_CONTROL_2026-09-20.md).

When adding a building family, the visible Generate to 3D panel and atomic
Community 3D compiler must prepare the same locked plot recipe. Use the shared
request builder: `native_home_plot`, authored first-edge axes, explicit height,
metric target and the caller's fit policy are recipe inputs. Do not introduce a
second preview-only request that can pass planning but fail locked placement.
After generation, reload and wait for tile/model readiness before judging the
scene. See the [seven-house Currie repair](CURRIE_GENERATE_3D_RECIPE_REPAIR_2026-09-20.md).

For each pilot, test a level case, a slope, an edge/unsupported case with
recovery, and an edit while ground is pending. Keep the matrix finite. Shared
algorithm tests may be cited across candidates when the implementation is
unchanged, but new geometry/variant assumptions need their own runtime proof.
Do not transfer a model's visual approval or a different site's measured result.

Before scaling a catalogue batch, complete one mixed-scene project from an empty
project on visibly vacant land. Use ordinary student controls to place several
buildings plus a street/path and park/open-space object, then edit, Undo/Redo,
reload, apply residual landscape and download the free exact 3D export. Remove
unsupported fallback objects from the final evidence scene. Test an oversized
fixed-native candidate on a separate, appropriately sized vacant parcel and on
the terrain mode it advertises; never shrink it to make a residential pilot fit.

Collision preview, snapping and final placement must use the same complete
occupied envelope. If a nearby valid position exists, assisted placement should
offer or snap to it while preserving roads, approaches and existing objects.
Treat a hard rejection against an invisible plot envelope as a classroom defect
when the visible geometry appears clear; do not blame the student or weaken the
authoritative envelope to make the test pass.

Paid image generation needs a server-calculated preflight before the call. Show
the selected engine, exact credits to reserve, remaining balance and number of
calls beside the action. If the balance cannot fund the request, disable it with
clear recovery. Reconcile observed balance changes with the render audit record;
do not repeat paid calls while accounting is unexplained. A paid output still
requires the C8 same-camera fidelity comparison and explicit fallback/review
status.

Include an irregular development boundary when the real vacant parcel lies
between roads with different alignments. Trace the visible road edges with
ordinary site controls and record that the polygon is an approximation unless
surveyed. Test natural and explicitly prepared ground separately: a large
level prepared pad may expose a conspicuous boundary even when street contact
and exact capture pass. For a proposed public-road extension, verify the saved
endpoint against the map, Undo/Redo/reload, and the actual off-site surface at
low view. Do not infer that junction grade from a zone's stored point elevation;
the prepared renderer may use the active site level. The
[irregular Currie street pilot](CURRIE_IRREGULAR_STREET_TRANSFER_2026-09-20.md)
records this finite test and its still-open visual checks.
On prepared ground, the site surface may win the first 3D pointer hit over a
contained street. Re-select the street directly after reload, then select the
site elsewhere and return to the street; the smallest containing authored
zone should win without requiring the Layers panel. For a fixed street, test
the panel's Add bend point control, drag the new route point, and verify the
saved centreline, compiled identity and edit handles after reload. The Currie
second pass found and repaired the boundary picking overlap, and confirmed a
three-point route through ordinary controls. Keep junction grade and clearance
as separate checks.

In a mixed building/street/park pilot, verify connections twice: first the
plan-level building and park route, then the current 3D ground/entrance review
after saving. A plan-connected building route can still meet an obstruction at
the rendered step; adjust it through the UI and recheck instead of accepting
the line alone. Automatic park access may save no entrance anchor while its
derived path is connected, so inspect the resolved path to the sidewalk rather
than treating a null manual anchor as failure. Reload and download the free
exact 3D image, then judge the actual composition at both context and close
views. The [irregular mixed-scene prototype](CURRIE_MIXED_PROTOTYPE_2026-09-20.md)
records one finite example; its clay model and sparse pad do not transfer
visual approval to new variants.

Plain prepared boundaries use a shared grass finish by default; this represents
proposed ground cover, not the original Google texture. Authored park and
residual-landscape materials still own their surfaces. Keep appearance choices
independent of elevation, masking and contact checks. Check an immediate
post-reload capture as well as the settled scene: the grass follow-up in the
mixed-scene record exposed delayed street elevation that a late screenshot hid.

Prepared public-road extensions must seat inside pavement and furniture on the
known site datum immediately, while publishing pending status until the outside
centre and both edges have measurements. Reuse the street readiness guard for
early capture and recheck it before releasing output; a screenshot fallback must
not bypass an unfinished alignment. Reset the sampler after route, boundary or
level edits. The [Currie loading/export repair](CURRIE_STREET_LOADING_EXPORT_2026-09-20.md)
records both a held-terrain test and an immediate UI export after a fresh load.

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

For reusable placeholder vegetation, use `GlobeLandscapeTreeStand` and its
metric species profiles. The [lightweight crown recipe and Currie check](LIGHTWEIGHT_TREES_2026-09-20.md)
describe a branching-crown pilot awaiting user visual acceptance; palms and park-owned GLB trees remain separate
visual checks. Inspect overhead and oblique silhouettes as well as pedestrian
clearance; flat crossed sheets can pass one camera while failing another.

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
If repeated measurements cannot cover a park, the terrain option stays disabled
and natural mode may hide the whole unsupported assembly. Test the visible
move/resize and deliberate prepared-level recovery before claiming student use.
Do not release a partial-site capture until every rendered park surface, object
and route has current complete support; the existing capture guard rejects the
whole partial snapshot. See the
[fresh Currie park check](CURRIE_PARK_GROUND_RECOVERY_2026-09-20.md).

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

**Prepared-site public connections:** whole-site clearing must also retain each
supported outside street footprint in the live tile shader. Use only constructed
bands, preserve setbacks, and open the measured site retaining face through that
same footprint. Road side/end transitions must use real cross-section samples.
Check the endpoint against the visible existing road from above and from inside
the site at low height; a ready flag or an endpoint outside the parcel is not
proof that it reaches the road. Test route Undo/Redo and reload. Reapply free
landscaping after route edits when the current workflow clears its prior layout.
Download verification on Windows must use a native Windows browser download
directory and the actual link; compare saved bytes with the preview. See the
[ground/export continuation](CLASSROOM_GROUND_EXPORT_2026-09-22.md).

**Catalogue entry defaults:** start adaptive parks at the recommended programme
size; keep compact minima as explicit resizing choices. Readiness text must
describe the renderer actually selected by the exact variant/revision, including
explicit adaptive layouts when the backend records a pending external family.
Do not silence warnings for unrecognized siblings. For one fixed-native building,
measure the native entrance/apron and bind it to the exact asset revision; a larger
plot must not move the entrance away from the unscaled model. Do not transfer that
contract to repeated houses. Verify both street sides and resize/Undo/reload.
See the [Beltline/local-street/garden pilot](CLASSROOM_CATALOGUE_PILOT_2026-09-22.md).
Test the actual download action separately from preview generation and valid PNG
bytes; saving the preview's data URL is not a download-button pass.

**Continuous landscape base:** new custom artwork lives beneath the authored 3D
objects, with GPT Image 2.5 as the landscaping default. Keep object surfaces and
depth ordering authoritative; do not introduce per-archetype cutouts into the base.
Continue using complete plots and access corridors for tree placement clearance.
Verify the surrounding-tile colour blend, loading, Undo/Redo and exact export for
each new archetype. Colour blending cannot close a ground-height gap; check that
separately. See [the live base pilot](SITE_LANDSCAPE_BASE_PILOT_2026-09-20.md).

**Ideation interaction contract:** normal building placement must settle into
nearby valid space rather than ask the student to repair an overlap. Protect
existing sidewalks and entrance routes while snapping; verify preview/drop
agreement and a single reversible move. Default entrance connections should
follow the nearest supported sidewalk using the exact variant's reviewed native
entrance. Register this with the placement asset, including supported dimensions;
do not send students to coordinate fields for each ordinary placement. Test
both street sides, existing mapped proposed roads, route changes and Undo.
Manual choices must remain available and preserved. See
[the snapping pilot](IDEATION_SNAPPING_2026-09-20.md) for the initial supported
infill, shared solver, acceptance evidence and remaining catalogue coverage.

For repeated placements, test the same native building on **both sides of a bent
street**. Verify the actual entry-facing geometry and the Place another behavior;
an enabled street-facing control or a prior house's rotation is insufficient.
An entrance should be authorable from visible geometry without trial-and-error
developer coordinates. Preserve failed pick/gap evidence, count manual adjustments,
and distinguish an assisted functional pass from independent novice usability.
The [Currie seven-home student exercise](CURRIE_STUDENT_NEIGHBOURHOOD_2026-09-20.md)
passed save/reload/exact export but exposed this remaining entrance-placement
friction. Its measured anchors must not become defaults for other variants.

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

When students are unavailable, a UI-only agent exercise may be a provisional
prototype checkpoint, explicitly labelled as simulation. Start from an empty
project; record unsuccessful placements, save waits and ordinary recovery, not
only the finished scene. Explain prerequisites using the controls' actual names
(for example, Clear site for redevelopment before landscape presets). Read-only
API comparisons can verify persistence, but API-authored geometry does not count
as student authoring. This changes neither per-variant visual approval nor
publication rules. See `SIMULATED_STUDENT_EXERCISE_2026-09-22.md`.

Keep heavyweight screenshots, models and browser scripts external. Commit the
concise review, exact hashes, durable evidence references, limitations and
next action. Local-only paths are not a collaborator-accessible evidence backup.
Do not mark historical candidates passed retroactively: review changed assets
and integrations explicitly before advertising those capabilities.

For park/street visual work, review native Google Tiles close and aerial views
before AI enhancement. Use metric paving detail and restrained edging rather
than diagram-like outlines. Specify botanical height independently of its
placement footprint; retain path/prop clearance and full-footprint terrain
support. Bound instance counts and texture size per exact variant. The
[public-realm pilot](PUBLIC_REALM_VISUAL_PILOT_2026-09-22.md) records reusable
opt-in geometry, prepared-ground behavior and limits; it is not approval for
other variants.

For replacement furniture, prove that the complete new mesh stays inside the
existing placement envelope, with feet at the shared metric datum. Use batched
geometry and retain the same yaw, scale and support offsets. An exact variant's
reviewed replacement must not silently change when a global legacy-asset flag
is enabled. Review isolated components as well as their actual Tiles placement;
an isolated kit image cannot establish site support. See the
[meadow furniture review](MEADOW_FURNITURE_REVIEW_2026-09-22.md).

For a vegetation kit, record the full canopy envelope and per-prototype triangle
budget, not only a trunk footprint. Test deterministic geometry across several
seeds and review it beside real-scale furniture. Curved grass blades need narrow
segments along their centreline; a single spanning triangle can become a broad
spear. Component appearance does not establish terrain support or route/entrance
visibility; see the [meadow vegetation kit](MEADOW_VEGETATION_KIT_2026-09-22.md).

When integrating replacement vegetation, preserve support/transforms and fit
the full crown to the parcel and fixed program reserves; use a narrower type
or omit an edge candidate rather than silently miniaturizing it. Fit replacement
low planting inside the existing clump reserve. Keep exact-variant opt-in.
Compare close-up AI finishes with the exact capture: pale prepared-site edges
can become invented water. Keep failed originals explicitly unverified, and
reconcile charged audit rows against any weekly balance reset. See the
[Currie vegetation trial](MEADOW_VEGETATION_SITE_TRIAL_2026-09-22.md).

For offline park batches, export the actual shared kit with its metric geometry
and linear vertex colours. Consolidate static details by material and retain
shared mesh instances. Deliver rigid native modules separately from the level
assembly preview, plus surface ownership and placement recipes. Verify walking
corridors against the reimported GLB's surface material and obstruction height;
put sports entries beside, not behind, goals. Full view framing must account
for render aspect ratio. See [sports/garden assets](SPORTS_GARDEN_ASSET_BATCH_2026-09-22.md).

For straight street assets, check the full walking width and seating-bay links,
not just the corridor centreline. Ground ownership regions must meet without
thin lawn gaps. Orient cycle stencils along travel and verify both directions
against the intended local traffic convention. These offline checks complement,
but cannot replace, bent-route and real-road connection trials. See
[planted street assets](PLANTED_STREET_ASSET_BATCH_2026-09-22.md).

Keep sky colour separate from missing terrestrial context. A grass fallback
must be non-pickable ground/context geometry, never the global scene background
or a source of terrain/support samples. Verify sky and ground simultaneously in
an oblique editor capture. Preserve original generation inputs when recapturing
after a visual fix. Native-size DEV asset trials on prepared ground do not prove
student authoring or street connectivity; see the
[Currie close-up review](CURRIE_PUBLIC_REALM_CLOSEUPS_2026-09-22.md).
