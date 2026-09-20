# Runtime integration for every archetype

Version: 2026-09-20. Applies to every new or materially revised building,
street/path, and park/open-space variant intended for the student catalogue.
Read this before authoring the asset, not only when installing its picker card.

This is the shared runtime acceptance checklist. RLASM 6.1 remains the building
construction and visual-review authority. Existing catalogue publication,
independent review, and human activation requirements remain in force.
This checklist adds site integration evidence; it does not grant asset approval.

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
   Keep failed or untested applicable checks open; do not describe the candidate
   as student-ready. Scale only after the pilot's applicable checks pass and
   the existing publication requirements are met.

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
