# AI Master Planner: archetyped Community 3D contract

Date: 2026-07-21
Branch: `codex/ai-lego-only-planner`

## Outcome

The AI Master Planner now treats the accessible runtime LEGO library as its
building catalog. It no longer assumes that a frontend render card or a
completed Meshy cache row means a detailed 3D building can be built.

The Site Boundary **Generate Community** action now runs the LEGO Community 3D
compiler. It does not call the legacy `/generate-all` Meshy workflow. The
existing colored-polygon rendering workflow and the general/manual Community
3D massing fallback remain unchanged.

## Executable building catalog

`master_planner/lego_catalog.py` derives a deterministic capability catalog
from the `ModelLibraryEntry` records accessible to the project owner:

- project-owner entries plus public entries;
- enabled LEGO metadata only;
- complete modular families, or exact fixed assembled variants;
- every advertised parent/variant and storey count proven through
  `plan_vertical_assembly` at the catalog footprint;
- a stable SHA-256 capability fingerprint.

The catalog distinguishes parent aliases from exact variants. This matters for
fixed landmark families: some can assemble only when their exact source
variant and native storey count are requested.

Each selectable parent or variant also carries the native width/depth proven
for that exact runtime asset. The catalog fingerprint includes these
dimensions, so a dimension-changing reimport invalidates an older cached plan
just as reliably as adding or removing a family.

The backend planning-dimension table was synchronized with the existing
`london_heritage_mansion_block` frontend catalog entry so that the imported
London LEGO family remains selectable.

## Planner and geometry guarantees

When a runtime LEGO catalog is supplied:

1. The Anthropic tool schema requires an exact parent archetype for all five
   planning bands and exposes only runtime-proven parent IDs.
2. Validation fills missing bands, replaces unavailable IDs, selects an exact
   variant when necessary, and snaps storeys to the chosen identity's proven
   floor set.
3. Provider failure uses a complete deterministic LEGO-constrained plan; it
   never falls back to the unrestricted scenario building palette.
4. The geometry palette carries the parent allowlist, variant allowlist, and
   exact selectable-ID floor map. Normal resolution, per-bar variety, and
   district-height re-resolution stay inside that inventory.
5. Cached Master Planner specs carry the capability fingerprint. An import,
   removal, or executable-dimension change invalidates the old palette and
   causes revalidation/recomposition. A catalog is requeried immediately
   before final binding; a mid-generation inventory change fails safely before
   the previous plan zones are replaced.
6. AI parcel sizing uses exact selectable LEGO dimensions. Narrow modules are
   tiled as native, independently compilable cells, uniformly reduced only
   within the production 0.8-1.0 fit range. The geometry does not stretch a
   small facade to consume a whole block; unused land remains available to the
   residual landscape. Meshy cache measurements are not consulted.
7. Rectangular recipes accept an exact quarter-turn when the browser reports a
   polygon's long axis as width but the authored module stores that axis as
   depth (for example, an 8 x 15 m rowhouse measured as 15 x 8 m). The asset's
   authored proportions and texture axes remain intact.
8. Per-bar alternates are filtered against the carved cell before emission:
   they must preserve exact floor support, accept the cell directly or at a
   quarter-turn, and remain inside the bounded 0.82-1.18 safety envelope.
   The generator revalidates the selected identity on every emitted cell so a
   stylistic alternate cannot silently become a geometrically incompatible
   building.
9. A final pre-persistence binding pass mirrors the browser's footprint
   measurement and runs the LEGO planner against every actual generated
   polygon. A stretched or clipped parcel is deterministically rebound to the
   closest stylistically compatible family that fits. Small clipped slivers
   with no valid family are omitted within a strict 10% building-count / 5%
   footprint-area budget and reclaimed by residual landscaping. Exceeding
   either bound fails before replacing the previous zones.

If no executable LEGO family is accessible, the AI plan fails with an
actionable import message instead of drawing buildings that Community 3D would
silently downgrade.

## Parks, streets, and residual landscape

All generated public-realm zones now persist explicit archetype identities:

- signature parks, pocket parks, greenways, plazas, ponds, and courtyards have
  a `green_space_archetype_id`;
- spines, locals, paths, lanes, roundabouts, locked-network fallbacks, and
  numerical street residues have a `road_archetype_id`;
- remaining site-boundary land continues through the residual-landscape kit.

This makes the public realm deterministic at the backend boundary rather than
depending on a later frontend inference.

## Atomic Site Boundary compile

The shared `compileBoundaryCommunity3D` entry point reloads authoritative zones,
limits work to zones inside the selected boundary, and preflights every
building. If any building lacks a detailed LEGO recipe, nothing is persisted
and the user receives an actionable error. This strict behavior is opt-in for
the AI/Site Boundary path; legacy/manual Community 3D retains its established
mixed detailed-model/planned-massing behavior.

Project-scoped browser planning uses the same inventory as the background
planner: project-owner private modules plus public modules. An editor's own
unrelated private library cannot change the family chosen for somebody else's
project. After the atomic compile, the strict client also verifies that every
requested building returned exactly one `lego_assembly` result and rejects any
Meshy, planned-massing, missing, duplicate, or extra building response.

Site-preview layouts are validated before any layout mutation. The current
preview handoff supports exactly one building per source zone; a multi-building
preview is rejected before `applyLayout`, and lightbox/history failures remain
open for inspection and retry. When that one-building preview is applied, the
compiler plans against the linked Building's authoritative footprint rather
than the larger developable parcel. This compiler-local geometry handoff keeps
recipe dimensions, center, orientation, and the globe-mounted Building aligned
without changing the persisted parcel or the Classic polygon pipeline.

AI-bound recipes carry the runtime catalog fingerprint from plan zone to
browser recipe. Under the project mutation lock, both batch compilation and
single-building Place/Rebuild lock the relevant module rows, recreate the
catalog, and re-plan the exact recipe before any Building mutation. The locked
re-plan uses the same deterministic `allow_setback=False` policy as the AI
binder and browser compiler. Manual recipes omit the fingerprint and preserve
their historical behavior. The single-zone composer is also project-inventory
aware, so shared-project editors cannot accidentally plan from their unrelated
private modules.

Plan redraw and compile also share an explicit artifact-ownership rule. A
generated Building is eligible for automatic cleanup only when its
`community3DRepresentation` contains the complete compiler stamp: schema,
known generator, valid source-zone UUID, compile timestamp, and a SHA-256
representation hash. Redraw removes those owned artifacts before replacing
their source zones; compile removes marked artifacts whose source zones no
longer exist. Unmarked, malformed, and user-created buildings are preserved,
and compile cleanup participates in the same atomic transaction as placement.

New compiler-owned Buildings explicitly persist the renderer's neutral
`rotation_degrees=0.0` before their representation fingerprint is stamped.
This avoids a false stale result caused by the database insert default becoming
visible only after flush.

## Direct 3D rendering isolation

The globe render panel now has two explicit source contracts:

- **Classic Polygons** continues to receive the augmented colored-zone source
  used by the established multi-preview pipeline, including its existing style
  catalog and optional geometry-accurate model checkbox.
- **Direct 3D** receives only authoritative persisted proposal zones plus the
  compiled Building snapshots. It captures the visible LEGO buildings, park
  kits, street kits, and site-boundary residual landscape in one
  geometry-conditioned call. Legacy unlinked models can remain visible as
  context, but cannot claim proposal pixels or mask current AI geometry.

The paid Direct preflight locks the project and verifies every zone source hash,
Building link, generator-specific representation hash, and residual-landscape
claim against current database state. Source and representation fingerprints
are mirrored onto the mounted Building snapshot so a mixed refetch cannot be
accepted. Turning detailed models off immediately reveals colored massing and
disables Direct 3D, while re-enabling or reloading remounts the LEGO layers.

## Live runtime pilots

Two fresh projects were converted in the local 5175 runtime with one Google
Tiles tab:

- **Stress pilot — 2.55 ha:** 46 LEGO buildings, 6 parks, and 13 streets. The
  final binder reported 46 unchanged, 0 repaired, and 0 omitted buildings.
  All recipes used `lego_assembly`; no current-plan Meshy or planned-massing
  fallback was persisted. Browser QA showed `Assembled 46 · No family 0 ·
  Skipped 0` and a 1280 × 720 Direct capture with 18.9% proposal coverage.
  Residual landscaping filled 7,288 m², and all 65 physical representation
  fingerprints were current after the rebuild.
- **Common pilot — 1.60 ha:** 5 LEGO buildings, 2 parks, and 7 streets from the
  Environmental scenario (12,256 m² GFA). All five Buildings are linked and
  carry `lego_assembly`; database checks found zero Meshy references and zero
  planned-massing records. Native fit scales ranged from 0.99286 to 1.0. The
  residual kit landscaped 5,570 m² of otherwise un-authored parcel with four
  deterministic context-aware trees.

The common pilot was reviewed at 30° oblique, 63° steep, and 90° overhead,
then through model off/on, reload, plan-overlay changes, LEGO Builder, Direct
capture, and Classic-panel selection. Its focused 1280 × 720 Direct capture
classified 11.1% proposal pixels (ground 1.6%, landscape 0.1%, street 3.6%,
park 2.3%, building 3.5%). A close photoreal Direct result retained 92.3%
registration, 99.8% building edges, 98.6% semantic edges, 0 exterior delta,
0.4/0.8 px translation, and -0.04° rotation.

## Verification contract

Before promotion, verify:

- focused Master Planner, capability, placement, geometry, and LEGO assembly
  backend suites;
- focused Site Boundary routing and Community 3D frontend suites;
- TypeScript type-check and production build;
- live runtime capability inventory;
- a fresh AI Master Plan to LEGO Community 3D conversion in one Google Tiles
  tab, reviewed at approximately 30°, 60–75°, and 90°;
- zero planned-massing or Meshy fallbacks on the strict boundary compile;
- no regression to the colored-polygon render pipeline.
