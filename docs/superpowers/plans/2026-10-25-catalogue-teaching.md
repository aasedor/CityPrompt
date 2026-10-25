# Catalogue teaching implementation plan

> **For agentic workers:** Use `superpowers:executing-plans` inline. A fresh whole-branch reviewer checks the completed implementation.

**Goal:** Let undergraduates browse and learn styles/planning ideas inside the existing City Prompt catalogue.

**Architecture:** An exact-placement teaching overlay supplies researched labels, short definitions, citations and uncertainty. Existing registry objects and placement callbacks remain authoritative. Extend current filters and card details.

**Tech Stack:** React, TypeScript, JSON, Vitest, existing Vite local runtime.

**Spec:** `docs/superpowers/specs/2026-10-25-catalogue-teaching-design.md`.

## Global constraints

- Native inline execution under the user's instruction to keep working while asleep.
- Undergraduate language; separate use/style/planning; planning associations are component suggestions.
- No model, seed, render-prompt, geometry, placement-property or database edits. No push/deployment.
- Preserve `buildingArchetypes.json` bytes; no parse/modify/dump of that file.
- Exact revision/domain/variant matching; changed entries withhold teaching data.
- Baseline: 35/36 narrow tests pass; existing presentation coverage test misses four court-only entries. Fix coverage in Task 1.

## Review focus

- A model revision or sibling variant changes without a new teaching audit: no inherited lesson or certified style.
- A disputed reference is searched/filtered: never present its tentative style as settled.
- A student changes domain or clears an empty intersection: planning/style state and paging reset together.
- A student reads definitions or source links: no placement callback fires.
- A student chooses a filtered design: the identical registry asset reaches the existing callback.

## Tasks

### Task 1: Exact teaching data and safe style discovery

**Files:** create `frontend/src/data/catalogueTeaching.json`, `frontend/src/features/catalogueLearning/teaching.ts` and `teaching.test.ts`; modify `catalogueFacets.ts`, `canonicalCatalogue.ts`, `cataloguePresentation.json` and their narrow tests. Preserve immutable audit/contract snapshots, generator and tests under `tools/catalogue_teaching/`.

**Interfaces:** `lessonForChoice(choice, variantId?)` returns a matched lesson/status or undefined; `teachingStyleIds(choice)` supplies classified IDs or an explicit held/stale empty set; `planningIds(choice)` exposes only supported introductory component associations; style/planning definition lookup and search-term helpers serve the UI.

- [x] Write behavior tests for 25 missing labels, disputed entries withheld, revision/sibling/domain mismatch, and immutable placement identity; run RED.
- [x] Transform the existing audit into a bounded overlay, preserving source provenance and exact model revisions. Add four missing court presentation records from their existing registry metadata.
- [x] Implement matching, definition lookup, style discovery and search integration. Preserve unknown-future fallback and existing Nordic style alias.
- [x] Run narrow existing/new Vitest files to GREEN. Record baseline correction separately from teaching behavior.

### Task 2: In-app teaching controls and card explanations

**Files:** create `frontend/src/features/catalogueLearning/CatalogueTeachingDetails.tsx`, `TeachingDefinition.tsx` and UI tests; modify `PlacementPalette.tsx`, `CatalogueFacetControls.tsx`, `CanonicalCatalogueCard.tsx`, `catalogueFacets.ts`.

**Interfaces:** optional `planningId` extends `CatalogueFacets`; teaching browse actions set the existing list view and expand controls; detail components consume Task 1's exact lesson/status and definitions.

- [x] Write RED tests for style/planning entry from category tiles, definitions without placement, combined filters, zero matches/reset, section changes and unchanged placement callbacks.
- [x] Add teaching entry actions, planning select and concise selected-topic explanation. Reuse current category, search and paging behavior.
- [x] Show exact-variant lessons in expanded cards; held/stale entries receive a short review message. Keep sources in a separate expandable region.
- [x] Run relevant catalogue/palette/card tests and `npm run type-check` to GREEN.

### Task 3: Local student trial, review and delivery

**Files:** create `docs/CATALOGUE_TEACHING_LOCAL_REVIEW_2026-10-25.md`; keep screenshots, runtime receipts and findings in ignored/external artifacts.

- [x] Run a finite browser trial: find a Neoclassical building by style, find street components by planning idea, read a disputed entry, clear an empty intersection and select/cancel an exact design.
- [x] Check mobile/narrow layout, keyboard controls, unchanged asset/reference hashes, errors and local startup. Do not bypass any browser denial.
- [x] Run one fresh whole-branch review; address material findings with regression tests. Run relevant checks and inspect diff/status before commit.
- [x] Commit only this initiative; do not push. Deliver a concise review note and screenshots to the existing Drive review folder, clearly labelled as screenshots.

## Ledger

- Base `44930bc3f`; reused the clean isolated worktree on a new initiative branch. Main and student-fix checkouts are untouched.
- Ruling: continue inline without questions because the user explicitly asked to keep working while asleep; implementation choices are documented as mine.
- Ruling: use existing audit classifications, not new image generation, for the label gaps. Four uncertain blank styles remain held rather than guessed.

- Delivery checkpoint: five JPEG screenshots and review note verified in Drive folder `1E8yvPqqSn_UH2e90UHupp0GMR2RIvg4i`; originals and receipts remain external.
