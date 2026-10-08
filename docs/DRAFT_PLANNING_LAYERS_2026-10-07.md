# Additional draft planning layers

## Classroom use

The Site tab retains the current zoning, local area plans, MDP and CTP. Two
additional source editions are available without replacing those layers:

- Zoning map studio → **Draft bylaw · May 2025**: 27 choices (22 base zones
  and five variants), plus Custom. Draw inside a saved site boundary, select
  a district, save, and click the resulting polygon to read its purpose and
  open the source rules. Draft studies have independent save, undo, opacity
  and export state. The existing/proposed current-bylaw studies are separate.
- City-wide policy maps → **Calgary Plan · proposed May 2026**: eight map
  toggles, individual opacity, original legends, reading guidance and source
  page links. Viewing these maps does not require a site boundary.

The draft bylaw states that zoning maps are not included. Its drawing palette
is therefore explicitly illustrative, not an official City draft zoning map.
Reused codes such as MU-1 are tagged with their bylaw edition. Current-bylaw
catalogue matching and report comparisons do not evaluate the draft scheme.
This release adds classroom maps, not a draft regulatory compliance engine.

## Sources and map inventory

- [Annotated draft zoning bylaw, May 2025](https://www.calgary.ca/content/dam/www/pda/pd/documents/city-building-program/cbp.annotated-draft-zoning-bylaw-may2025.pdf)
  SHA-256: `be7585b88f7d80d54cd1f44c228bc97d3e1026a24a2d21056db35a0dfc0e7258`
- [Annotated proposed Calgary Plan, May 21 2026](https://www.calgary.ca/content/dam/www/pda/pd/documents/city-building-program/calgary-plan/calgary-plan-annotated-2026-05-21.pdf)
  SHA-256: `508588bb486bafa0a5dbd37e687c4c8182cdc24a1fcdfb83ef5ea2f7ae55fdca`

| Map | Title | PDF page | Printed page |
| --- | --- | --- | --- |
| 1 | City Structure | 25 | 21 |
| 2 | Downtown Streets | 26 | 22 |
| 3 | Natural Systems | 51 | 47 |
| 4 | Wheeling Network | 59 | 55 |
| 5 | Primary Transit Network | 61 | 57 |
| 6 | Road and Street Network | 63 | 59 |
| 7 | Goods Movement Network | 65 | 61 |
| 8 | Developing, Redeveloping and Industrial Areas | 83 | 79 |

Regional maps on PDF pages 93 and 94 are excluded because this annotated edition
marks them for deletion. Sources are pinned to the supplied editions; changing
the PDF requires review and recalibration.

## Extraction and spatial limits

`tools/policy_maps/tile_calgary_plan.py` extracts the embedded map artwork Form,
excluding page annotations, deleted prose and page furniture. The UI identifies
the proposed edition. It preserves original cartography and a separate original
legend, then generates transparent 512-pixel tiles and a low-resolution overview
using the existing policy-map loading pipeline. These are raster policy overlays,
not newly invented vector boundaries.

Citywide artwork was registered to the independently calibrated current MDP
Map 1 road network. Registration median residual was 2.75 m (75th percentile
5.35 m); this is a fit statistic, not a citywide accuracy guarantee. A separate
14 St NW / Kensington Rd NW road-junction check measured 5.51 m for the six
citywide maps with a road background. Downtown measured 12.92 m. The wheeling
map shares the citywide frame but has no measurable road-junction background;
its alignment was visually compared, without an independent numeric claim.
The maps remain generalized policy artwork, not parcel or engineering surveys.
Calibration and independent control coordinates are recorded in
`tools/policy_maps/calgary_plan_calibration.json`.

Rebuild with a Python environment containing PyMuPDF, NumPy, Pillow and pyproj:

```powershell
python tools/policy_maps/tile_calgary_plan.py --source <downloaded-pdf> --output <external-review-directory> --only 1
# Review the pilot before building the bounded eight-map packet without --only.
```

479 reviewed files (471 WebP assets and eight map manifests) are promoted under
`frontend/public/policy-maps/citywide-2026-v1/calgary-plan-*`. WebP assets use the
repository's existing Git LFS rule. Source PDFs, calibration experiments and
visual-QA screenshots stay outside Git.

## Verification

- Nine focused frontend suites: 68 tests passed, covering existing studies,
  draft save/round-trip/export, code namespace isolation, map controls, catalogue
  matching and report comparisons.
- `npm run type-check`: passed.
- Zoning-study API suite: 30 tests passed, including cross-edition rejection and
  draft persistence. Existing project ownership/concurrency checks are retained.
- Existing citywide-map tests: five passed; new proposed-map tests: three passed.
- Browser: all eight maps toggled, legends and PDF links inspected; map opacity
  changed to 50% and retained across hide/show. Draft MU-1 polygon drawn, named,
  saved, clicked and reloaded at 50% opacity. Existing proposed study retained.
- No paid image/video generation and no deployment performed.

Browser project: `eac6a0f5-61e6-4431-8706-5741dfc46ec7` (Shaganappi Gateway trial).
External evidence: `C:/dev-artifacts/CityPrompt/draft-plans-2026-10-07/`, including
`calgary-plan-browser.jpg`, `draft-zone-inspection.jpg` and `all-map-review.jpg`.

The local preview uses `CITYPROMPT_PUBLIC_DIR` at
`C:/dev-artifacts/CityPrompt/render-readiness-2026-10-07/assets-model-fix/public`.
The reviewed map packet was also copied there and the local frontend/backend
restarted. Other environments must retrieve the committed LFS assets and include
them in the served public directory. No new environment variables or database
migration are required.
