# Fixed-width street catalogue pilot — 2026-09-07

Initiative: `codex/fixed-width-street-catalogue`.

Students can now place three additional existing metric street designs from the
simple Streets menu. No AI generation, new binary assets, or paid renders were
needed. The existing 16 m Calgary local street retains its saved identity.

| New choice | Total section | Components |
| --- | ---: | --- |
| Planted laneway | 5 m | 0.75 m planted edge + 3.5 m shared lane + 0.75 m planted edge |
| Shared street | 6 m | 0.3 m flush edge + 5.4 m shared surface + 0.3 m flush edge |
| Calgary collector | 20 m | 0.3 m setback + 3 m pathway + 3.4 m boulevard + two 3.3 m travel lanes + 4.6 m boulevard + 1.8 m sidewalk + 0.3 m setback |

The laneway/shared street are representative teaching designs. The collector
reuses the previously researched Street Manual Draft 4.0 Figure 6. Its easement
is not included in the 20 m drawn section. The City page was rechecked on
September 7 and still anticipates final-draft administrative approval in Q2 2027:
https://www.calgary.ca/planning/city-building-program/city-building-program/the-street-manual.html
Earlier research: `docs/CALGARY_RESEARCH_RECONCILIATION_2026_09_05.md`.

## Implementation

- Registry defines the bounded three-option addition using existing variants,
  authoritative thumbnail roots and catalogue widths.
- Cross-section diagrams use `resolvePilotStreetSectionProfile`, also used by
  the 3D renderer. Every surface band is numbered and dimensioned; horizontal
  widths are proportional and vertical heights explicitly schematic. The
  section looks back toward the first route point, consistent with the mesh's
  positive-left normal and ascending signed offsets.
- Route recognition checks the saved section marker, archetype and variant.
  Move, bend, route validation and advanced-panel width locking now use the
  selected section width instead of assuming all streets are 16 m.
- Selecting another street while drawing activates that type, rather than
  toggling drawing off. Only the selected street card has a pressed state.
- The drawing sidebar names the active street and its fixed total width.
- No building, park, render-prompt, backend or source catalogue JSON was changed.

## Browser trial

Local frontend: http://127.0.0.1:5178 (the active isolated checkout; the other
checkout and server on 5174 were left intact). Backend: port 8002.

1. In the existing 20-building community, placed a 5 m laneway between the
   western house columns. The first two attempts overlapped the plot envelopes
   and were correctly rejected. A precisely centred route fit and compiled.
   Project: `3c12dda6-3b15-4151-bf8b-eb59628a99ff`.
   Saved street: `5a54cb40-85bd-45f8-8dd7-686572b4c354`.
2. Created a separate local test fixture with the same vacant-site boundary
   through the existing project/zone APIs, then placed all three street types
   through the catalogue and drawing buttons (two route points and Finish).
   Project: `200eaf4e-e5d6-40f1-a59c-b8f7f4e74f20`,
   "Street sections trial - 5m 6m 20m".
3. Server records report all three as compiled. Saved widths and resolved 3D
   band totals agree at 5/6/20 m. No paid render was requested.
4. Selected the shared street, clicked Add bend point, then dragged its centre
   handle sideways. Three route points saved, width remained 6 m, and 3D rebuilt.
   Advanced settings showed a disabled width input with value 6.
5. Reloaded the project: all three compiled streets and their widths persisted;
   the shared street retained the bent three-point centreline.
6. Inspected the picker and expanded cross-sections at 1600x1000 and 1024x768.
   Tablet page width remained 1024 with no horizontal overflow or broken images.

Screenshots/QA data are outside Git under:
`C:/dev-artifacts/CityPrompt/fixed-street-sections-2026-09-07/`.

## Limits and next increment

- This adds placeable designs and dimensioned controls, not newly generated
  visual families. Existing catalogue reference pictures remain illustrative.
- Collector metric surfaces work; live furniture is less developed than the
  existing local-street family. Do not present it as a completed furniture kit.
- Centreline-only drawing makes narrow gaps difficult to judge. A future full-
  width preview with visible plot envelopes would improve placement confidence.
- Widths are full authored sections, not just asphalt carriageways. Detailed
  servicing, easements and engineering approval remain separate.
- Source changes remain local until a push is requested. No generated imagery
  is staged with the implementation.

## Verification completed

- 91 targeted Vitest tests passed across placement, registry, cross-section UI,
  section profiles and advanced property controls.
- TypeScript `npm run type-check` passed.
- ESLint passed on the new/modified pick-place production components and tests.
- `git diff --check` passed before the local checkpoint.
