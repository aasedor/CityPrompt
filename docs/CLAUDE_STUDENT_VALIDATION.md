# Claude Code — student validation of the exact 27-model rebuilt copy

First follow [the portable setup](CLAUDE_VALIDATION_SETUP.md). The app is
http://127.0.0.1:5180/login **in your test environment**, not Andrew's Windows PC.
Log in as `student-validation@example.com` with the generated password printed
by `python3 scripts/validation_bundle.py init-env` (also stored privately in
`.validation/env/backend.env`). Do not put credentials in reports or commits.

Operate the real browser as a student. Preserve exact model hashes. Bootstrap
seeding of the Model Library assets is necessary and authorized; scripting
student design geometry, boundaries or demonstration projects is not. All
authoring should use ordinary UI controls. Paid generation is disabled.

Report this as a **rebuilt-copy validation**, including the Git SHA, browser,
map availability and terrain mode. A missing runtime prerequisite is BLOCKED,
not a model pass or failure. This packet has not been browser-approved.

## Scope and exact inventory

Use `frontend/src/data/validationCatalogue.json` in this checkout and the extracted `.validation/evidence/<placement_id>/` directories. Windows paths in the source inventory are historical provenance only. They identify every exact variant, revision, SHA-256 and local URL. Expect **12 buildings, 8 parks and 7 streets**. Every card must expose only its selected variant; no older sibling, generic substitute or exploratory catalogue should be offered.

Buildings: Buff-brick infill; Crystal brewhouse; Earth-sheltered museum; Halifax clapboard house; Machiya cafe and gallery; SoHo cast-iron loft; Streamline Moderne corner; Terraced garden mid-rise; Timber community hall; Timber-screen townhouse; Beltline mixed-use mid-rise v005; Calgary Modern Infill v007.

Parks: Conservatory botanical garden v013; Museum sculpture court v006; Neighbourhood orchard v002; Terraced performance lawn v003; Timber and stone square v003; Wetland boardwalk v005; Teaching demonstration garden v5; Basketball park v4.

Streets: Amsterdam canal street v005; BRT transit mall v004; Planted shared lane v001; Quiet residential street v002; Tied-arch gateway bridge v003; Neighbourhood Main Street recipe v2; Pedestrian Market Street recipe v2. Main/Market retain their stable saved variant IDs ending in `_v1`; check the new recipe/module hashes, not the suffix alone.

The 21 baseline entries have user-adopted visual baseline approval. The six priority upgrades still need exact-version visual acceptance. None is declared completed by this installation. Do not copy a pass from an older model or mark human approval yourself.

## Known limitations — do not waste time rediscovering them

- The **six baseline parks** and **five baseline streets** are installed as exact, fixed native review assemblies. They require a prepared site and their full rectangular footprint. Move and rotation are the intended review controls. Native surfaces are retained; models are not stretched or bent. Resizing/irregular layouts, extensible road routes, full connections and station editing for these versions are **missing integration**, not validated capabilities. Mark their advertised extension gates **BLOCKED / classroom blocker**, even if the static model looks excellent. Attempt one representative prohibited resize to confirm a clear guard, then do not repeat the same missing feature eleven times.
- In particular, the BRT review assembly contains its authored station. Right-click **Add station / stop**, position/persistence/removal and avoiding automatically repeated stations are still required acceptance gates. If unavailable, record FAIL/BLOCKED; do not mark N/A or call the model complete.
- Main Street and Market Street use native modular route rendering: test longer/bent routes and junctions. They must not stretch the complete preview GLB.
- Basketball and teaching garden use the shared adaptive park fitter with the upgraded module bytes. Basketball has a 28 × 15 m playing area in a 36 × 23 m module, with native run-off/gates; up to four full courts may fit. Garden structures/bed units remain rigid and whole bed rows can be added within its bounded programme.
- All buildings are single fixed native models. A larger surrounding plot must retain the same unscaled building, roof, openings and floor count. Additional buildings use Place another. Do not expect building stretching or extra floors.
- Native building entrance anchors for this new roster are not newly measured/approved. Test ordinary entrance picking/connection controls and report a missing or wrong route. Do not insert developer coordinates, move doors or fabricate an entrance pass.
- This build uses the tested source base above; it does not include unrelated uncommitted changes from other worktrees. Read `docs/ARCHETYPE_RUNTIME_INTEGRATION.md` and `docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md` in this checkout for the full acceptance checklist.

## Finite student test

1. **Start naturally.** Log in through the UI. Create a new disposable project on visibly vacant land. Use a sufficiently large parcel for the native models; put the bridge/large museum/BRT in separate appropriately sized test projects. Draw the site boundary and use the normal prepared-site workflow for the first pass. Do not place over existing buildings. Do not create design geometry with APIs, scripts, console injection, or a seeded demonstration scene.
2. **Discovery.** Check the three category counts (12/8/7), search each model, and confirm there is one exact version per card. Check inspector variant selectors too. Images, labels and model identity should agree. Missing models, legacy variants, broken references or silent generic blocks fail this gate.
3. **Pilot first.** Build one small mixed scene using Modern Infill, Main Street and basketball (use garden too if space allows). Place, move, rotate, resize where supported, Undo, Redo, save, reload, reopen and export. If login, placement, ground or export fails systematically, capture one clear reproduction and stop repeating the blocked workflow. Continue only independent useful checks.
4. **Visual pass for every model.** Place each of the remaining exact models through its card. Wait for loading/ground/save readiness. Inspect an aerial view and at least front/side/rear low views; inspect signature details and the roof. Compare with its locked reference photos and reference evidence in `.validation/evidence/<placement_id>/`. Look for reference identity, believable metre scale, coherent materials, missing faces, generic proxies, black/transparent surfaces, z-fighting, floating/buried bases, unsupported structures, blocked doors/paths, and a cohesive appearance alongside neighbouring models. A pretty aerial image is not sufficient. Record framing failures separately from geometry defects.
5. **Building behaviour.** For each building, place at default size, rotate, move, enlarge its plot and verify the model itself is unchanged. Check a too-small plot is rejected rather than distorted. Check entrance-to-approach-to-sidewalk continuity at pedestrian height; include side/rear access when visibly intended. Undo/Redo and reload must retain the same exact model and settings. Check changing floor controls cannot silently substitute a massing model.
6. **Adaptive parks.** For basketball and garden, try default, minimum, larger, narrow, triangle and L-shaped plots through student controls. Doubling area only permits a second court when the **whole court plus run-off and access actually fits**; it must never make one giant court. Choose a sufficiently wide/deep rectangular case to demonstrate a second full court, then shrink again. Check courts, hoop heights, nets/fences, shelter, beds and labels never stretch or overlap. Paths should reach usable gates/entries; unsuitable shapes must explain what cannot fit. Confirm count, geometry and access survive edits/reload. A tennis court is not in this roster—do not import an older tennis model to demonstrate repetition.
7. **Modular streets.** For Main and Market, draw a short straight route, a substantially longer route and a bend. Fixed width and furniture scale must remain stable. Check endpoints, T and X junctions, intersections with each other, tree/stall/bench spacing, clear sidewalks and crossings, no duplicate geometry at joins, and no stretched lamps/canopies. Test route editing, Undo/Redo, delete/restore and reload. Inspect where the proposal meets a real existing street; an internal junction marker alone does not prove external access.
8. **Ground and recovery, bounded sample.** After the level mixed scene works, try one building, each adaptive park and one modular street on a sloped/natural site. Exercise an edge/unsupported placement, then correct it using ordinary controls. Change an object while ground is pending. Do not flatten the site just to hide a grounding defect. Test one interrupted/failed save or temporarily offline session: retain the draft, offer recovery, and avoid endless loading or stale geometry. Record natural versus prepared terrain separately; do not infer a pass for untested models.
9. **Community coherence and capture.** In a mixed prepared scene, apply the available non-AI site-landscape preset, check residual ground avoids occupied footprints and access routes, then move an object and verify updates. Save and reopen. Use free exact current-view export, actually download the image, and inspect it: same objects/counts/positions/materials as the viewport, no stale models, missing props or editing handles. Check loading/unsupported geometry prevents a misleading export. Do not use AI images as model evidence.

## Reporting and token discipline

Save evidence under `.validation/claude-review/`.
Create `results.json`, `RESULTS.md`, a screenshot index and a short ranked defect list. Include local URL, Git commit/dirty status, project IDs, exact model/recipe/module hashes, browser/viewport, terrain mode, steps, expected/actual results and screenshot/download paths. Record console/network errors without credentials.

For each of the 27 rows, report **PASS / FAIL / BLOCKED / NOT TESTED / N/A with reason** for: identity, visuals, native scale, ground, access/connections, extension rules, editing, Undo/Redo, save/reopen, and exact export. Keep human visual approval, asset quality, runtime acceptance and release selection separate. Known missing advertised capabilities are not N/A. No blanket “all passed” based on a single mixed scene.

Work in checkpoints: pilot; remaining buildings; parks; streets; mixed-scene/recovery/export. Save after each checkpoint. Reuse scenes and shared algorithm evidence appropriately, but every exact model needs its own visual/identity check. Capture two useful views per model plus extra evidence only for failures/signature details; avoid repeated full-page screenshots and unchanged polling. Report touch/mobile as NOT TESTED unless actually tested. A bounded desktop result is useful.

Finish with: models ready for human acceptance, models blocked (and why), small follow-ups, untested gates, and the five highest-impact fixes. **Report first; do not quietly change code, replace models, relax guards, set approval flags, publish or push.** If a fix is needed to proceed, preserve the failure evidence and describe the smallest proposed change.
