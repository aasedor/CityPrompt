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
