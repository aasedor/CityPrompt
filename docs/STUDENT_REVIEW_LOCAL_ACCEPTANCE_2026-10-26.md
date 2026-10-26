# Local student review — 26 October 2026

Integration branch: `codex/student-review-local-20261026`. No push or deployment.
The LuxModus handoff snapshot and private Drive delivery remain unchanged.

## Implemented and verified in automated checks

- Site Context and Policy groups reuse the existing lazy data state. Street names
  recover once from transient service failures and retain usable cached labels.
- Public reference features disclose their source attributes. Selections are
  pinned to a snapshot and clear on authored selection or incompatible tools.
- Existing City land use is read-only and independent of saved student studies.
  Proposed zones update their selected designation and colour immediately. The
  future-bylaw authoring tab is removed; legacy saved data is preserved.
- Entrance connection and optional walkway problems are advisory for placement
  and capture. Physical model contact and unknown integrity failures still block.
  Buildings attract to sidewalk edges; nearby straight junctions recover within
  3 m / 5 degrees before the original full geometric validation runs.
- Court-only options are grouped under four base sports without changing saved
  archetype identities. Brick Podium is the finite storey pilot: native 13 stays
  unchanged; 15–40 recommended, supported 13–40, with intact floor repetition,
  podium and crown. Other building contracts remain as authored.
- Immediate saved image results expose animation, including edited/local street
  results. Video routes support drawing, selection, moving/removing points,
  deletion and undo/cancel. Street POV and subject-relative follow framing differ
  from aerial movement.
- Photographic video finish defaults on. Free preview and readonly guide recovery
  perform no paid calls. Explicit Generate prepares/reuses an exact bound guide,
  checks combined credits first and preserves uncertain request identities. Saved
  guides can be reused on reopening with only video credits and images paused.
- The local launcher prepares schema, verifies routed worker queues, manages a
  recovery scheduler, and waits for operational readiness. Windows slash variants
  in owned PID paths are recognized. Durable jobs are enabled only in ignored
  local configuration, with the previous configuration backed up privately.

Combined frontend run: **244 tests / 27 files passed**, plus TypeScript. Related
isolated backend video integration: **117 passed, 2 optional service skips**.
Spatial verification: **226 passed**; tower/court verification: **81 frontend and
25 backend/Blender tests passed**. These suites overlap; counts are not additive.
Launcher Windows-path follow-up: **10 passed**. Actual local `/ready` reports
database, Redis, storage, image worker and reference worker ready. Recovery beat
dispatch and task completion were observed without any paid provider request.

## Browser acceptance completed

Disposable copy:
`http://localhost:5174/projects/246003b1-5062-421d-9ceb-d8133b2ec548`

The original Downtown project was not changed. Copy receipt and unchanged source
hash are recorded outside Git at
`C:/dev-artifacts/CityPrompt/student-review-20261026/qa-project-copy.json`.

- Site Context and Policy groups appear below the boundary step.
- Street names load successfully from the live City service.
- Existing land use loads actual `DC157D2025SITE1` as read-only. A proposal copied
  from City outlines changes to `C-COR1`, updates its label/colour, saves, and is
  retained when switching back and forth. Existing remains the official district.
- Historic resources load four nearby records. Clicking the visible point opens
  Graphic Arts (Western Printing) Building, address, year, style and designation
  fields, with its original source link.

## Remaining visual acceptance — do not describe as completed

Computer Use stopped because it could not establish the minimized browser's URL
with enough confidence for its safety check. No alternate UI route was used after
that restriction. DOM state had updated while screenshots/canvas frames were
stale, so a large grey occluder in one screenshot is not a verified model defect.
Read-only investigation confirms source/clone plans and served model hashes and
bounds agree; a geometry workaround is not justified without reproduction.

The ordinary live visual pass still needs: Brick 13→15→25→40, save/reload and
return to native 13; court option placement; building/sidewalk and intersection
snapping; optional-tool panels and drawing recovery; actual free video route
preview/edit/delete and follow-person framing; capture readiness with an entrance
advisory. No paid image/video generation was performed in this fix batch, so
provider output quality and a paid end-to-end Omni result are not verified.

Known adjacent broad-suite failures are older catalogue expectations in
`validationCatalogue`, `parkMatching`, `ZoningCatalogueCard` and
`canonicalParkPlacement`. Focused changed-feature suites pass. Runtime manifest
metadata can be regenerated in the sparse checkout; that does not establish full
release asset hydration. No release readiness is claimed.
