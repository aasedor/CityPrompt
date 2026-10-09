# Student workflow and release checkpoint — 8 October 2026

Branch: `codex/student-workflow-release-checkpoint-2026-10-08`.
This consolidates the recent application work for Git review. It does not activate
unreviewed catalogue candidates, change the production branch or deploy CityPrompt.ca.

## Changes completed in this pass

- `e8ba32909`: assessment evidence is saved in project metadata against the exact
  active boundary. Reopening restores the result without another Calgary query.
  An explicit refresh updates it; changed geometry cannot reuse a stale total.
  Owner/editor writes preserve other project metadata, viewers only read saved
  evidence, and a boundary changed during lookup is rechecked before persistence.
  Reports include the matching whole-property and prorated estimates with their
  assessment year, retrieval date, coverage and source. No database migration.
- `b9ed345a9`: transportation sampling rejects detached tile hits and implausible
  Calgary heights. Unknown points remain hidden until measured; rejected values
  are not replaced by invented elevations. The broad Calgary-only 500–2,000 m
  guard is an outlier safeguard, not a surveyed terrain accuracy claim.
- `ffe5e37d9`: drawing a zoning study over an existing building no longer cancels
  drawing and selects that building.
- `482770187`: independent project details and paving remain visible in scene
  captures as fixed context. They are metadata-authored objects, not zone-owned
  instances; the capture no longer incorrectly demands zone identifiers from
  them. They are not individually represented in the AI proposal instance mask.
- `d497f7291`: apply the existing lossless catalogue packing to reference
  signatures and the validation roster. All fields survive browser decoding.

## Browser evidence

Tested the existing **Crossroads Plaza · detail accuracy trial** project
(`9577e98b-99a9-4d1a-a78b-fd973acadc13`) at localhost:5183 with backend:8011.
This was a bounded workflow regression trial, not a new complete student project.

- Calculated and restored after reload: three assessed properties, 2026 roll,
  97.57% mapped coverage, $10,641,230 whole-property assessed value and
  $9,568,262.47 prorated site estimate. The map displays the rounded site estimate.
  Retrieval is dated 9 October UTC / 8 October locally. This is existing-property
  assessment evidence, not an acquisition price or valuation of the new design.
- Moved a basketball park with keyboard input, exercised Undo/Redo, deleted it
  and restored it with Undo.
- Reproduced the zoning-over-buildings failure, then drew and saved a four-corner
  MU-1 study across placed buildings. Clicking the study opened its zoning
  information instead of the site boundary. The saved study survived reopening.
- Generated a new report containing the MU-1 comparisons, partial zoning overlap
  findings and saved assessment metrics. No approved LAP in the current collection
  covers this site; the report correctly retains that limitation.
- Entered Walk, moved and turned within the plaza. This does not certify every
  interior, stair or slope, and no laptop frame-rate benchmark was performed.
- Reproduced the detail capture failure, repaired it and downloaded a 2,048-pixel
  wide original 3D PNG through the preview's Download control. No paid image or
  video generation was submitted; account balance remained 8,774 tokens.
- The earlier assessment report downloaded successfully as HTML and its amount
  and source were checked. A later report was confirmed in the UI and after
  reload, but a second HTML download was not confirmed on disk. Do not count
  repeated download attempts as successful exports.
- A final CTP-1 geometry sample had 1,436 grounded segments, maximum segment
  length 19.48 m and zero segments over 100 m. Earlier bad samples had generated
  kilometre-long spikes. The oblique screenshot showed no corresponding spikes.
  This is a local sample, not exhaustive validation of every City vector feature.

## Verification

- Assessment/report backend: 54 focused pytest tests passed.
- Project details backend: 16 tests passed.
- Policy/reference/report frontend: 176 tests passed; drawing follow-up: 24;
  detail/capture/paving follow-up: 39; catalogue consumer follow-up: 20.
  These are separate runs with some overlapping coverage, not a full-suite total.
- TypeScript passed after production TypeScript changes.
- Nine Node packing tests passed, including exact decoded equality for all eight
  packed JSON files. The two additional data files decoded in about 4 ms each on
  this desktop; this is not a low-end laptop timing claim.
- Configured Vite build and existing budgets passed: initial JS 471.2 KiB,
  total JS 8,407.9 KiB / 8,448 KiB, largest chunk 2,403.1 KiB / 3,584 KiB,
  CSS 171.6 KiB / 175 KiB. Total JS has about 40 KiB headroom.
- The first build omitted the Maps key and tree-shook globe code. Its smaller
  output is not valid release evidence. The final check explicitly supplied a
  placeholder Maps key and HTTPS API origin to include the full globe.
- Builds used an empty public directory and placeholder configuration: they
  verify source compilation and budgets, not deployable asset delivery.

Screenshots, PNG/HTML exports, logs and builds are outside Git at
`C:/dev-artifacts/CityPrompt/assessment-persistence-2026-10-08/`.
Use `verified-site-maps.png`, `proposed-zoning-selected.png`, `community-export.png`
and the original `planning-report.html` as the scoped evidence described above.

## Remaining hosted release work

Follow [the staging runbook](RENDER_RELEASE_2026-10-07.md), using
`render.staging.yaml`, not the legacy production Blueprint.

1. Resolve exact-byte human activation for the 19 existing local-trial model
   records. The metadata publication check still rejects those records. The
   ordinary local byte check also encounters unhydrated LFS model files; runtime
   tests use the verified external catalogue packet. No flags were bypassed.
2. Rebuild and audit a current full asset packet from the approved clean commit.
   The older 7 October packet is not proof that the newer standalone details and
   transportation assets are ready on a remote host.
3. Configure the actual Render staging services, restricted browser key, private
   storage, workers, queues, database and spending limits. Provisioning requires
   the actual account configuration and agreed infrastructure budget.
4. Back up production data/media and decide the data transfer before any live
   upgrade. A Git push does not move desktop projects or database contents.
5. Test hosted assets and the full student workflow on representative Windows,
   Mac and iPad hardware, then run the 40-session rehearsal. Keep paid quality
   trials finite and deliberate. None of these capacity checks is yet complete.

The separate building-family worktrees and unapproved expansion waves are not
part of this checkpoint's publication approval.
