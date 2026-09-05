# Calgary catalogue: recovered research and reconciliation

Reviewed September 5, 2026 on `codex/calgary-catalogue-guide`. This records
research recovered after the first catalogue-guide implementation, the small
corrections applied, and the decisions that still need implementation. Earlier
research is evidence of prior decisions, not a new instruction to run old scripts,
publish work or treat draft documents as adopted standards.

## Research locations

| Record | Location and scope |
| --- | --- |
| **Assess Calgary bylaw classification** | Codex task `01a06525-4a50-7940-8d7b-63c0823f8d25`, September 2, 2026. A whole-catalogue feasibility study; implementation was deferred at that time. |
| Bylaw recommendation | [Original study](C:/Users/andre/OneDrive/Documents/CityPrompt/artifacts/calgary-bylaw-study-2026-09-02/feasibility-and-recommendation.md). |
| Full teaching crosswalk | [Readable crosswalk](C:/Users/andre/OneDrive/Documents/CityPrompt/artifacts/calgary-bylaw-study-2026-09-02/catalogue-crosswalk.md) and [JSON companion](C:/Users/andre/OneDrive/Documents/CityPrompt/artifacts/calgary-bylaw-study-2026-09-02/catalogue-crosswalk.json). Includes provisional parent mappings and 12 selected variant cases. |
| Street cross-section decisions | [Historical memory](C:/Users/andre/.claude/projects/C--Users-andre-OneDrive-Documents-Playground/memory/project_calgary_street_manual_archetypes.md), begun June 9, 2026; 13 classes, drawing audits, image roles and corrections. |
| Traffic-calming reconciliation | Git `7f536adcb37345d424d2e324ff19be914dcc62c7:docs/TRAFFIC_SAFETY_STREET_MANUAL_RECONCILIATION_2026_06_15.md`. Chapter 10 treatment crosswalk, source revisions and historical gaps. |
| Broader policy/spatial research | Same Git commit, `docs/MUNICIPAL_POLICY_SPATIAL_AI_RESEARCH_2026_06_25.md`. Related research, not an instruction to fold the separate transport product into the student tool. |
| Transport inventory and gap check | Git `d518c4b260039f79fc7ed2f6c227cdde5271e421:docs/transport-standards/README.md` and `docs/transport-standards/CATALOG_GAP_CHECK.md`. June 25 inventory of 56 standards-related references. |

The original study files are local, ignored artifacts in the OneDrive checkout.
They have been left intact. The street documents remain recoverable with
`git show <commit>:<path>` even where absent from the current working tree.
Do not import the full research crosswalk into the browser bundle.

Identity checks against this checkout:

- All 224 parent IDs and 896 variant IDs/counts remain represented by the study's
  source catalogue; the entire source file is byte-identical to the study input.
- Catalogue SHA-256: `fc1a88d1a2bacfca4d1e078bd1b6c964c88e4b247fe27e0943bd7451be1ed307`.
- Study JSON SHA-256: `13eb3287c052b5e9a03eea999db5d77289538d8d47b81e92965073aa03ba5fda`.
- The 896 variants were inventoried, not all individually assessed. The study
  labels 159 parent mappings provisional, 33 needing variant overrides,
  24 requiring program selection, and 8 special cases.

## Building decisions to retain

The proposed teaching sequence is **use/program → form → appearance**, with
districts as references to investigate. Keep five concepts distinct: student
browsing collection, Schedule A use group, Part 4 defined use, physical form,
and the district actually assigned to a parcel. Mixed-use buildings can have
several component uses and belong to several collections.

The first guide provides broad parent-level collections. It does **not** yet
implement the study's many-to-many use mapping or variant-aware legal-use layer.
Its existing development-type prefilter also remains in the property-panel flow.
Do not use its search results as a complete district compatibility list.

Corrections adopted in this follow-up:

| Catalogue case | Browsing correction |
| --- | --- |
| Hotel families | Their own Hotels collection, with a defined-use source and an explanation that the Residential use group is distinct from the parcel district. `hotel_particulier` remains a detached mansion. |
| Both vertical-farm families | One Indoor farms & food production collection, rather than splitting between industry and unknown concepts. |
| Transit Podium Residential / Transit-Oriented Station Block | Mixed-use parent defaults; housing beside transit is not automatically a station use. |
| Old Montreal Warehouse Loft | Apartment conversion as the parent browsing default; selected variants may have other programs. |
| Junction Converted Industrial Loft | Mixed-use conversion as the parent browsing default. |

Hotel section 209 and Food Production section 198.1 were checked again in the
City's current online text before adding those guide notes. [Hotel](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?alphaSearch=209&div=2&part=4),
[Food Production](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?alphaSearch=198.1&div=2&part=4).

Next building increment should use a small, reviewed set from the study's
16-example pilot. Store stable parent/variant IDs, proposed component uses,
form, sources, review date and review state separately from model geometry.
Specific cases already identified for that increment:

- Calgary Modern Infill: detached, side-by-side semi-detached and laneway-suite
  compositions require different use descriptions.
- RNDSQR: stacked suites need program clarification; the terraced garden,
  courtyard and heritage-integrated variants have different activities/scales.
- Farnsworth River Gallery: its explicit gallery program cannot inherit a
  housing-only use merely because the parent is a house.
- Tech-campus data centre/research and CBE headquarters/adaptive reuse require
  an operator/program decision.
- Aquatic Natatorium and Convention Exhibition Center remain in the broad civic
  browsing group; their legacy health/sports labels must not feed legal analysis.

The research also found 53 variants with floor bounds outside the parent range.
Overrides are supported by the source schema; this count is not proof of invalid
models. Reports must evaluate the selected variant and actual dimensions.

## Street decisions to retain

All **13** authored Calgary cross-sections are already in the current catalogue.
Their zone widths still sum to the recorded section width (floating-point
tolerance). The four sections initially missed by the new browsing map are now
classified with their local/collector peers.

| Family | Figures and current section widths | Calgary browsing group |
| --- | --- | --- |
| Alley | 1: 6.5 m | Alleys |
| Local | 2: 16 m; 3 Industrial: 18 m; 4 High Activity: 21 m; 5 Rural: 20 m | Local |
| Collector | 6: 20 m; 7 Industrial: 26 m; 8 High Activity: 27 m | Collector |
| Arterial | 9: 33 m; 10: 36 m; 11 High Activity: 36 m; 12 Six Lane: 46 m | Arterial |
| Skeletal | 13: 60 m | Arterial & major streets |

These are values already encoded from Draft 4.0 drawing research, not a fresh
engineering validation. The alley's recorded width needs its original drawing
context; do not universally interpret every section width as a legal ROW width.
`confidence: exact` means fidelity to that drawing, not municipal approval.

The earlier user-selected scope was 13 base classes, each with one manual
configuration. Parking/school/speed alternates are separate sections to author
if needed, not decorative variants. Retain `section.zones`, figure citations,
source revision and vector diagrams as the geometry backbone. Avoid stretching
every lane, sidewalk and cycle track proportionally when reshaping a standard.
Length/route can change independently; a changed cross-section should be labelled
custom rather than continuing to claim the original standard.

The historical preferred image roles were photoreal card, stylized section for
display and vector section for dimension evidence/conditioning. Current
`aestheticCatalog.ts` instead gives the 13 vectors primary-reference and
generation-input precedence, with existing tests enforcing that behavior.
Preserve it during this classification pass. A later street-render pilot should
explicitly test the display-versus-conditioning roles before changing them.

The June transport inventory's **11 diagram / 36 section-data / 9 card-only**
finding is historical. The current adapter already attaches vectors and
`standardSection` metadata for the 13 Calgary sections, so it is incorrect to
repeat the old claim that none are wired. Actual image-render fidelity and the
remaining transport families still need their own end-to-end verification.

Chapter 9 intersections and Chapter 10 traffic calming are separate plan-view
treatments. Reuse the treatment crosswalk and index instead of regenerating
generic streets under new names. TAC, NACTO and fire-access comparison gaps
identified in the older side project are not completed Calgary standards assets.

For policy status, use the [current Street Manual project page](https://www.calgary.ca/planning/city-building-program/city-building-program/the-street-manual.html)
and the dated source register in [the guide](CALGARY_CATALOGUE_GUIDE.md).
Historical draft files and old forecasts must not override that status.

## Scope and verification

This follow-up changes educational browsing metadata and documents the recovered
research. No source catalogue JSON, dimensions, asset files, render pipeline or
saved student geometry changes. Original research and local visual-QA outputs
remain ignored. No API generation or deployment is needed.

Regression coverage checks the corrected building cases and that searching
Calgary under local/collector/arterial/alley finds all 13 sections in the expected
groups. Run the guide/browser, catalogue and property-panel tests, type checking,
changed-file lint and a local browser filter trial before committing.

Completed: 57 tests passed across those four files; TypeScript, changed-file
ESLint and diff checks passed. The local browser showed all four Calgary local
and all three collector sections under the correct filters. Before/after API
snapshots confirmed saved zone geometry and properties were unchanged; no page
errors were reported. Evidence is in ignored
`artifacts/calgary-catalogue/history-filter-result.json` and the accompanying
`history-*.png` screenshots. This was a catalogue-filter trial, not a new render
or placement validation. The cold globe still paused while aligning to ground.
