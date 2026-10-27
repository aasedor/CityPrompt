# Student review fixes — local acceptance

User approved implementation and testing of the reported issues on 2026-10-26.
The existing LuxModus package remains a separate, frozen handoff. No push or
deployment is part of this initiative.

## Implementation units

1. **Site information and controls:** recover street-name loading; inspect public
   data features; make existing land use an official read-only view; edit proposed
   zones immediately; remove the future-bylaw tab; group Site Context and Policy;
   audit optional tools and connect animation to immediate image results.
2. **Placement and capture:** explain entrance clearance, allow buildings beside
   sidewalks, make entrance/route defects advisory for image capture, and repair
   near-valid intersections with bounded geometric snapping before validation.
3. **Catalogue and towers:** group court-only variants under their base sports;
   preserve saved identifiers; pilot authored-floor repetition for Brick Podium
   tower with native podium/roof/material identity and a supported storey range.
4. **Video:** photographic finish defaults on; free preview stays free; explicit
   generation prepares/reuses a bound Sunburst guide and sends it with the exact
   route video; quote combined cost first; repair local worker readiness; provide
   simple route drawing/editing/deletion, automatic follow-person framing and
   distinct aerial/POV/cinematic movement.

## Verification

Each unit starts with regression tests for the reported behaviour. Run narrow
Vitest/pytest/compiler tests and TypeScript checks as appropriate. Integrate
coherent commits, inspect diffs, then test the combined localhost student flow in
a disposable project. Verify persistence/reopening as well as first use. Record
provider-dependent limitations honestly; no paid call on mount, toggles, preview,
or automatic retries. Keep generated assets in ignored output or artifact storage.

## Acceptance checklist

- [x] Street names load and recover.
- [ ] Entrance placement passes; malformed-anchor paid capture remains untested.
- [x] Public-data points disclose their records.
- [x] Selected proposed zone changes label/colour immediately.
- [x] Existing official land use is read-only; no future-bylaw editing tab.
- [x] Site Context and Policy groups organize the existing controls.
- [x] Supported tower storeys retain detailed authored geometry.
- [x] Court variants appear under their base archetypes.
- [x] Buildings can meet sidewalks without an artificial exclusion gap.
- [ ] Image results expose Animate render.
- [ ] Local Omni readiness is operational without weakening production controls.
- [x] Free aerial, street POV and follow-person routes have the intended framing.
- [ ] Photographic finish defaults on; paid guide preparation is not exercised.
- [x] Routes can be drawn, moved, shortened and deleted; incomplete routes explain the next step.
- [ ] Optional student tools work or explain an actionable prerequisite.
- [x] Near-valid intersections snap safely into complete junctions.
- [x] Combined automated checks pass; browser limits are recorded below.

## Repair acceptance — 27 October

The disposable QA project is `246003b1-5062-421d-9ceb-d8133b2ec548`.
The original Downtown Lux Modus project was not changed. Evidence is outside
Git in `C:/dev-artifacts/CityPrompt/student-review-repairs-20261027/` and in
the private [Drive retest folder](https://drive.google.com/drive/folders/1eMF7-3PcNLOVCJBzrcQWtxiFM7ISaqKH).

- Tower: ordinary browser edits to 15/25/40 storeys retain detailed geometry;
  40 survives reload and return to native 13 succeeds. Fixed plot dimensions
  are disabled and resize corners are absent.
- Junction: a new 57 m Neighbourhood Cycle Street joins the existing separated
  walking/cycling greenway, saves, renders and survives reload. The actual
  saved native greenway fixture covers its asymmetric cycle-track offset.
- Legacy volume: no detailed original model ever existed for the custom
  three-storey brownstone prompt. Recovery explains this, requires an explicit
  supported choice, checks every module against the actual tapered plot, and
  preserves the custom design on cancel/failure. Explicit Halifax at reviewed
  85% footprint saves a detailed model; Undo, Redo and reopening pass. Exact
  boundary contact is allowed with a 10 micrometre numerical seam, while
  genuine spills and concave-notch crossings remain rejected.
- Initial camera: the actual blocker arrived after coarse display readiness.
  An event-driven initial visibility watch now adjusts only an obstructed
  view, stops for user/capture ownership, and is bounded to 120 seconds,
  60 checks and three corrections. Fresh untouched reload reached a clear
  75-degree view after detailed context arrived. All diagnostics were removed.
- Road context: transient provider failure tries one independent read-only
  mirror, each response has an elapsed eight-second budget, and the overall
  lookup has a 20-second budget. Only successful data is cached; a failed
  refresh removes stale snap targets. Current public-provider outage remains
  external; manual drawing still succeeds. Calgary centreline data was not
  substituted because its access/grade/width metadata cannot certify safe
  connection suggestions.
- Restart: launcher restores the configured isolated containers, external
  hydrated public root, API, worker and beat without failing on expected
  Windows native-command stderr. Actual launcher readiness passed.
- Final video retest: a newly drawn two-point aerial route produced a
  four-second, 96-frame 1280 × 720 H.264 preview and played to the end. Omni
  readiness and the combined photographic-guide quote enabled Generate;
  no paid submission occurred. Delete route cleared the preview and reopening
  the editor showed zero points. The optional preview MP4 was not delivered:
  the browser's blob-media export was unsupported and the ordinary download
  returned no completed file within 20 seconds. Eighteen screenshots and the
  review note were uploaded to Drive and all 19 files verified private by
  metadata and folder readback. Local delivery receipts record their IDs.

Final verification: 3,879 frontend tests passed, one skipped, across 465 passing
files; TypeScript passed. All 291 relevant backend tests and 16 launcher tests
passed. An earlier full frontend run timed out in
`validationCatalogueUI.test.tsx` under concurrent load; its isolated run and
the final complete run with two workers passed without changing the timeout.
The intentional unavailable-model fixture logs an error as part of its test;
the final run has zero failed tests. No push, deployment, paid generation,
credit purchase or catalogue publication was performed.

The earlier 18-item browser review now has 13 complete passes and five partial
checks: paid malformed-entrance rendering, paid animation of an existing image,
paid Omni output, automatic paid photographic-guide submission, and complete
ground/cleanup-tool application. Free readiness/preview checks do not certify
those paid or unexercised outcomes. The earlier review is preserved separately;
screenshots of superseded failures in this new batch are labelled by the
review note rather than presented as current failures.
