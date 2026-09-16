# Canonical catalogue checkpoint

The primary Buildings / Parks / Streets catalogue now discovers the existing
eligible aesthetic catalogue, rather than only the small placement registry.
Current computed coverage is 223 building, 130 open-space and 115 street/path
entries. Counts are observations, not hard-coded acceptance expectations.

Search includes canonical names, variants, descriptions, categories, district
codes and existing placement labels. Categories and variant selectors come
from the same source data. Duplicate IDs, malformed entries and duplicate
variants fail validation. New eligible catalogue entries need no bespoke card.

Reviewed placement definitions retain their native placement path. Other
entries use the existing outline/route authoring and compiler with exact
archetype, variant and reference identity. Cards distinguish detailed placement
from design references/massing. This is a discovery checkpoint: full single-click
building placement and simpler editing remain Phase 4 work.

The previous property-panel selection builder is shared with catalogue creation;
it was extracted without duplicating catalogue metadata or compiler ownership.
Building creation explicitly derives height from the chosen floor count and
floor height. Saved fallback metadata now produces a visible notice after reload.
An unavailable detailed model is not presented as a successful detailed building.

## Evidence and limits

Evidence lives under `C:/dev-artifacts/CityPrompt/student-design-transformation/`.
All 2,080 referenced catalogue image paths were resolved against exact tracked
Git/LFS content and checked for local availability; new runtime assets use local
immutable hardlinks outside the source tree. No catalogue data was promoted or
published. Existing human review requirements remain intact.

Browser pilot project: `c5f73929-f949-41d2-ac7d-0340e09339e7`.

- Brownstone reference/variant selection, outline creation and automatic massing
  compilation preserve canonical identity. Visual inspection found a generic
  30 m default overriding the selected two-storey height. The corrected new
  building saves at 6.4 m; the earlier failure is retained as evidence.
- An oversized skate park correctly reports a simplified fallback. A second
  outline within existing reviewed limits resolves the skate-park assembly.
  Its 31 missing local runtime texture files were restored from exact Git/LFS
  bytes (1.58 MB). A subsequent reload had no new browser errors or failed
  resource responses. The bowls visibly retain an incorrect green surface:
  park surface/grounding acceptance remains open; this is not a park visual pass.
- An outside-boundary test drawing was rejected and preserved locally. Its
  reason and coordinates were recorded before discarding only that test draft.
  No benchmark geometry was changed.
- Narrow catalogue/property/automatic-compilation suites: 42 tests pass.
  Type-check and targeted production-file ESLint pass.

All 33 categories (14 building, 10 park, 9 street) were selected in the browser;
visible reference images loaded in every category. Screenshots were inspected
in grouped QA sheets. The 900 × 768 catalogue has no horizontal overflow or
clipped primary filters. Cumulative browser errors stayed unchanged at 442
after asset restoration; no new failed resource responses were observed.
Coverage is recorded in `phase3-category-browser.json`, `PHASE3-GROUP-*`,
`PHASE3-QA-SHEET-*` and `PHASE3-NARROW-CATALOGUE.png`.
The full first-time student journey, detailed identity across all categories,
and final render output are not yet accepted. No paid image/video calls were
made. The external API ledger retains the conservative Maps allowance.
