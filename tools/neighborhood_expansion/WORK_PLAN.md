# Twenty more neighbourhood buildings

The user authorized twenty additional normal everyday buildings on 2026-10-03,
to be built while they are away. This continues the local school/fourplex
prototype work. Do the work autonomously within this finite scope; do not ask
again for routine design/build/review steps or publish anything.

## Resume locations

- Worktree: `C:/Users/andre/.codex/worktrees/neighborhood-refinement/CityPrompt`
- Branch: `codex/neighborhood-refinement`
- Base source checkpoint: `3ea075106ce4f6595b5f82fe4f7bb1e1988954bb`
- Live progress: `C:/dev-artifacts/CityPrompt/neighborhood-expansion-20-2026-10-03/progress.json`
- Source batch manifest: `tools/neighborhood_expansion/batch-20.json`
- Prior reusable helpers and browser/check scripts: `tools/neighborhood_refinement/`
- Prior reviewed models: `C:/dev-artifacts/CityPrompt/neighborhood-refinement-2026-10-03`
- Preserve the prior preview on port 5201 and the unrelated process on5202;
  use port5203 for this batch (5202 was already occupied).

The main checkout and original neighborhood-essentials worktree contain unrelated
pending user work. Do not edit, stage, clean or reset them. All heavyweight output
goes under the new external batch root. New source images belong in that root's
`reference-repo/frontend/public/archetypes/buildings/<family-slug>/` tree. Record
the exact root and authority in each manifest; never use legacy image folders.

## Fixed scope

Exactly 20 variants are enrolled: three schools, three childcare centres, three
fourplexes, four sixplexes, three branch libraries and four community halls.
Their original briefs are copied into the batch manifest. Exclude the already
built school/fourplex and the childcare/library beneath housing variants.
`childcare_garden_pavilion` is the representative pilot. After it passes the
local independent architecture/walking review, advance in finite groups of four
(the final group may be smaller), with a checkpoint after every candidate.

The user's request authorizes this bounded expansion following the prior visible
pilots. Human catalogue/publication approval is still absent. No external paid
image API is authorized; use the built-in image generator for required original
designs and source-conditioned derivatives. Use one call per asset, preserve
prompts, inputs, output paths and hashes. Do not replace a failed built-in call
with a paid CLI/API. Existing exact compatible source pixels can be reused.

## Execution

1. Read repo instructions, the RLASM skill and canonical v6.1 method/policy/memory.
   Check git status and progress; resume an existing render/job before starting
   anything new. Never run duplicate work against one candidate.
2. Establish each variant's own front, compatible oblique and roof/top references.
   Inspect them, record inferred rear/program decisions, and lock exact hashes.
   The 20 briefs are design intent, not pixel proof. Do not model before locking
   a coherent source set. Preserve rejected source attempts separately.
3. Write the dimensions, plan/roof graph, wall/opening schedule, room programme,
   circulation, landscaping, material authority and complete camera roster.
   Reuse low-level geometry helpers, not a universal recoloured building shell.
4. Build a complete editable scene and exact GLB with native walking metadata.
   Furnish program-specific rooms. Fourplex/sixplex dwelling counts stay exact;
   provide kitchens, bathrooms, beds and connected stairs. Civic buildings need
   their actual reading/play/meeting/classroom uses and relevant outside spaces.
5. Exercise the app's actual walking solver plus real-GLB physical path checks.
   Test entry, every occupied floor, meaningful room routes and furniture
   exclusions. Add threshold/body-clearance checks before final rendering.
6. Render every mandatory view from the exported/reimported GLB, with source and
   phone boards. Inspect the full set. Fix nonarchitectural QA-light reflections
   early instead of repeating the old blown-white pane artefacts.
7. Use a separate independent RLASM verifier, as explicitly required by the skill.
   Builders cannot self-approve. Review every required view and source. A local
   architecture/circulation pass and full textured-keeper assessment are separate.
   Keep every real limitation visible; never relabel a scoped pass as a keeper.
8. At most three repair versions per candidate in one pass. If still failing,
   preserve the blockers and move to another queued item instead of looping.
   Revisit held items only with a concrete new correction and finite next pass.
9. Verify passing candidates in the isolated browser inspector, including model
   load/switch, actual embedded walking, interior/exterior views, reload and
   visibility toggle. Save browser screenshots and readable evidence.
10. Save candidate lifecycle, exact hashes and progress after every material step.
    Keep `progress.json` and the source manifest synchronized at checkpoints.
    Commit only coherent verified source/manifests after diff checks. Never push
    or modify the seed/runtime catalogue or the user's live saved project.

## Lessons from the completed pair

- Reserve stair voids, landings, headroom and treads in geometry and navigation.
  A broad hidden navigation floor can trap upper flights or conceal physical gaps.
- A route solver pass is insufficient: raycast actual exported floors/ceilings.
- Check partitions against windows, counters, open door leaves and beds.
- Rooms must accommodate the app's 0.22 m movement clearance. The bathroom pilot
  needed a 0.95 m doorway and an offset path around its shower tray.
- Use cameras that prove complete fixtures and threshold edges. Browser review
  cameras must respect authored lens settings; generic FOVs can hide evidence.
- The old pair passed local architecture/walking review but still had two P1
  keeper limitations each. New work should improve those limitations; they are
  not permission to conceal finish defects or make keeper claims.

## Completion and follow-up

Count a model complete only after the agreed local architecture/circulation gates,
browser checks, reproducibility records and independent review pass. References,
render attempts, recolours and failed models do not count toward twenty. Full
keeper blockers remain separately recorded. Keep the previous pair intact.

The heartbeat continues this finite work from saved progress. Stay quiet for an
unchanged running job; notify the user on a meaningful batch checkpoint, completion,
failure needing intervention or required user action. Once all twenty have passed,
write a final contact sheet, interactive local catalogue and human/machine delivery
manifest, report the result, and pause this task's heartbeat. Do not archive the
chat automatically. If tools or a required approval block progress, record the
exact blocker and notify the user without claiming completion.

## Pilot commands and current tooling

Run from the worktree above. `build_childcare.py` is a dedicated constructor for
the garden pavilion; it does not build the other nineteen designs. Each needs
its own locked source set and authored composition. The original brief alone
does not authorize using this envelope for another family.

```powershell
$batchRoot = 'C:/dev-artifacts/CityPrompt/neighborhood-expansion-20-2026-10-03'
$blenderExe = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
# Choose a new unused version; never overwrite an existing candidate.
& $blenderExe --background --python tools/neighborhood_expansion/build_childcare.py -- --output-root $batchRoot --version vNNN --dry-run
& $blenderExe --background --python tools/neighborhood_expansion/build_childcare.py -- --output-root $batchRoot --version vNNN --resolution 1280
$candidate = "$batchRoot/childcare-garden-vNNN"
node tools/neighborhood_refinement/check-walking.mjs $candidate
node tools/neighborhood_expansion/check-garden.mjs $candidate
& $blenderExe --background --python tools/neighborhood_refinement/check-physical-walk.py -- $candidate
python tools/neighborhood_expansion/boards.py $candidate
python C:/Users/andre/.codex/skills/rlasm-expert/scripts/validate_candidate.py $candidate
# Start once; use --refresh to update the model list while it already runs.
node tools/neighborhood_expansion/preview.mjs $batchRoot 5203
node tools/neighborhood_expansion/preview.mjs $batchRoot 5203 --refresh
```

The source builder snapshots its own code, low-level dependencies, source pixels
and masonry tile into each external candidate. It renders the reimported GLB.
The tile's observed cadence was calibrated to1.25Ã—2.2m; the requested2.4m square
was not produced by the image generator. Remaining palette finishes require a
separate full keeper material pass. Route checks cover authored paths and cannot
certify unrestricted collision or building-code compliance.

## Corner-entry fourplex tooling

`build_corner_fourplex.py` authors the separate corner-entry design; its three
source locks and inferred dimensions live in `corner-prework.json`. It uses
`delivery.py` only for source validation, export, script snapshots and exact-GLB
rendering. The shared delivery module does not compose building geometry.
Run it with the same `--output-root`, `--version` and `--resolution` arguments
as the childcare builder. Its masonry cadence is1.92x2.0m, distinct from the
childcare tile. The generalized boards tool selects the locked front source and
an existing interior camera. The expansion viewer excludes the earlier
central-entry fourplex's one-off shower camera.

The finite corner repair pass ends at `fourplex-corner-v004`. Its33 views prove
four furnished homes, two separate stairs, intersecting roofs, shower fixtures
and a clear rear bicycle bay. The20 authored routes include both stairs in each
direction and access to the rear bench/bikes. Run `check-garden.mjs` after the
native walking check; three rear props have explicit collision probes.
Do not begin another repair version in this pass. Consult its independent
review and delivery manifest for the final scoped decision.

Carry these concrete corrections into later constructors:

- Guard the upper slab lip above a lower flight as well as both inner stair
  edges. Cross the half landing beyond the guard ends and include guards in
  navigation obstacles. Match navigation triangles to actual tread/slab edges.
- Do not place an opaque bathroom liner behind an exterior window. Show complete
  fixtures with dedicated cameras, and avoid open door leaves obscuring beds.
- Reserve the bicycle parking footprint before placing shrubs. Include hardware
  helpers explicitly in obstacles when their default module is not a site prop.

## Brick sixplex tooling

`build_brick_sixplex.py` authors a three-storey brick walk-up with exactly six
furnished flats and one stacked shared stair. Its revised wide front, compatible
oblique and roof study are locked in `sixplex-prework.json`; generation records
are in the external `sixplex-locked-generation.json`. The original narrow front
in `source-attempts/sixplex_brick_walk_up/front-001.png` remains preserved with
its original provenance. The roof study governs topology, not metric dimensions.

Use the same builder arguments as the other constructors. The sixplex reuses
atomic wall, door, bed and bathroom helpers from `build_corner_fourplex.py`;
`delivery.py` snapshots that dependency through its optional `extra_scripts`.
The envelope, flat roof, facade composition, plan and circulation are sixplex
specific. Its source-conditioned brick tile maps to2.16x2.08m.

V001 has40 completed views but fails six apartment entry paths beside protruding
books. V002 offsets those aisles by0.20m and adds two clear kitchen sink/contact
views, making42 required views. Those views exposed cabinet timber filling the
sink recesses. V003 cuts the cabinet around each bowl. Preserve both failed
versions. The gate requires all25 routes,20 furniture probes,4 garden probes,
physical checks, browser and independent review. Read live progress for the
final decision; machine checks alone cannot approve a candidate.

Carry the middle-floor stair distinction forward: a stacked continuing flight
needs an open upward mouth; the guard across the lower-flight lip belongs only
on the top floor. Disable camera, glossy and transmission visibility on QA lights
as well as their specular/transmission factors. This removes the oversized light
ovals established in earlier prototypes; material finish remains a separate gate.
For sinks, cut the supporting cabinet as well as the worktop and bowl. A real
bowl can otherwise be filled by solid timber even when the countertop hole looks
correct from a distance. Require a close kitchen view before accepting it.

## Reading pavilion tooling

`build_library_pavilion.py` builds the distinct vaulted reading pavilion.
`library-prework.json` locks its harmonized front, corrected oblique and overhead
roof study. Earlier narrow/notched attempts remain in
`source-attempts/library_neighborhood_pavilion/`; full built-in generation
records are collected in `library-locked-generation.json`. The overhead study
governs topology only. Independent source review is in
`prework/library-source-review.json` outside the repository.

The single asymmetric roof has a real opening beneath its long clerestory.
The initial proposed cap would have sloped backward. Its resolved cap rises
from 6.61 m at y=-3 to 6.8205 m at y=2.8 and meets the main plane with flashing.
Sources, roof planes, dormer cheeks, lining and support rods must agree on that
opening. Do not terminate pendant rods against the main roof that was removed.
Brick gables stop at the roof-lining underside with 5 mm overlap; coplanar gable
tops previously broke through the zinc. Service partitions, refrigerator and
display sit between the five side windows.

The first three library versions remain preserved as failed review attempts.
V003 also replaces the raised apron edge with a real sloped connection from
site ground at z=0.04 to the floor at z=0.14 over 1.5 m. Navigation matches that surface and starts
on public ground, so the route covers the transition. This is local programme
proof, not accessibility certification. V004 uses a solid ramp prism embedded
in the ground and trims the adjacent lawn clear of its edge. V004 is the last
repair in this pass. Consult live progress for final gates.
All 27 final cameras include a dedicated approach view and an interior view from
behind the clerestory glazing. The boards helper now accepts `reading_hall`.

The prairie hall's initial front attempt remains in
`source-attempts/hall_prairie_community_league/front-001.png`, with prompt and
review notes in `hall-reference-generation.json`. Compatible front and oblique attempts show a nearly flush lower hip-roof
wing, which fits the user brief. The top attempt changes its relative width and
depth; reconcile that and its roof junction before source lock. Earlier prompt
shed-roof/setback details were design assumptions. The resolved lock and builder
are documented below.

## Prairie community hall tooling

`build_prairie_hall.py` authors the distinct broad gable and lower hipped service
wing. `hall-prework.json` locks front001, oblique001 and top003 in the external
canonical community-hall reference folder. Top001 and top002 remain rejected
attempts: the first changed wing proportions, and the second retained a conflicting
ridge direction. Top003 establishes parallel longitudinal ridges only; front and
oblique remain facade authority. The shorter 10 by16 m wing is a declared inference.

The roof constructor partitions planar domains and retains their upper envelope.
Valley nodes come from actual plane intersections. Two details still need explicit
closure: the vertical step where a main eave ends above a lower hip, and the gap
above a partition when the union roof rises above its original eave datum. Metal
cheeks close the first; infill cut from the actual roof patches closes the second.

V001 is retained with26 renders and13/15 native routes passing. Its blockers include
those roof closures, a rear noticeboard over glazing, unsupported wing luminaires,
canopy/transom overlap, an entry planter blocking the service door, and a lawn route
too close to a porch post. The public sidewalk also shared a coplanar grass surface.
V002 closed the partition gap and side cheek but retained open ends on that cheek.
Its lawn route also ended too close to the bench. V003 adds front/rear cheek returns
and approaches the bench from its front. All26 views were rerendered;15 native and
browser routes,20 furniture probes,4 garden probes and1,088 physical samples pass.
V003 passed independent local architecture/circulation review with zero P0/P1.
Full keeper remains on hold for browser roof seams and source finish/landscape.
This completes the pilot plus the first four-building group:5/20 local prototypes.
Wave2 began with `school_shared_community_campus`; its later hold is recorded below.

All sinks cut the cabinet as well as the worktop. Every light and extractor reaches
a physical support. The public approach begins at ground z0.04 and rises to z0.14
over a solid1.3 m ramp. These checks establish a local walking prototype, not code
or accessibility certification. Do not activate this or any batch entry in runtime.

## Shared community campus tooling

`build_campus_school.py` is the dedicated two-storey school constructor. Its
three original sources are locked in `school-campus-prework.json`; prompts,
inputs and hashes are in external `school-campus-locked-generation.json`.
The independent source-only review accepts front001 and oblique001 as facade
and roof/side authority. Top001 supplies adjacency only: its altered bay count,
bicycle shelter rotation, rear notches and depth ratios are excluded. The
64 by42 m plan is an architectural inference, not a survey.

The classroom bar has five furnished rooms per floor, rear support rooms and
an upper gallery over the double-height commons. Two stair flights connect
actual slab voids. The taller rear-right gym connects to the school and to a
separate community vestibule. Its basketball boards have physical supports.
Public-ground and interior threshold slabs must pass the exact-GLB path checks.
There were42 mandatory cameras through v004, including every classroom, both washrooms and
resource rooms, and reverse teaching-wall views.

The source-conditioned buff masonry has five brick lengths across and36 courses
vertically, mapped to1.20 by2.70 m. These observed counts supersede the requested
image dimensions. Other finishes remain a declared prototype scope.
V001 stopped at the grounding assertion before export. V002 produced38 views
but failed two classroom routes and two staff window carrier checks; it also
had unsupported paving, missing trunk collisions and incomplete room evidence.
V003 corrected those with42 views and25 passing routes, but reverse views
exposed door leaves intersecting teaching boards and detached canopy anchors.
V004 swings the doors inward, seats the anchors and makes mirrors opaque.

V004 still remains on independent local hold: both half-landing side edges
lack guards, and reversing the classroom carrier buried the teaching boards
inside the wall. Passing25 native/browser routes,57 apertures,20 furniture
probes,5 garden probes and3,225 physical samples does not close these defects.
That was the last repair in the first pass. The external
`prework/school-campus-next-pass.md` records the
specific two-part correction and added proof needed after advancing the next
queued variant. Preserve all source snapshots and review decisions.

## Courtyard childcare source checkpoint

`childcare-courtyard-source-lock.json` locks front001, corrected oblique002 and
top001 for `childcare_sheltered_courtyard`. Independent source review v2 closes
identity compatibility and the three-field mono-pitch roof topology only.
Oblique001 and its rejection remain preserved: its left roof introduced an
internal ridge and secondary strip. Built-in image generation repaired that
view using front001 and top001; no external image API was used.

Front001 controls facade identity and relative heights. Oblique002 corroborates
the exposed left elevation and continuous inward-falling roof plane. Top001
supplies adjacency only: three wings, an uncovered court, and two diagonal rear
roof junctions. Canonical copies occupy variant1 in the external childcare
reference folder; the original pilot sources remain intact. Prompts and input
hashes are in external `childcare-courtyard-locked-generation.json`.

## Courtyard childcare delivery checkpoint

`build_courtyard_childcare.py` now authors this distinct U-shaped building.
`childcare-courtyard-prework.json` records the inferred 30 by24 m envelope,
6 m wings, 2 m verandas, three inward-falling roof planes and diagonal rear joins.
Three furnished learning rooms surround the open play court, with reception,
a four-cot nap room, staff room, kitchen, adult and child washrooms. Timber roof
supports, low gate, playhouse, sandbox, growing beds and bicycles are explicit.
The source-conditioned terracotta tile uses its observed cadence: eight brick
lengths by about26.6 courses, mapped to1.92 by2.00 m. Source-only provenance stays
immutable; `childcare-courtyard-build-generation.json` adds material provenance.

V001 remains a failed36-view attempt: blocked routes, a bicycle approach gap,
a pane crossing a partition, poorly seated fixtures/cubbies, playhouse roof
penetration and incomplete camera proof. V002 repairs those with39 views but
retains a staff-route obstruction, coincident earth/turf and two evidence gaps.
V003 routes around the staff chair, separates earth and turf, and adds direct
staff and mirror contact cameras. Preserve both failed versions and reviews.

V003 passed independent local architecture/circulation review: zero local P0/P1,
41 exact-GLB views,22 native and browser routes,20 furniture probes,7 garden
probes,41 carrier apertures and1,018 physical samples. Seven browser screenshots
record manual entry from public ground, detail views, model switching, visibility
and reload. Full keeper remains unapproved: source finish/landscape/fixtures and
optical response, including roof stippling and a dark browser mirror, need work.
Its delivery manifest preserves these limits. The completed local count is6/20.

## Garden sixplex source checkpoint

`sixplex-garden-source-lock.json` locks compatible front001, oblique001 and
top001 in external variant1; the brick sixplex pilot sources remain intact.
Independent source review is `prework/sixplex-garden-source-review.json`.
The actual pixels show a transverse main gable with three short front cross-
gables. Their ridges terminate on the main forward plane below its ridge.
Reject the original prompt assumption of three full-depth parallel roof bars
and the top prompt's claim that cross-ridges meet the main ridge. Solve actual
plane intersections for the valleys; do not treat seam lines as roof folds.

Front controls the six door leaves and three recessed balconies. The left and
middle bays have windows left of their paired entries; the right bay mirrors
that arrangement. Oblique controls four left-side windows per storey. Top is
adjacency evidence only. Hidden elevations, six floorplans and three enclosed
upper stairs still need explicit inference. No sixplex geometry or material
exists yet; source approval is not model approval.

## Campus second bounded pass

After courtyard childcare v003 passed, v005 opened a second finite pass with
at most three repair versions. Its side guards have slab-seated pickets, short
rail transitions to the last flight posts and rear guard connections. Two
new side contact cameras make44 views. Embedded guard obstacles have two named
exclusion probes at z2.04; `check-circulation.mjs` exercises those through the
bundled actual app solver after `check-walking.mjs`. Teaching boards now centre
at y=-9.1655 and trays at-9.20, overlapping the reversed classroom carrier by
2 and5 mm respectively. The inward door swings remain.

V005 passed the fresh independent local architecture/circulation review with
zero local P0/P1. All44 exact-GLB views and three boards were reviewed, alongside
25 native/browser routes,20 furniture probes,5 garden probes,2 circulation guard
probes,57 carrier apertures and3,225 physical samples. Nine browser PNGs and logs
prove entry from the sidewalk, repaired contact views, model switching, visibility
and reload. Exact GLB hash begins7746db3c; full hash and independent review live
in its delivery manifest and synchronized progress. V004's hold is preserved.
Full keeper still has two P1 finish groups: schematic source details/landscape,
including an overlapping lawn patch, and offline/browser optical/shadow response.

The sixplex has an external measurement draft and source-conditioned buff brick
specimens. Original and v002 specimens have10 brick lengths by27 courses and
fail even-course bond continuity. Both remain preserved with independent records.
V003 uses four lengths by12 alternating courses, mapped to0.96 by0.90 m. The
independent material-category review confirms the corrected phase and source
compatibility. `sixplex-garden-material-lock.json` locks only prototype masonry
authority. Boundary mortar continuity, baked edge shading and short-pattern
repetition still need mapped render proof before full keeper approval.
The draft is not frozen construction authority. Read
`prework/sixplex-garden-measurement-draft.json` and
`sixplex-garden-material-v003-generation.json`,
`prework/sixplex-garden-material-review-v3.json` and
`sixplex-garden-build-v3-generation.json` before continuing. Resolve all six
floorplans, three private upper stairs, roof intersections, routes and complete
camera roster before creating its dedicated builder. Then advance the park-edge
hall within wave2. Completed local count is7/20. No build job remains running.

## Garden sixplex first geometry checkpoint

`build_garden_sixplex.py` is a dedicated constructor for six flats in three
8.333 m bays, three private straight stairs and three recessed upper balconies.
`sixplex-garden-prework.json` freezes inferred dimensions, six furnished plans,
three source locks, v003 material authority, 41 routes and 61 cameras. Its 13
clipped roof fields cover exactly 387.09 square metres: one transverse main
gable and three lower short front cross-gables. Wall caps follow the analytic
planes. Independent code preflight corrected balcony/stair separation, fixture
contacts, a rear opening collision, shower bracket support and table supports.
Dry run passed three sources and 61 cameras before the first finite candidate.

### Garden sixplex v001 hold and finite v002 repair

V001 completed all 61 views and three boards but failed six native routes:
three upper entries omitted a native strip across a physically solid doorway;
three stair ascents targeted the shared approach/riser boundary. Two of 1,561
physical route samples hit the underside at a float32 riser edge. These failures
remain preserved. Both sides of all 51 risers passed 102 unchanged-tolerance
physical probes, proving complete treads. A separate amended-metadata diagnostic
on the unchanged v001 GLB passed 41 routes and 1,626 physical samples. That
diagnostic is not a model deliverable or approval.

V002 adds the real portal surface, puts the first tread waypoint inside that
tread, and seats twelve book props on six dining tables. It rerendered all
61 views for complete independent review. Both jobs have finished; consult the
latest progress record instead of relaunching either candidate.

## Garden sixplex local delivery and park-edge hall handoff

V002 passed independent local architecture/circulation review with zero local
P0/P1: 61 exact-GLB renders, 41 native and browser routes, 20 furniture probes,
six garden probes, three balcony barrier probes, 31 carrier apertures, 1,626
physical samples and 102 two-sided riser probes. Thirteen browser screenshots
cover manual entry/back, upper landing, kitchen/shower/balcony, switching,
visibility and reload. Direct GLB inspection verified all three native portals
and twelve books seated on six dining tables. Earlier prework prose said six
books; the delivery manifest records the actual twelve. V001 and its three
local P1 groups remain preserved.

V002 retains two keeper P1 groups: source finish/detail/landscape and optical
finish, including roof stippling, pale metal, near-absent offline glass and an
opaque browser shower screen. Delivery manifest and local-pass-index preserve
these limitations. Keeper approval, runtime activation and main-app placement
remain unapproved.

The hall's front001, oblique001 and top002 sources are independently compatible
and locked by `hall-park-source-lock.json` in external variant1. Top001 remains
held for an apparent unsupported rear bar. Top002 is topology-only and supplies
no nadir metric authority. All three compatible sources show six outer veranda
columns; an apparent seventh is recessed at the glazing plane. Author five
structural bays and classify recessed supports separately.

The measurement draft is not frozen: 32 x 22 m includes a 3.5 m veranda.
Room/frame/roof/contact coordinates, routes and cameras need reconciliation.
Cedar v002 retains eight full board widths at an inferred 0.96 x 2.40 m mapping.
Independent category review finds it source-compatible, with a partial boundary
repair and unresolved repeat/optical limits. `hall-park-material-lock.json`
records category authority only. Use board-aware geometry/UVs without raw
horizontal wrapping, or a separate bounded correction. Preserve both specimens
and reviews; `hall-park-build-v2-generation.json` collects their provenance.

Next is the hall's dedicated measured constructor. Completed local count is
8/20. Final contact sheet/catalogue and full keeper assessment remain pending.

## Park-edge timber hall first construction checkpoint

`build_park_hall.py` and `hall-park-prework.json` freeze one common gable roof,
six outer veranda columns/five bays, separate recessed and inferred rear
supports, a vaulted entrance commons, occupied main hall, two meeting rooms,
kitchen and washroom. The 32 x 22 m envelope includes the 3.5 m veranda.
Individual 0.12 m cedar boards use interior intervals from the source specimen,
without raw horizontal/vertical wrapping. Physical brick solids are clipped
against every opening and consolidated into one mesh; prototype edges/finish
remain declared limitations. No shared compiler or live project was changed.

Independent initial preflight found seven source/code groups; corrections
preserved its hold. A later low-window brick-coverage hold was also preserved
and corrected with two-axis clipping. V4 source/code preflight passes with zero
P0/P1, scoped to pre-build only. The first unskinned diagnostic was interrupted
for a bounded brick-mesh optimization. V002 preserved two route failures at a
room leaf and storage rack. V003 passed all 23 actual-app routes, 20 furniture
and four garden probes, with 1,031 cedar board segments inside source UV bounds.
The 1.3 m public ramp, plateau, native surfaces, waypoint and portal agree.

The first candidate `hall-park-v001` completed 38 exact-GLB views. Its later
independent hold and the bounded correction are recorded below. The unskinned
checks and source/material categories do not approve a model. Checkpoint the
completed second group before beginning the third group.

## Park hall bounded v002 correction

V001 is preserved with all 38 exact-GLB renders, three boards, 23 native routes
and 1,556 physical floor/headroom samples. Independent review holds two local
P1 groups: rear windows/artwork intersect posts, and the rack base floats 11 cm
above the floor. Full keeper also holds source finish/detail and optics.
The broader 462-ray aperture check confirms two obstructed rear windows;
the carrier-only audit missed nearby geometry. Browser evidence is partial.

V002 moves the inferred rear lights into clear bays, seats art on the solid
wall between them, adds four grounded rack casters and updates its route/camera.
Sources, front roof and frame stay locked. Fresh complete renders, machine and
browser checks, and independent review are required before counting it.

## Wave2 complete: nine local prototypes

Hall park v002 passes independent local architecture/circulation with zero
P0/P1 blockers. Rear lights and artwork clear the retained posts. Four physical
rack casters reach the floor and overlap the base by 40 mm, independently
verified from the exported GLB.

All 38 exact-GLB views and three boards, 23 native/browser routes, 20 furniture
and four garden probes, 1,544 physical samples, 462 aperture rays and 13 browser
screenshots pass. Controls, model switching, visibility and reload work. Browser
route error reaches 25 mm at the washroom basin; every route stays within the
agreed tolerance. Full keeper retains two finish/optical groups.

V001 and failed diagnostics remain preserved. This completes the pilot plus two
bounded groups: 9/20. All nine GLB/review hashes match local-pass-index. Wave3
begins with school_timber_learning_courtyard and requires its own source lock
and inferred plan before construction. Main-app runtime, human catalogue and
publication approval remain absent.

## Timber courtyard school source checkpoint

The third group begins with school_timber_learning_courtyard. Built-in front,
rear oblique and roof-study references are independently compatible with explicit
source roles. Their exact pixels are copied to the external canonical
neighborhood-school variant_2 files. school-timber-source-lock.json records
front facade/entrance authority, rear courtyard/covered-walk authority, and
topology-only use of the elevated roof study. Its changed four front window
groups and canopy/site details are excluded. The primary front has three broad
connector upper groups plus narrower or obscured transitions.

Source images show a full brick ground storey with cedar above. The two parallel
wing ridges meet a transverse connector roof; infer actual unequal heights and
clipped plane intersections rather than copying projected crossings. The rear
court stays completely unbuilt and open to a play lawn.

External prework/school-timber-measurement-draft.json proposes a 52 by40m U,
six furnished classrooms per floor, connected courtyard corridors, two stairs
and occupied support rooms. This is a draft. Bay/partition, washroom, stair-void,
roof/lining, material and camera contracts still need a complete prebuild review.
No school geometry or material specimen has been approved or built. Resume those
concrete steps; preserve the three original references and provenance. Completed
local count remains 9/20. Keeper and main-app readiness remain unapproved.

## User checkpoint after building ten: main CityPrompt browser trial

The user requested: "Once you get to 10, please trial them all in the City prompt
browser." After the tenth independently passing local model, trial all first ten
additional buildings in the main CityPrompt app before starting building eleven.
This checkpoint is part of the ongoing finite batch. The standalone inspector
checks already recorded do not establish this trial.

Use a separate disposable project on an appropriately sized vacant site, preserving
the user's live project and all original candidates. Freeze the ten exact IDs and
GLB hashes. Verify each model through supported local app placement, identity,
scale, ground support, entrances/approaches, visible rooms and available walking.
Exercise supported editing, Undo/Redo, save/reload/reopen, visibility and capture;
then review a mixed neighbourhood containing all ten with clear paths/open space.
Keep individual trials for large civic buildings. Save per-model screenshots,
binding/hash readback, console/network findings and PASS/FAIL/NOT TESTED results
using the shared runtime checklist. Preserve sealed asset reviews; add separate
runtime evidence. Do not infer keeper approval from a browser load.

Temporary isolated local test bindings are within this trial's scope. Public
catalogue activation, publishing, pushing and changing the user's live project
remain unauthorized. Identify the actual app/backend/storage environment before
installing fixtures. Record concrete blockers and required intervention honestly.
Read the machine checkpoint in progress.json and finish it before building eleven.

## Timber courtyard school prebuild and diagnostic checkpoint

The material review confirms eight120mm cedar pitches and24courses/eight brick
length equivalents. Both raw repeating specimens remain held. The dedicated
school uses physical116mm cedar faces/4mm gaps and230x65mm brick faces in
240x75mm running-bond modules, with measured interior-face sampling and parent
UVs through opening/ridge cuts. Long cedar grain stretching remains a finish
limitation. Brick stays behind the separate interior finish.

Measured prework freezes twelve24-seat classrooms, eight support rooms, both
connected floor corridors, two22-riser stair cores, exact floor/ceiling voids,
seated guards and a source-specific three-ridge U roof. Equal-drop overhangs and
upper-envelope plane clipping close the roof intersections without overlapping
whole roofs. All71 review cameras were authored before geometry.

Independent constructor v001 holds seven source/contact/circulation groups;
v002 holds two residual furniture/path groups. Both source snapshots and reviews
are preserved externally. V003 code preflight passes zeroP0/P1 after finite
corrections, including supported window shades, ceiling joins, real table/bench
links, rear native thresholds, measured material samples, seated fixtures/books,
and clear stair cameras. This closes only the prebuild code category.

The bounded22-view texture-free diagnostic has started externally at
prework/school-timber-unskinned-v001. Read its saved job/PID/log before resuming;
never duplicate it. Run45 actual-app routes, nine garden and six guard probes,
physical exact-GLB floor/headroom/aperture/stair checks and independent diagnostic
pixel review before the first skinned candidate. Full71 exact-GLB views, three
boards, browser evidence and independent holistic local review remain required.
Completed count remains9/20. The main CityPrompt all-ten trial stays pending the
tenth local pass and must finish before building eleven.


## Timber school diagnostic checks prepared

The texture-free diagnostic PID10664 remains the one active school job. The
source builder and measured prework stay frozen at ae889608 and53dde8b0.
No model pass has been added:9/20, with the allten main-app trial pending.

External `check-school-timber-physical-details-v003.py` passed independent
checker-only review with0P0/P1. It checks both sides of all44 stair risers and
four flat joins (96 probes),78 aperture sections (1,638 rays), actual floor-based
headroom and asserted imported opaque roles. Its explicit `--unskinned` mode
validates diagnostic bytes and source snapshots before allowing the two absent
skin roles; skinned models require both. Preserve the earlier two checker holds.
Actual mesh results are still pending and this review grants no model approval.

External `school-timber-boards.py` prepares the22-view diagnostic contact sheet,
or the complete71-view/source/phone boards for the later skinned candidate.
It selects the actual `classroom_left_1_1` camera and refuses missing renders
and overwrites. Both helpers passed Python compilation; hashes and commands
are recorded in the manifest. Run only after the necessary files exist.

Read-only main-app preparation identified5174 as the qwen-street-trial frontend
at48ef5038082d2636c2ec9cde4301114373e71cfd, with a live main-app landing page.
Its8001 backend/database/storage configuration remains unverified. This is
preparation only: no models placed, fixtures installed or original projects
changed. Save a new runtime preparation record and identify the isolated trial
environment when the tenth model passes.


## User completion handoff: bring up CityPrompt

After the full twenty-building batch and the required ten-building main-app
trial are finished, bring up the verified main CityPrompt app visibly in the
Codex browser. Prefer the disposable mixed-neighbourhood trial project so the
user can inspect the results. Verify the page loaded and keep the tab as the
user-facing deliverable. Preserve original projects. The standalone model
inspector does not satisfy this handoff. Record completion_browser_handoff,
then report the honest result and pause the heartbeat.


## Timber school first diagnostic hold and finite replay

Unskinned v001 completed22 exact-GLB views and preserved its original named
scene. Its0f7fa425 GLB passes96 stair-boundary probes and1,638 aperture rays.
The actual app solver passes40/45 routes,20 furniture and9 garden probes.
Both ascents stay on an incorrectly competing lower native plane; three routes
cross real open leaves/posts. Physical route review preserves279 failures,
including under-stair head hits and failed-route continuation at paving edges.
Independent diagnostic review holds twoP1 groups; no model pass has been added.

The null-only guard helper also reports six failures because it selects a
distant legitimate lower floor. Independent movement toward all six guards at
their occupied height rejects crossing without a level drop. Preserve the old
failure; use a separate explicit at-height movement proof for the revised
diagnostic. App clearance/step tolerances stay unchanged.

V005 source/prework changes only navigation ownership/routes and camera poses.
The proposed v002 replay uses v001's sealed named blend, asserts identical
non-navigation/camera source AST, preserves obstacles, and requires identical
exported binary geometry. It must rerender22 views from the newly exported GLB
and pass fresh native/physical and independent review. Keep original assembly
source/spec separate from the newer network/camera snapshots. Classroom views
clear foreground leaves and canopy-post views include the feet. Complete71-view
skinned/model/browser gates remain pending. Count9/20, no building11 started.


## Timber school v002 replay launched

Independent v005 source/replay preflight passed0P0/P1. The one bounded replay
uses the original named diagnostic scene, unchanged geometric source AST and
asserted exact BIN bytes, with updated navigation and camera evidence only.
Job PID28948 is recorded externally. Preserve v001 hold and all failures.
Fresh geometry JSON/bounds,45 routes,9 garden probes, six at-height guards,
physical floor/headroom/stair/aperture evidence and22 rerendered views still
require independent diagnostic review. Count remains9; no skinned/model pass.


## Timber school v002: physical pass, rendered evidence hold

Fresh45/45 app routes,20 furniture,9 garden and6 at-height guard controls pass.
ExactGLB physical proof passes13,450 route/start samples,96 stair boundaries and
1,638 aperture rays. BIN and geometry-bearing JSON match v001; only walking
extras change. The old null-only guard report remains4/6; occupied-height
movement rejects both upper-lip approaches without dropping to a lower floor.

Independent pixel regression holds v002: blind object-name lookup selected
QA rear LIGHT instead of QA rear.001 CAMERA. New black patches also require
render-state diagnosis despite unchanged geometry. Preserve all22 images and
passing machine evidence. A finite GPU/CPU control is running; require typed
camera assertions and independently reviewed render-only correction before
fresh22 pixels and the full skinned candidate. Count remains9, no building11.


## Timber school diagnostic pass; first full skinned build running

Independent unskinned v003 review passes0P0/P1 after all22 direct pixel views,
three locked sources and complete bound evidence. Both earlier diagnostic holds
remain preserved. The rear CAMERA identity and original OPTIX process-device
initialization restore correct rear framing and remove black surface artifacts.
Exact geometry JSON/BIN remain unchanged. Native45 routes,20 furniture,9 garden,
six at-height guards,13,450 physical route/start samples,96 stair boundaries
and1,638 aperture rays pass within their declared scopes. This is diagnostic
approval only, not a complete textured model or keeper approval.

The first full school-timber-v001 build is now one hidden Blender job, PID5212.
Builder/prework are frozen at a60f515e/9526ab31. It constructs physical source
brick/cedar and renders all71 exact-GLB views at1280. Preserve original jobs and
evidence; the source assembly may exceed30minutes before export. Run fresh
full-skinned checks, three boards, validator, browser and independent holistic
local review after actual completion. Count remains9/20; no building11.

Main-app checkpoint preparation also records an external first-nine fixed-native
fixture draft v002 with exact reviewed GLB hashes, full landscaped plot bounds
and embedded network equality. It is provisional and NOT_TESTED: no fixture
installed, source catalogue/database/project modified or runtime gate claimed.
Add the tenth after local pass, then freeze ten and complete all required
individual/mixed CityPrompt app trials before starting eleven.


## Isolated main-app checkpoint environment prepared

Main CityPrompt now runs from this worktree at5175 with a dedicated8003 backend,
owned empty cityprompt_neighborhood20_20261003 database, one local trial account,
own56380 Redis and private19003 media bucket. Normal UI login and the styled
empty dashboard reload pass; no fixtures installed, models trialled or projects
created. Preserve original databases, projects,5174/8001 and the5201 user tab.
Current5174 is qwen-wan-current-main; earlier qwen-street-trial identification
is historical. Detailed redacted proofs and preserved preparation failures are
in ten-building-trial-environment-prework-v004.json and main-app-runtime/.

Independent fixture helper v001/v002 holds remain. Corrected v003 passes
helper-only0P0/P1, with complete exact GLB/review/network/build/thumbnail/source
bindings, ten distinct identities, GLB-bound native dimensions and a process
startup seal SHA. The omitted original childcare review hash is independently
verified and pinned; no review or decision rewritten. No runtime approval.
Frontend jobv004PID22284 uses the v003runner, launched FROM frontend so Tailwind
content paths resolve. Keep earlier missing-style screenshot and jobs.

At10 local passes, run seal-main-app-ten-fixtures-v003.py --apply externally,
record the seal SHA, and restart only own5175 frontend with that exact
--seal-sha256 argument and frontend working directory. Then complete ordinary
UI individual and mixed vacant-site trials with per-model runtime evidence
before building11. Current count9. School-timber-v001 PID5212 has entered its
71-view render stage; run fresh complete skinned gates only after BUILD_COMPLETE.


## Tenth local model passed; main-app trial checkpoint triggered

School-timber-v001 finished71 exact GLB1280x960 views, three boards and all fresh
gates:45native/browser routes,20furniture,9garden,6at-height guards,13,450bound
physical route/start samples,4,469generic samples,96stairs and1,638aperture rays.
Independent full-resolution review passes local0P0/P1 and holds two keeper-only
finish/material and optics groups. ExactGLB538e8115/64,702,276bytes is pinned.
Both independent review versions are preserved; additive v002 harmonizes only
the canonical local decision literal without changing findings. No main-app
runtime approval. Legacy null-only guard4/6 failure remains preserved.

COUNT10/20. Stop new buildings at the user-required checkpoint. Freeze/install
the exactten external private fixtures with v003 helpers and process sealSHA,
then trial all10 in the dedicated main app5175/8003 through ordinary controls
on separate disposable vacant-site projects plus a mixed neighbourhood. Save
per-model PASS/FAIL/NOT TESTED, screenshots/readbacks and honest limitations.
Complete and report the trial before11. Original projects/catalogue untouched.


## Exact ten installed; first main-app trial active

Corrected v004 fixture helpers independently pass0P0/P1 and13 positive/negative
cases. Earlier holds and the actual v003 seal refusal remain preserved. Allten
are now sealed externally at43fb056d; own5175 frontendjobv005PID26756 enforces
that exact startup seal from the frontend working directory. Do not apply the
sealer again or duplicate running jobs. Source catalogue remains unchanged.

Normal UI created only disposable Garden Pavilion project0a17a73b in owned8003
trial DB. Exact9,051,328-byte GLBf509d4a1 and native38x30m plot pass HTTP/readback;
front entry walk reaches connector/classroom doorway and return entrance works.
Visibility toggle, exact free preview PNG, rotation Undo/Redo, move save/reload
retain stable zone identity and dimensions. Original natural ground hadfive
unavailable cells; preserved evidence precedes deliberate UI redevelopment
level1102.662m. This is prepared concept evidence, not natural terrain approval.

First trial remainsIN_PROGRESS: sidewalk/actualstepfoot, complete ground/low
view review, additional recovery checks and independent runtime review remain.
No sidewalk selected; no comprehensive route traversal or runtime acceptance
claimed. Evidence is externalmain-app-trials/01-childcare-garden-v004. Complete
the remainingnine separate ordinary UI vacant-site projects and mixedten, record
honest PASS/FAIL/NOT_TESTED, and report checkpoint before11. Count10/20 unchanged.

## First main-app pilot on hold

The Garden pilot reproduced C3 ground seating, C5/C9 entrance integration and C8 visual blockers. Independent diagnosis and adapter-design preflight are preserved under its external review folder. Native walking omits the 0.6 m band across existing paving at the plot boundary; portal rectangles alone do not create floor. Begin only a bounded shared C3 repair using exact native bounds, current shared/prepared ground and measured foundation seating. Entrance and optics remain on hold; keep nine other main-app trials NOT TESTED and building eleven queued. The internal lane recovered through hydration of nine existing local LFS objects and normal Retry. A rejected boundary edit recovered through normal Reload saved version. Landscape Apply is UI-only evidence pending invalidation, reload and capture.

## Bounded C3 repair verified

The review renderer now measures the complete native GLB bounds, matches the existing bottom-centred transform, and uses shared full-footprint contact and measured foundation seating. Verified ground controls walking and capture issues; retained display ground only keeps a coherent draft. Suspended/failed models register blockers and clean up on unmount. Independent source review v002 passes 52 narrow tests plus type-check. Independent browser C3 review v001 passes only the first Garden prepared-ground contact, reload and free capture; natural terrain and real-browser negative cases remain untested. Source freezes and all nine images/readbacks are external. Sealed GLB bytes and native dimensions remain unchanged.

The additive runtime-trial-report-v001.json remains HOLD for C5/C9 advertised entrance controls/native floor handoff and C8 glazing/roof artifacts. Nine other main-app trials, mixed neighbourhood and building eleven remain queued. Next: finite renderer diagnosis and explicit physical/native handoff review, then reprove Garden before scale. No assets, catalogue entries, original projects or running environment jobs were replaced.
