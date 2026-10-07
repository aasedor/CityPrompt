# Calgary district identity correction — 2026-10-05

The student zoning editor previously reduced City data to an editable label and
assigned colours by polygon order. The gallery's illustrative proposed areas
used captions such as “Courtyard housing,” which did not identify Calgary
districts. The user clarified that the map must use actual City designations,
such as R-CG, from the Land Use Bylaw and City district geometry.

## Change

- Retain `lu_code`, the complete published `label` (including modifiers and DC
  references), and `description` when copying the City district geometry.
- Store district identity separately from the student caption through editing,
  clipping, undo, drafts, saving, reloading and SVG/PNG export.
- Load a bounded list of published district codes from the same City dataset
  when an editable area is selected. Source designations from the site remain
  selectable. A generic DC choice is excluded; individual copied DC references
  are retained.
- Restore the saved designation from older unedited City copies. Existing
  custom concept labels remain unassigned until a student chooses a district;
  there is no automatic conversion of a programme name into a zoning code.
- Label the drawing and district key with codes, preserve captions alongside
  them, and give narrow districts margin callouts rather than clipped labels.
- Use stable study colours for the same designation, independent of source row
  order. These are editable presentation colours, not official City symbology.

The City dataset is [Land Use Districts, qe6k-p9nh](https://data.calgary.ca/Base-Maps/Land-Use-Districts/qe6k-p9nh).
The [online Land Use Bylaw 1P2007](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html)
was checked for the R-CG and S-SPR designations. The app queries the published
spatial dataset; it does not substitute invented programme labels for districts.

This correction does not implement a development compliance engine or change
statutory zoning. Base district choices do not generate site-specific height,
density or floor-area modifiers. Copied full designations retain those modifiers.

## Verification

- Four focused frontend test files: **28 passed**.
- `npm run type-check`: passed.
- `backend/tests/test_zoning_studies.py`: **19 passed**.
- Browser on the isolated local instance at port 5178, API 8009: copied and
  saved all seven source district pieces; reloaded the study with their complete
  designations and descriptions. Existing source includes S-SPR and six distinct
  DC designations.
- In the agent-created classroom trial proposal only, assigned the published
  R-CG and S-SPR choices to the two illustrative concept areas. Save and explicit
  shared-version reload retained both codes and the original captions. These
  proposed assignments do not describe the site's existing zoning.
- Inspected the actual downloaded PNG: R-CG, S-SPR, full names, captions, source
  attribution and separate proposed-study identification remain readable.
- Browser error log empty at the final check.

Screenshots and the exported PNG are outside the repository in
`C:/dev-artifacts/CityPrompt/calgary-district-identity-2026-10-05/`:

- `existing-calgary-districts.jpg`
- `proposed-calgary-codes.jpg`
- `proposed-calgary-codes.png`

Source-only local checkpoint on `codex/calgary-district-identity-2026-10-05`.
No push, deployment, gallery replacement, paid generation, catalogue asset
change, or primary-checkout change. This resolves the zoning-code disconnection;
it does not declare the wider visual work approved or finished.
