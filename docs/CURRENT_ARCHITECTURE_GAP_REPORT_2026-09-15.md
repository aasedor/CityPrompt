# Current architecture & gap report

Audit date: 15 September 2026. Initiative: `codex/student-design-transformation`.
Authoritative baseline: `origin/main`, `1172db1ef97036a92286463c5da83b54321f8a4f`.

## Scope, evidence and checkpoint

The supplied master brief stops after section 21's “Prefer the conceptual
separation:”. Neither visual goalpost image is attached. The complete acceptance
gates and referenced API validation budget are therefore unavailable. This
report reconciles the supplied sections with current source; it does not invent
the missing requirements, carry forward another mission's spending allowance,
or claim the transformation is complete. The remainder and images were requested.

The original OneDrive checkout is on `codex/neighborhood-presentation` at
`679b76a35`, eleven commits behind main, with substantial staged, unstaged and
untracked user work. It was inspected without changing its files or index.
Implementation must use the separate `C:/dev/CityPrompt-student-design-transformation`
worktree. No unrelated local worktree was merged or cherry-picked.

The audit read current AGENTS/CLAUDE, RLASM method/policy/human memory,
building publication workflow, September student/catalogue/ground/road/render
handoffs, performance and media reports, source consumers, and merged PR metadata.
Historical reports establish previous observations, not fresh acceptance.
The human building memory contains legacy scaling guidance; the newer RLASM
v6.1 exact-variant/native-clay contract has precedence. No method was changed,
so machine companions require no edits. August Wave 2 publication prose also
conflicts with supplied instructions: do not infer new publication authority.

Read-only inventory output is external:
`C:/dev-artifacts/CityPrompt/student-design-transformation/catalogue-inventory.json`.
The accompanying `inventory.mjs` imports current runtime registries through Vite
and reads canonical Git blobs. `inventory-summary.json` records source revision,
counts, validation and largest files. It inventories every canonical parent and
variant, declared dimensions/storeys/type/description, exact image URLs and tracked
angle siblings, reference visibility, placement IDs, clay bindings/review hashes,
park kit components, and executable street sections/selections. Missing data is
left missing; a reference image is not a detailed-model approval.

## Recent changes that must be retained

Merged PRs #14–#25 account for all eleven commits since the original checkout:

| PRs | Current foundation |
| --- | --- |
| #14–#16 | Student placement, desktop/tablet catalogue, occlusion-aware render controls, close-capture readiness |
| #18–#19 | Six published clay buildings and repeatable exact-byte catalogue promotion |
| #20 | Student editing, measured park terrain and automatic park alignment |
| #21 | Grounded catalogue junctions and bounded public-road connections |
| #22 | Three park publications and retained visible ground during tile refresh |
| #23 | Editing/deletion reliability, irregular parks, ground/camera/style fixes, GPT Image integration |
| #24 | Procedural road source/topology, certified RLASM repair, three tower activations |
| #25 | Same-capture three-engine render comparison default |

Commit dates and merge dates differ: #25 was authored September 9 and merged
September 10 UTC. Older “not published” labels in pilot documents do not override
the current main tree. Likewise, unpublished local showcase/experiment branches
do not become the authoritative product merely because they are newer.

## Canonical inventory

| Domain | Parents | Variants | Reference-visible parents | Primary placement cards |
| --- | ---: | ---: | ---: | ---: |
| Buildings | 224 | 896 | 223 | 11, covering 10 parents |
| Parks/open spaces | 130 | 520 | 130 | 7 |
| Streets/paths | 115 | 355 | 115 | 4 |

These counts were computed, not copied from CLAUDE's obsolete 97/36 counts.
Reference visibility comes from `archetypeReferenceAvailability.json` and is
not a fresh downloaded-byte check. The clay manifest has **9 runtime-enabled
deliveries**, totaling **55,296,804 declared model bytes**. The placement registry
also retains two earlier pilot building choices; do not relabel them as newly
published deliveries. Registry validation returned no errors.

Public-realm source contains **37 park family IDs**, **15 archetype-owned park
kits**, **5 executable street families**, and **20 street selection records**.
Multiple section sizes can share a variant, so selection records are not unique
archetype counts. The primary picker does not expose all of those capabilities.
Seven park cards include the neighbourhood park and six park-trio/sports choices;
their registry readiness remains `pilot`. Preserve the narrower provenance and
shape/terrain limits rather than changing labels to satisfy coverage.

## Complete product path and current seams

| Stage | Current source and behavior | Gap relative to this mission |
| --- | --- | --- |
| Select site | `features/projects/ProjectViewPage.tsx`, `GlobeSitePlannerMap.tsx`, `useSiteZones.ts`: project location, WGS84 boundary drawing, persisted zones | Site/Design/Present is not the primary navigation contract yet |
| Manual design | `SitePlannerToolbar.tsx`, `PlacementPalette.tsx`, `PlacementControls.tsx`, `GlobeEditMode.tsx`: building/park/street actions, hover preview, drag/corner/rotation editing | Palette opens in a modal and pauses the map; it does not stay visible while designing |
| Discover archetypes | Three canonical JSON libraries → `aestheticCatalog.ts` → advanced selectors; separate `pickPlace/assetRegistry.ts` → primary palette | Full reference vocabulary and supported placement vocabulary need one discoverable UI with honest capability states |
| Publish buildings | `tools/catalogue_promotion`, clay `library.json`, generated `publishedBuildingAssets.ts`, selective seeder/readback | Good automatic publication path; do not replace it with manually duplicated student records |
| Place/edit | `GlobePlacementPreview.tsx`, `geometry.ts`, `ReshapePanel.tsx`, `ProjectViewPage.tsx` | Plot containment/overlap feedback exists. Draft rotation is explicit; no general nearby-street auto-facing in this placement path. Height/type changes still require broader inspector flow |
| Compile Community 3D | `useAutomatic3D.ts`, `communityCompiler.ts`, `projectCommunityCompile.ts`, backend `lego_assembly.py` | Automatic compile is tied to current placement markers; broadening discoverability alone does not make arbitrary assets auto-placeable |
| Detailed buildings | Exact variant → approved library → assembly recipe → `GlobeLegoAssemblyLayer.tsx` / `GlobeBuildingModelsLayer.tsx`; `nativeClayPlacement.ts` preserves native scale | Unsupported dimensions/floors must explain planned massing before applying. General sibling substitution is forbidden |
| Parks | Backend `public_realm_lego.py`; `parkLegoFamilies.ts`, `parkArchetypeOwnedKits.ts`, `parkTrioLayout.ts`, `GlobeParkKitLayer.tsx` dispatch reviewed assemblies | Arbitrary component editing and all-family slope/irregular-shape support are not established |
| Streets | Canonical section profiles, `streetFamilyCatalog.ts`, fixed-section route editor, grounded junctions; new `road_source.py`/`road_network.py` for marked centrelines | Two legitimate contracts remain: detailed catalogue sections versus general procedural planning surfaces. Their detailed junction trimming is not unified |
| Ground/context | Prepared levels/terraces, shared Google measured grid, individual saved park grids, ECEF globe with local East/North/Up frames | Initial whole-site ground rejection can hide valid buildings. Visible Google surfaces are not bare-earth survey data |
| Camera | `useGlobeCamera.ts`, `authoredCameraGround.ts`, globe controls/pegman, capture manifests | Provider-independent coordinate identity and persistent cross-mode camera/route behavior need explicit tests |
| Still image | `direct3dCapture.ts` → `useDirect3DRender.ts` → API validation → backend render service/provenance/gallery | Strong source controls exist. Generative design fidelity and presentation quality still require matched-camera visual acceptance |
| Video | `deterministicVideoCapture.ts`, `videoRouteControls.ts`, `VideoGeneratePanel.tsx`, video API/services/fidelity | Deterministic source is implemented; generated temporal fidelity, actual output dimensions and route retention remain open |

Paths in this table under the globe live in
`frontend/src/components/viewer/globe/`; feature and hook paths are under
`frontend/src/`; backend services are under `backend/app/services/` unless noted.

## Grounding, datum and floating/sinking defenses

Keep these defenses together; removing one can reintroduce a different contact defect:

1. `sitePreparationSurface.ts` resolves one saved boundary ellipsoid level,
   per-zone terrace offsets and exact containment. It keeps backing below
   authored pavement and respects measured park terrain over prepared levels.
2. `SharedSiteGroundProvider.tsx` raycasts only original visible Google tile
   scenes. A fixed coverage camera, relevant-tile invalidation, bounded per-frame
   work, plausibility limits and two repeatable passes prevent root-tile and
   incomplete samples from masquerading as verified ground.
3. `sharedSiteGround.ts` uses the same piecewise planar triangles for all
   consumers. Current caps: 1,200 grid points, 0.08 m pass disagreement,
   0.6 m local residual and 0.45 shared-ground slope. This is a visible-surface
   quality policy, not proof of survey datum or accessible routes.
4. Display and verification contexts are separate. Same-source refreshes retain
   the last verified display surface; captures wait for fresh verification.
   Boundary/anchor changes deliberately invalidate that reuse. Initial failure
   has no retained surface, which explains the remaining wide-area visibility gap.
5. `buildingGroundContact.ts` samples actual transformed native footprints,
   edge/grid crossings and interior terrain vertices. Rigid buildings sit
   0.04 m above maximum contact with individual foundation skirts/caps; required
   skirts over 3 m fail unresolved. This prevents buried geometry but does not
   establish a usable entrance or an engineered foundation.
6. `terrainContactProfile.ts`, `importedBuildingGround.ts`, terrain anchor caches
   and per-model probes support older/imported/outside-site paths. They must be
   inventoried as compatibility consumers when centralizing surface resolution;
   do not silently reinterpret their stored heights.
7. `parkTerrain.ts` persists footprint-specific two-pass surfaces;
   `AutomaticParkGround.tsx` remeasures after edits using a bounded retry queue.
   Draft triangles keep lawn, paths and props coherent while measuring.
   Stale saved profiles are rejected; supported grid reuse does not extrapolate.
8. `streetSharedGround.ts`, `streetGroundExtension.ts`, `streetMesh3D.ts` and
   junction ground consumers drape sections/furniture over consistent triangles.
   Outside-road extensions reuse shared vertices and measure additional ground;
   they do not move the existing building grid.
9. `publicRealmDepthPolicy.ts`, prepared backing separation and detailed surface
   ownership prevent coincident pavement/paint/ground. `TileSpatialMaskPlugin.ts`
   clips geographic polygons rather than projected stencil walls, preserving
   context behind proposals. Capture depth/normal materials retain that clipping.
10. `sharedGroundCapture.ts`, street/park capture checks, backend
    `shared_ground_provenance.py` and source claims reject stale geometry before
    paid rendering. Keep uncertainty visible without calling it verified ground.

Developer diagnostics already include `window.__sharedGroundDiagnostics` and
ground review samples. Extend them into an optional contact overlay rather than
adding engineering terminology to the student UI.

For Lux Modus, first separate context display from an immutable design frame and
an explicit ground-surface contract. Preserve WGS84 design geometry, units,
vertical-reference provenance and saved elevations across provider switches.
Do not implement a guessed Lux file importer or geoid offset. A sample dataset
and its CRS/vertical datum are required before validating that adapter.

## Scene truth, persistence and compatibility

`community3d.ts` binds source zones to linked building IDs, generator, compile
timestamp and representation hash. Paid capture requires complete SHA-256 source
and representation claims. `api/v1/direct_3d_render.py` recomputes the claims
against server-current project data before credit admission. A source hash alone
does not prove that the mounted model is the intended representation.

Direct capture v2 includes beauty, class/instance masks, numeric depth, normals,
material IDs, projection/world matrices, position/quaternion/lens and fingerprint.
`useDirect3DRender.ts` reuses one captured source for provider comparisons. Current
same-camera style logic conditions identity on the captured model; do not restore
older catalogue-photo conditioning that encouraged geometry/material substitutions.
Render audit sidecars retain frozen scene/camera/output revisions and distinguish
provider originals from safety-source returns. Historical controls and current
presentation-first advisory behavior are different paths; inspect the selected
mode before claiming source-pixel restoration or automatic fidelity acceptance.

Video's 24 fps deterministic source clock uses frame index rather than elapsed
wall time. Geometry checkpoints and ordered camera controls supplement source
preview video. `video_fidelity.py` compares structure, protected regions and
temporal consistency; generated output remains review evidence. Near-field
routes have weaker checkpoint coverage. Existing reports record geometry changes
and 720p outputs despite higher-resolution sources.

Persistence is server-backed, not a single exported scene blob:

- SQLAlchemy `Project`, `SiteZone` and `Building` store PostGIS SRID 4326
  points/polygons plus JSONB properties/specifications, model/LOD URLs and links.
- `useSiteZones.ts` provides optimistic mutations, revision guards, project-scoped
  undo and idempotent request IDs. `zoneDrafts.ts` preserves unsaved creates per
  user/project in local storage, with an explicit memory-only fallback.
- `projectWriteQueue.ts` serializes same-tab authored/derived writes; server
  revision checks still arbitrate other clients. Ground background writes update
  revision state without creating misleading authored undo steps.
- `ZoneHistory` snapshots, stored terrain profiles, `pick_place_asset` IDs,
  definition versions, exact selected variants, centreline properties and
  compiled hashes are compatibility boundaries. A definition version is not an
  immutable model-byte pin, especially where old pilot revisions are null.
- Reference layers remain separate context. They must not become proposal zones,
  physical inventory, tile masks or extra planned quantities.

Changing IDs, reordering frontage vertices, deforming native GLBs, replacing
model URLs in place, splitting road parent zones, migrating old roads implicitly,
or recomputing saved heights from a different datum can break existing projects.
Additive adapters and explicit versioned migrations are preferable.

## KEEP

Keep Google context, source-locked RLASM/native clay, truthful planned massing,
canonical references and publication gates, curated park programs, metric street
sections, project write/revision/undo contracts, geometry capture/provenance,
reference-only layers, and opt-in planning/report capabilities. None needs a
parallel replacement to deliver the requested student workflow.

## EXTEND

Extend the existing catalogue adapters into one discovery surface; add tokenized
metadata/storey search; keep capabilities separate from visual references.
Extend placement preview with deterministic street-facing orientation and a
manual override shared by preview/save. Extend the selected-object panel with
four clear actions and representation impact before size/height/type edits.
Extend shared-ground lifecycle handling per footprint, terrain-aware entrance
anchors, saved source contracts and ground QA. Reuse current same-camera image
and deterministic video infrastructure for finite visual matrices.

## CONSOLIDATE

Consolidate the two catalogue search implementations and primary/advanced
browsing adapters. Consolidate ground precedence through one surface resolver
while preserving measured/display/verification distinctions. Connect procedural
road ownership with detailed section trimming incrementally, preserving source
zone IDs. Keep legacy Mapbox, imported models and older compiled recipes working
until their actual consumers have replacement tests; deletion is not this phase.

## SIMPLIFY UX

Make Site, Design and Present the primary navigation. Keep Buildings, Streets and
Parks visible in Design with a persistent palette on desktop and a compact tablet
layout. Treat top-down as a camera choice. Put providers, compile details, ground
diagnostics and source hashes in advanced/developer surfaces. AI suggestions stay
explicitly requested. Preserve saving/conflict/readiness messages because they
explain actionable state, but express them in student language.

## BUILD

Missing contracts: provider-independent context/design-frame boundary; per-object
ground uncertainty and entrance contact acceptance; stable per-house entrance
identity; safe representation-aware height/type controls; reviewed deterministic
family variation; full eligible catalogue discovery; live procedural snap feedback
and detailed junction ownership; the complete slope/reload regression; instrumented
scene performance and a measured final image/video acceptance matrix.

## RISKS and performance

- Ground thresholds are not tuning knobs for making a failing site pass. Preserve
  raw uncertainty and fresh-capture gates when keeping objects visible.
- Generic park replacement or automatic catalogue-wide variant mixing would
  violate reviewed identities. Explicit compatible family data is needed.
- Road planning topology and detailed band geometry have different guarantees.
  Procedural intersections still lack general detailed trimming and parcel clipping.
- Asset delivery is not reproducible solely from source presence. This audit's
  initial checkout exposed 794 historical ordinary-image blobs covered by LFS
  attributes. Their byte-identical checkout copies were removed only from the new
  worktree and sparse source checkout was used. Original user files were untouched.
  Fresh asset hydration/storage readback remains a release gate.
- September performance measurements are historical: full catalogue payload,
  large textures/models, continuous WebGL rendering and terrain raycasts remain
  areas to measure. No fresh FPS, GPU-memory or tablet claim is made here.
- Current largest files by Git bytes include backend `master_plan_2d.py` (266,928),
  render service (229,301), `ZonePropertiesPanel.tsx` (192,529), globe map
  (189,991), `useGlobeAIRender.ts` (173,809), and project page (99,910).
  Extract cohesive tested boundaries as needed; avoid a simultaneous rewrite.
- Existing local render reports cite account-specific model availability and
  provisional costs. Those are not current provider-access or pricing facts.
  Recheck the real account read-only before any separately budgeted live pilot.

## IMPLEMENTATION MAP and TEST MAP

Sequence coherent commits within this initiative; each slice has its own tests,
browser observations and evidence. Do not mix catalogue publication/compiler
generation into editor changes.

| Slice | Existing files to extend | Acceptance and regression evidence |
| --- | --- | --- |
| 1. Canonical discovery | `aestheticCatalog.ts`, `calgaryCatalogue/guide.ts`, `pickPlace/assetRegistry.ts`, `PlacementPalette.tsx` | All eligible IDs remain discoverable; no candidate promotion; metadata/number-word/storey searches; authoritative images; keyboard/tablet/persistent palette; registry/catalogue/palette tests |
| 2. Site/Design/Present | `ProjectViewPage.tsx`, `SitePlannerToolbar.tsx`, `StudioControls.tsx`, workflow helpers | Manual design remains primary; no unsolicited AI; undo/save/conflict controls reachable; existing workflow, toolbar, read-only and accessibility tests |
| 3. Placement/edit fidelity | `GlobePlacementPreview.tsx`, `geometry.ts`, `ReshapePanel.tsx`, `GlobeEditMode.tsx`, existing assembly API | Ghost equals saved footprint/orientation; street facing plus override; move/rotate/stretch/type/height; exact native or declared massing; place/edit/undo/reload and compiler regression |
| 4. Ground/context boundary | `SharedSiteGroundProvider.tsx`, `sharedSiteGround.ts`, `buildingGroundContact.ts`, `sitePreparationSurface.ts`, park/street surface consumers | Invalid footprint does not hide valid neighbors; no stale capture; explicit CRS/datum/provider provenance; change provider without moving proposal; ground lifecycle/contact/capture and backend provenance tests |
| 5. Street/park interaction | `streetPlacement.ts`, `streetSnapping.ts`, `road_network.py`, junction geometry, park layout/access modules | Finite T/X/unequal-width/acute cases; disjoint pavement and connected sidewalks; no props in paths/water/courts; source IDs and revisions survive reload |
| 6. Full slope gate | Existing Salisbury hillside fixture as candidate, then a disposable mixed project | Detached + mid-rise + tower + street/junction + park/trees/furniture; uphill/downhill/side/street/aerial; save/reopen; no float/burial or elevation drift. Prior park-only trials do not pass this matrix |
| 7. Present | `direct3dCapture.ts`, `useDirect3DRender.ts`, render API/service, deterministic video/camera controls | Frozen source/camera, masks/fingerprints/revisions, captured-source vs provider-output inspection, actual dimensions/temporal fidelity; no paid calls until missing budget is resolved |
| 8. Performance/release | Vite bundle checker, runtime manifest tooling, scene diagnostics | Fresh cold-load/frame/transfer/memory measurements with 20 buildings; context retained; current scene truth and reviewed identities preserved; real laptop/tablet and novice usability checks |

Relevant existing backend suites include `test_road_network*`,
`test_shared_ground_provenance`, `test_community_3d_scope`,
`test_building_community_freshness`, `test_direct_3d_render`,
`test_direct_3d_presentation_first`, and `test_video_fidelity`.
Frontend neighbors cover shared-ground lifecycle, terrain/contact, park profiles,
street ownership, capture, deterministic clocks, selection, placement, writes and
undo. Compiler/catalogue promotion suites become required only when those
contracts change. Each production TypeScript slice must also pass type-check.

## Verification in this audit

- Eight focused frontend suites: **65 tests passed** on unchanged main source
  (registry, catalogue, palette, Community 3D, shared ground, building contacts,
  procedural road adapter and deterministic video clock).
- `npm run type-check`: **passed**.
- Four focused backend suites: **61 tests passed** (road topology, shared-ground
  provenance, Community 3D scope and video fidelity), using the existing local
  Python environment. These tests do not establish live database persistence.
- Runtime registry validation: **no errors**; inventory imports completed.
- Fresh Vite on `http://127.0.0.1:5174`: sign-in page loaded, screenshot inspected,
  no captured browser errors. This is a shell smoke test only.
- At audit startup, expected local API/database/storage ports were closed.
  No authenticated placement/save/reload, real Google-ground slope regression,
  paid media call, provider comparison or production deployment is claimed.

Audit artifacts remain external; application source and canonical catalogues are
unchanged. The next checkpoint requires the remainder of the master brief and
its visual references to finalize the mission-wide gates. No push is authorized
or performed by this audit.
