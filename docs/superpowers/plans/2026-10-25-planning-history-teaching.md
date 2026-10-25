# Planning history teaching implementation plan

> **For agentic workers:** Use superpowers:executing-plans inline, then one fresh whole-branch reviewer. Existing user direction authorizes research and local categorisation; proceed without a new approval pause.

**Goal:** Classify current archetypes by design era and planning context for an introductory Canadian urban-planning course with international connections.

**Architecture:** Preserve the original teaching data; add a hash-bound history layer and small pure frontend helpers. Authored exact-variant records drive both exports and browsing.

**Tech Stack:** JSON, Python/pytest, React/TypeScript/Vitest, primary-source web research.

**Spec:** docs/superpowers/specs/2026-10-25-planning-history-teaching-design.md

## Global constraints

- 196 current exact choices, eight held; five uninstalled candidates in export only; 497-family coverage index.
- Approximate era associations, no invented construction dates or automatic ideology/tenure claims.
- Preserve base teaching evidence/model/source assets, all placement behaviour and activation state.
- No paid generation, seed changes, push or deployment. Reuse isolated worktree on codex/planning-history-teaching-20261025.

## Review focus

- A contemporary reinterpretation can show historical influence without acquiring an invented construction date.
- A fourplex can support missing-middle teaching; a detached home or large tower does not become missing middle from its aesthetic.
- Held/stale identities expose no confident historical tags, including through search or filters.
- Planning affiliations describe components/context, never proven tenure, affordability, Indigenous governance or whole-neighbourhood performance.
- Filters reset across domains and at phone width; source-only families and offline candidates never enter the drawable catalogue.

### Task 1: Research framework and authored classification

**Files:** new tools/planning_history/reviewed-inputs/{framework.json,assignments.json,candidates.json,evidence-lock.json}; docs/PLANNING_IN_THE_CANADIAN_CITY_2026-10-25.md.
**Interfaces:** framework defines ordered eras/planning/styles/sources; assignments keyed by exact placement ID with copied contract; candidates bind model hashes separately. Existing audit/inventory are unchanged authoritative inputs.

- [x] Research Canadian/international origins, dates, recent changes and critical case studies.
- [x] Write failing contract tests for coverage, source binding, held identities and exact model contracts.
- [x] Author all current records and candidate contexts; implement validation with explicit failures and tests GREEN.

### Task 2: Reproducible outputs and research exports

**Files:** tools/planning_history/{build_data.py,test_build_data.py,README.md}; frontend/src/data/cataloguePlanningHistory.json; docs/planning-history-{archetypes,source-coverage}-2026-10-25.csv.
**Interfaces:** build_data.build() returns current-only history overlay and 201/497-row exports; CLI writes exclusively into a new output directory, refusing existing targets.

- [ ] Test altered locks/contracts, duplicate IDs, invalid era/source references and overwrite attempts RED.
- [ ] Implement finite deterministic generator; validate all rows and preserve base bytes; tests GREEN.
- [ ] Promote only reviewed text outputs and checkpoint source.

### Task 3: Era and planning context in catalogue

**Files:** new frontend/src/features/catalogueLearning/planningHistory.ts and tests; existing teaching, definition/details, palette/facet modules and relevant tests.
**Interfaces:** historyForChoice checks domain/archetype/variant/method/revision; eraIds/definitions feed facet filtering, contextual cards and search. Planning vocabulary/styles merge from reviewed history layer only.

- [ ] Test postwar bungalow, interwar influences, contemporary fourplex/missing middle, Vancouverism and held/stale records RED.
- [ ] Add era browsing/filter/card context, search and full reset/domain changes; tests GREEN.
- [ ] Run narrow frontend suite and npm run type-check; read-only local browser trial at desktop/phone width.

### Task 4: Final verification and handoff

**Files:** research/report and execution ledger; external artifacts under C:/dev-artifacts/CityPrompt/planning-history-20261025.

- [ ] Verify 201/497 export coverage, source links/date/interpretation boundaries and unchanged asset/base hashes.
- [ ] Run focused generator/frontend checks; review diff/check/stat/status; commit coherent source units.
- [ ] Obtain fresh-context whole-branch review on the most capable available model; fix any Important/Critical issues in one RED-to-GREEN pass.
- [ ] Deliver research, categorisation exports and local UI evidence; keep branch local and report remaining evidence gaps.
