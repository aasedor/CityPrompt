# Older-project navigation and compatibility checkpoint

The new student navigation initially opened boundary-free saved designs at
Choose your site. Existing buildings were visible, but the main confirmation
button was disabled. Opening a saved building, street or park scene now defaults
to Design, like a saved boundary does. Empty projects still start in Site;
explicit step navigation still takes precedence. No stored project migration is
needed and no new boundary is created.

## Verified locally, 16 September 2026

| Existing fixture | Browser evidence |
| --- | --- |
| Currie Commons, `bb4a6a7b-479f-45a1-b7f2-94f50b84e696` | 13 zones loaded with existing models; selected Craftsman, saved a name edit, undid and reloaded. All fields except the updated revision match the pre-test snapshot. |
| Currie 20-building trial, `3c12dda6-3b15-4151-bf8b-eb59628a99ff` | 26 zones loaded. Reproduced incorrect Site default, then reloaded into Design with Buildings/Parks/Streets available. Settled scene inspected; saved state unchanged. |
| Skyscraper trio, `9b77dbcd-b21b-4dbf-a425-216db44ed183` | Three existing towers loaded; top and oblique views inspected. Opens directly in Design without a boundary; saved state unchanged. |

All three preserve IDs, coordinates, properties, archetype metadata and stored
representations. No new browser exceptions or failed requests were observed.
Eighteen focused workflow/navigation tests, TypeScript and changed-file ESLint
pass. Evidence: external `phase13-compat-*.json`, `phase13-currie-*.json`, and
inspected `PHASE13-CURRIE-*`, `PHASE13-20-HOMES-*`, `PHASE13-TOWERS-*` images under
`C:/dev-artifacts/CityPrompt/student-design-transformation/`.

## Limits

This is bounded compatibility evidence, not acceptance of every historic schema
or the full edit/save/reopen journey for each fixture. Currie Commons retains
its disclosed simplified public-realm representation. White foundation edges,
context overlap in the 20-building trial and the cropped tallest tower in the
default oblique camera remain visual findings. The historical settings panel
also recalculates the zone mask colour when saving a name; Undo restored it.
No geometry was moved to conceal these findings. Grounding and professional
visual-quality gates remain open. No paid image/video calls were made.
