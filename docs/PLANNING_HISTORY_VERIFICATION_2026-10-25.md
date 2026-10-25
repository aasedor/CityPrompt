# Planning-history classification: verification and scope

The research and local teaching interface support an introductory course on
planning in Canadian cities with international comparisons. The companion
[research report](PLANNING_IN_THE_CANADIAN_CITY_2026-10-25.md) explains the
historical framework; the CSVs retain the individual classification evidence.

## What is classified

| Population | Result |
| --- | --- |
| Current local exact choices | 196: 97 buildings, 53 streets/pathways, 46 parks/open spaces |
| Classified choices | 188, including legitimate context-dependent era outcomes |
| Held reference conflicts | 8, with no confident era, style or planning tags |
| Reviewed offline building candidates | 5 research records; excluded from the runtime history catalogue |
| Archetype export | 201 rows: 196 current records plus five offline candidates |
| Family coverage export | 521 rows: 497 legacy families plus 24 current-only native park/street families |
| Legacy families without a current exact choice | 343, explicitly awaiting exact-variant research |
| Framework | Seven broad era outcomes, 23 planning definitions, 56 source records |

Dates are approximate design associations, not real construction years.
Historical influence can coexist with a contemporary reinterpretation.
Missing middle describes modest multi-unit forms, while Vancouverism describes
an urban-design approach. Neither establishes tenure, affordability, public
benefit or the performance of an entire neighbourhood from a model's appearance.
The bibliography distinguishes inherited curated references from sources
checked for this research.

The eight held identities are Halifax Clapboard House, the provincial brick
school, Inglewood Corner Merchants, Courtyard Primary School, CTrain Elevated
Station, Halifax Waterfront Warehouse, Old Montréal Limestone Commercial and
the rail through-truss public-realm model. Their exact IDs remain in the export.

## Verification

- Python: 30 tests passed across the new history contracts/generator and the
  original teaching generator. Tests cover input tampering, wrong exact model
  contracts, held records, source/era references, incomplete coverage, candidate
  hash changes, deterministic outputs and refusal to overwrite an existing batch.
- Frontend: 90 focused tests passed across history, teaching definitions/cards,
  facets, canonical discovery, presentation and palette browsing. New tests were observed
  failing before implementation. The frontend TypeScript check passed.
- A second finite generation reproduced the promoted JSON and all three CSVs.
  All 196 current records join the family coverage export exactly once; all 201
  construction-year cells are empty. A local receipt records output SHA-256 hashes.
- The original teaching JSON is byte-identical to its pre-task backup. Original
  reviewed teaching inputs, models, compiler, seed files and backend have no
  changes from the initiative's base commit.
- Independent whole-branch review found one Important search-path issue and no
  Critical or Minor findings. Five full-search regression cases failed before
  the fix, then passed with the 90-test suite and TypeScript check. Held/stale
  designs now retain literal name/ID discovery while legacy semantic tags and
  descriptions are withheld. The original locked evidence was not relabelled.

The only pytest warning is an existing pytest-asyncio fixture-loop configuration
deprecation; the focused synchronous tests pass.

## Student browser trial

Read-only local Edge checks used the existing court-only pilot project. No
objects were placed, no project geometry changed and no paid render was started.

| Student action | Observed result |
| --- | --- |
| Browse by postwar era | Nine building choices |
| Add a bungalow search | One choice, with 1945–1975/1950s association and CMHC/Don Mills context |
| Contemporary era plus missing middle | Nine modest multi-unit choices |
| Browse Vancouverism | Two residential tower/podium choices |
| Postwar plus missing middle | Clear empty result; Clear filters restores all 97 building choices |
| Switch from Buildings to Parks | Era and planning filters clear; all 46 local park choices remain available |
| Phone breakpoint | Browser override 375 × 812; actual CSS width 341 px equals document width, with no horizontal overflow |
| Keyboard | Tab moves from Design era to Planning idea |
| Console | No warning or error entries during the trial |

After the review fix, an additional browser check confirmed that `classical`
returns only the Neoclassical Office, while searching Provincial Brick School
by name still returns its held card with no taught era/style. The console
remained free of warning/error entries.

The temporary viewport override was reset. Screenshots show interface evidence,
not newly generated image originals. The test-mode catalogue has 195 choices:
an existing development-only plaza gate accounts for the one-choice difference
from the 196-record local-development snapshot. No availability gate changed.

## Scope decisions and remaining evidence gaps

1. Use a multi-axis history layer and local era browsing. One exclusive
   style/era hierarchy would obscure revivals and cross-era housing forms.
   A different syllabus emphasis may require revising these interpretive labels;
   it does not require changing models.
2. Classify the 196 exact local choices and five offline candidates, and report
   the larger source library separately. The 343 source-only families lack
   reviewed exact-variant evidence; extending dates to them would overstate
   certainty. They remain research leads rather than completed classifications.
3. Expand the coverage index from 497 legacy families to the 521-family exact-ID
   union. The 24 native park/street families are current choices outside the old
   source files. Keeping the populations separate prevents incorrect coverage
   claims; a future source-library refresh must reconcile them again.

The independent reviewer deliberately left six matters outside its verdict;
these decisions remain explicit:

4. Existing model geometry, reference fidelity, terrain and approval gates were
   unchanged. This review grants no new model approval; pre-existing visual
   issues still require their own exact-model review.
5. The 343 source-only families retain their unreviewed status. Broader library
   classification remains future work because exact evidence is absent.
6. Era overlaps remain interpretive teaching groupings. A different syllabus may
   call for different boundaries; these labels do not become construction dates.
7. Inherited sources retain disclosed inherited status. The independent checks
   targeted consequential claims; older links/background references may need
   later rechecking.
8. Deployment, publication and offline-candidate activation remain outside this
   initiative. Live students receive these changes only after authorized
   integration and publication.
9. The independent reviewer exercised actual search modules and reviewed the
   supplied browser evidence. It did not repeat the author's desktop/phone
   trial, so visual verification has one author-run browser pass rather than a
   second independent browser pass.

There are no deferred Minor review findings.

Institutional topics still need sourced case studies and composed neighbourhood
scenes: Indigenous authority, non-market/co-operative housing, displacement,
regional systems and neighbourhood outcomes. No new facade label resolves those
gaps. Existing held references need separate model/source review.

This initiative remains on local branch
`codex/planning-history-teaching-20261025` in the isolated architecture-teaching
worktree. It does not activate the five offline candidates, publish the expanded
catalogue, push Git changes or deploy the teaching interface.

External generated batches, logs, screenshots, receipts and the execution ledger
are retained under `C:/dev-artifacts/CityPrompt/planning-history-20261025`.

## Follow-up: explicit use/form tags

The instructor confirmed the four-axis categorisation and requested its tags.
All 196 local records already carry authored use/form, style, era and planning
fields. The follow-up exposes the reviewed use/form label on expanded cards and
in semantic search. This corrects the Charcoal Gable Fourplex's old broad
townhouse caption to Fourplex; the model, placement guide and locked audit remain
unchanged. Every one of the 188 classified records has an explicit display label;
the eight held records remain withheld. Housing tenure is not inferred or added.

Three new regression tests were observed failing before implementation: the
fourplex's four-axis card, complete form-label coverage and discovery by the
reviewed form label. All 93 focused frontend tests and the TypeScript check pass.
All 43 classified use/form IDs have plain labels. The local browser showed one
fourplex search result with the correct form, contemporary gabled style,
2000–present association and missing-middle/compact-infill planning connections;
no warning/error console entries were recorded. No placement or render action
was performed. A readable interface screenshot is stored with the follow-up
evidence. The generator still validates and reproduces the unchanged history
JSON. This small follow-up receives author verification; the independent
whole-branch review above applies to the earlier research/search checkpoint.
