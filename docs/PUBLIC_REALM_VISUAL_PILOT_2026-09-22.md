# Public-realm visual pilot — 2026-09-22

Local paired park/greenway initiative on `codex/public-realm-visual-pilot`,
based on `c924a3ac0`. This is a practical prototype improvement, not human visual
approval or a catalogue-wide activation. No paid image generation was used.

## Exact scope

- Street: `neighborhood_greenway` — finer procedural pavement, restrained relief,
  closer tree stations (14 m; existing cap of 16 trees), and blade-based planting.
- Park: `neighborhood_park_v2` (Natural Meadow) — pale aggregate paths, narrow
  edging, quieter material boundaries, 1024 px procedural ground, and bounded
  planting drifts in the two existing meadow rooms. Other park variants retain
  their current finish. Existing AI ground images are not regenerated.
- Shared opt-in geometry: deterministic vertex-coloured leaves and grass blades,
  no new texture downloads. Grass uses 104 triangles; each plant stays below
  400 triangles. Plant height is specified in metres independently of footprint.

Drifts consider at most 96 clumps, with eight instanced plants per accepted
clump. Full clump envelopes stay inside the parcel and clear paths, fixed props,
and existing microdetails. They use shared terrain samples at the centre and
four corners; unsupported or more than 0.18 m uneven samples are rejected.
An explicitly prepared site can use its existing local zero datum. Natural
terrain without support does not receive a fabricated zero-height fallback.

## Verification and evidence

Browser: localhost:5176, backend:8002, 1264 × 625 desktop viewport, existing
disposable project `54818ada-581f-4643-900a-78867b076c8c`,
“Currie Empty Lot — Sol Catalogue Trial”. The previously vacant irregular
Currie parcel contains four buildings, this greenway, this park and a rain garden.
This pass reviewed that saved mixed scene; it was not a new student-authoring run.

External local evidence directory:
`C:/dev-artifacts/CityPrompt/sol-empty-lot-trial-2026-09-22/browser/`

- `60-public-realm-before.png`: original aerial.
- `65-park-close-top.png`: previous thick park path outlines.
- `70-greenway-final-detail.png`: updated street close view.
- `71-public-realm-exact-export.png`: completed free exact-view capture preview.
- `72-meadow-latest-detail.png`: latest metric-height plants and park path finish.

These are local review files, not a durable shared evidence package. The capture
preview was visually reviewed; downloaded-file delivery was not tested here.

| Gate | Result and limit |
| --- | --- |
| C1 Exact identity | Confirmed through saved project readback; IDs above |
| C8 Tiles visual review | Close and aerial review completed; exact capture preview works; no AI comparison |
| C6 Reopen | Reload smoke passed; edit/Undo/save matrix not repeated |
| C3 / P2 terrain | Prepared-site visual smoke and support logic only; natural-slope browser matrix NOT TESTED |
| S4 / P1 clearance | Narrow placement regressions passed; exhaustive live clearance review NOT TESTED |
| Other runtime gates | NOT TESTED in this visual-only pass; prior evidence is not promoted |

Six focused Vitest files passed (185 tests): plant geometry/surface finish,
meadow drifts, street materials, park microdetails, street furniture and park
ground profiles. `npm run type-check` passed. No backend changes.
Browser error extraction returned empty error entries, so console cleanliness
is not asserted. No crash or React error overlay was observed.

## Reusable direction and next checkpoint

Use material-scale paving, restrained colours, fine edging and botanically
legible instanced planting. Keep clear central lawns and deliberate planted rooms.
Separate height from footprint and preserve existing clearance/ground rules.
Review both close and aerial Google Tiles views before any AI enhancement.

Remaining visible limitations include basic legacy park furniture/program pads,
stylized tree leaves and the coarse surrounding prepared-site landscape. Next:
review this pair with the user, improve one coherent park amenity kit, then adopt
the shared components in a bounded next pair. Do not enable detailed planting
across every variant without reviewing its scale, budget and terrain support.

The [next furniture checkpoint](MEADOW_FURNITURE_REVIEW_2026-09-22.md) replaces
the meadow variant's bench, picnic table, bin and lights with a coordinated,
bounded procedural kit. It retains the small-park pavilion limitation and
records the incomplete browser-download verification explicitly.
