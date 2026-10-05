# Student zoning studies — local checkpoint, 2026-10-05

Initiative: `codex/student-zoning-studies-2026-10-05`, following the site
reference and classroom bundle checkpoints. The user's clarification was
**both existing and proposed conditions, as separate map layers**.

## Result

- Site tools and the Layers drawer open a lazily loaded zoning map studio.
  Existing-condition graphics and proposed land-use studies have independent
  geometry, shared saves, device drafts, undo/redo, and visibility.
- Copy clipped Calgary district outlines into an editable graphic, or draw
  3–128-corner zones. A proposal can also copy the existing study. Copies and
  replacements can be undone. Polygon clipping retains source holes and
  supports concave sites and split results.
- Change labels and colours, drag outer corners, move a selected corner by
  one approximate metre, or remove a zone. Source outlines with more than 128
  outer corners remain available for styling; draw a simpler replacement to
  reshape them. Hole outlines are retained, not independently dragged.
- Deterministic SVG and PNG exports use the chosen geometry and colours, an
  irregular site edge, labels, legend, north arrow, approximate metric scale,
  and an explicit student-concept caption. Zone graphics are visually clipped
  to the current site. SVG preserves full labels in titles; visible long text
  is abbreviated. PNG is bounded to six megapixels and 2,600 pixels high.
- Saved studies appear as coloured reference overlays. They do not intercept
  drawing or enter direct scene captures. Official districts, development
  SiteZones, terrain, and assessed values remain independent.

## Recovery and shared edits

The two shared documents reuse ReferenceLayer storage; no migration is needed.
Each save requires project editor permission, the active saved boundary, its
current geometry, and the previously read content hash. Project, boundary, and
reference-layer locks serialize conflicting writes. A changed or removed shared
layer returns a conflict, preserving the student's draft. Reloading the shared
version is explicit and undoable.

Device drafts are scoped to account, project, boundary ID, boundary coordinates,
and condition. Storage is debounced; unmount, immediate reload, and pagehide
flush the latest draft. Malformed/oversized drafts are ignored in favour of the
shared document. Storage failures disclose that the draft is only in the tab.
Undo/redo retains 30 changes per condition within the open editor; history is
not a shared version archive. A successful save uses the server-normalized
document as its clean baseline.

If the site changes, the earlier study is flagged. Students can explicitly clip
its geometry to the current boundary before saving. The original boundary's
device draft stays under its original key. Saving rejects invalid or crossing
polygons, invalid holes, blank labels, duplicate IDs, and out-of-site geometry.
Overlapping zones are permitted and disclosed as stacked drawing colours.

Limits: 256 zones, 32 rings per zone, 4,096 points per ring, 50,000 points and
2 MB per study, and a 25 km² site. Existing project limits remain 20 reference
layers and 12 MB. These bounds are safeguards, not laptop performance benchmarks.

## Verification

- Frontend: `ZoningStudyEditor.test.tsx`, `zoningStudy.test.ts`,
  `useReferenceLayers.test.tsx`, and `referenceGeometry.test.ts`: 18 passing.
  Includes condition isolation, shared revision submission, conflicting-save
  recovery, immediate reload/pagehide flushing, damaged-draft recovery,
  normalized labels, undo, viewer restrictions, clipping, holes, and SVG escaping.
- Backend: `test_zoning_studies.py` and `test_reference_layers_api.py`:
  26 passing. Covers permission checks, active/saved boundary checks, isolated
  slots, conflicting/removed revisions, shape validation, and overlap warnings.
- TypeScript, touched-component ESLint, map-enabled production build, bundle
  budgets, and whitespace review passed at the final checkpoint.
  The editor is a separate approximately 16 kB minified lazy chunk (6.2 kB
  gzip); the initial app shell stays 455.2 KiB. Total JavaScript remains below
  the existing 8,448 KiB budget. This measures bundle size, not frame rate or
  concurrent classroom readiness.
- Browser: isolated local dev port 5178, backend 8009, production preview 5179.
  Disposable project `Zoning and assessment classroom trial` at Currie Barracks.
  Seven Calgary district polygons saved as the existing study. A six-corner
  housing zone and a seven-corner park were drawn and styled as a separate
  proposal. A page reload recovered the unsaved proposal; both conditions then
  saved independently. Dragging, physical-corner selection after clipping,
  precise movement, and undo were exercised through the visible UI.
- Downloaded SVG parsed as XML; exported PNG verified as 2,000 × 1,580 pixels
  and visually inspected. The browser's download-event watcher did not report
  the blob download, but both actual files appeared in Downloads and were
  copied to the external evidence directory.
- Production editor checked at an 820 × 1,180 viewport: stacked controls and
  scrolling worked, no horizontal document overflow; precise movement and undo
  passed. This is responsive desktop emulation, not physical iPad/Safari or
  touch-device certification. Temporary viewport override was reset.

Browser screenshots and exported maps are outside Git at
`C:/dev-artifacts/CityPrompt/overnight-2026-10-04/`:
`student-zoning-studio.jpg`, `student-zoning-tablet.jpg`, `student-proposal.svg`,
`student-zoning-production.jpg`, and `student-proposal.png`. The final production
studio restored both saved conditions after reload and reported no console
errors. Source changes only belong in the commit.

## Limits and remaining work

This is a local review checkpoint, not a deployment or 40-student hosted trial.
The existing Currie terrain-alignment warning is still visible; these map
overlays make no claim about verified ground heights. No paid image/video
generation, catalogue activation, Git push, or change to the user's dirty
primary checkout was performed.

Next independent initiatives remain catalogue search/facets; finite adaptable
park pilots; style refinement and matched-camera examples; landing-page refresh;
hosted load testing; and later camera-path/video quality. The user's separate
button-cleanup session stays separate. New candidate archetypes still require
their explicit visual approval and runtime acceptance before activation.
