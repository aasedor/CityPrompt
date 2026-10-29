# Claude crossings and practical buildings — implementation plan

> **For agentic workers:** Use superpowers:executing-plans inline, with one fresh review at the end of each coherent branch.

**Goal:** Integrate the remaining reviewed crossings, then practical hospital/fire/student buildings, then more bridges, in the user's requested order.

**Architecture:** Preserve exact Claude originals. Reuse fixed-native public-realm placement and shared component ownership extraction to remove oversized context without stretching a crossing. Corrected building or bridge designs, if required, use a separate candidate version and independent RLASM review; never replace an original silently.

**Tech stack:** React/Three.js, existing native/public-realm registries, Python/Blender authoring and source-byte auditing, local FastAPI test stack, ordinary Edge browser tests.

**Spec:** User: “Ok, let’s do those. Then after, I would like to have some practical buildings like the hospital, fire station and student residences. Then doing some more bridges”. Prior scope: snug envelopes, compact corresponding landscaping allowed, no building-attached roads, original GLBs immutable.

## Global constraints

- Deployment-version lineage; branch from7d088b70f. Separate public-realm and practical-building initiatives/checkpoints.
- Source pin7f30f4852c461c289fe5d305a472f853337a24f1 verified against remote on29October.
- Never merge Claude branch or bulk-fetch its history; bounded exact-object extraction only.
- Never parse-and-rewrite archetype catalogues. Original models and source-locked evidence stay byte-identical.
- C: evidence only; D: remains full and previously denied cleanup must not be retried.
- Use existing hydrated public assets read-only through a bounded overlay; no whole-library duplication.
- No paid image/video generation or deployment in this work. Deliver labelled free source captures/screenshots to the existing private Drive review folder.
- A displayed card is not an integration pass. Record incomplete checks and original open findings honestly.

## Review focus

- Original kilometre-scale context must not become the occupied plot or terrain carrier.
- Preserve complete arches, supports, parapets, rail/road decks and passage facades, including mixed-material components.
- Fixed architectural crossings must never enter arbitrary route bending, stretching or misleading size controls.
- Saved exact identity, unit scale, rotation, reload and capture must match the candidate actually displayed.
- Open visual findings cannot be silently cleared by adding catalogue metadata.

## Task1 — source and classroom scope

- [x] Read exact source reviews/recipes and measure Passatgev006, brick viaductv003, stone road bridgev003 and stepped plazav005.
- [x] Define retained component ownership and supported native placement; preserve originals and hashes.
- [x] Inspect hospitalv003, fire stationv009, student residencev002 reviews. Latest user explicitly authorizes addressing these, superseding their earlier report-only scope; originals remain immutable.
- [x] Record a finite later bridge set: planted green bridgev002, tied-arch shared bridgev003 and timber-covered footbridgev002, with new corrected candidates only if needed.

## Task2 — reviewed crossing pilot then scale

- [x] Add failing source/geometry/registry/release-boundary tests for exact ownership and snug fixed-native plots.
- [x] Implement the smallest shared extraction adapter, preserving existing building contracts and public-realm activation gates.
- [x] Add one local pilot, test ordinary picker/place/rotate/save/reload/free capture and show actual screenshot.
- [x] Repeat for remaining reviewed crossings; investigate plaza hold rather than activating a known defect.
- [x] Run narrow frontend/backend checks and TypeScript; independent review, exact LFS staging and local checkpoint.

## Task3 — practical buildings

- [ ] On a separate coherent branch, correct classroom blockers in new versions while preserving locked original files and references.
- [ ] Render/inspect the required source-locked evidence and obtain independent review before keeper/readiness claims.
- [ ] Use existing catalogue promotion, selective seed/readback, building-only ownership and snug-envelope workflow.
- [ ] Browser-trial hospital, fire station and student residence; verify exact model, unit scale, edit/reload and captures.
- [ ] Narrow checks, fresh review and local checkpoint.

## Task4 — additional bridges

- [ ] Repeat finite source-lock/correct/review/integrate/browser-test workflow for the three recorded bridge types.
- [ ] Preserve original review limitations and keep any remaining blockers visible.

## Task5 — delivery

- [ ] Upload completed free source originals/screenshots with dated batch notes and persisted verified Drive receipts.
- [ ] Report the exact candidates actually available, tested paths, remaining limitations and commit/release status.
