# Optional Public Data Layers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan inline in the existing isolated worktree.

**Goal:** Add simple optional public-data tick boxes while preserving fast default map use.

**Architecture:** A bounded lazy public-data adapter, a session-only query hook, and an accessible panel feeding the existing reference renderer. Official source cards cover rental-market and levy information without a finance spreadsheet.

**Tech Stack:** React, TypeScript, TanStack Query, existing GeoJSON/reference renderer, Vitest.

**Spec:** `docs/superpowers/specs/2026-10-25-optional-public-data-layers-design.md`

## Global Constraints

Work only on `codex/optional-public-data-layers-20261025` in the attached isolated checkout. Preserve other checkouts. Do not publish or deploy. Enforce the spec's network and geometry budgets and accurately identify incomplete data. Never fetch a disabled source. Keep generated browser evidence outside source control.

## Review Focus

Pay particular attention to aborts when disabled, stale site/project results, response/geometry budgets, correct dataset fields, and source/vintage limitations. Verify existing imported layers and capture exclusions retain their behavior.

### Task 1: Bounded public-data adapter

- [x] Run the existing reference-layer baseline tests.
- [x] Write failing tests for local bounds, scoped requests, curated attributes, invalid/oversized responses, clipping, assessment identifiers, and partial-result warnings.
- [x] Implement `frontend/src/features/publicData/publicDatasets.ts` and `publicData.ts` with finite budgets, abort-aware concurrency and lazy clipping.
- [x] Run the focused tests, confirm RED then GREEN, and record evidence.
- [x] Commit the coherent adapter and its tests after diff checks.

### Task 2: Lazy checkbox controls

- [x] Write failing hook/panel tests for no default traffic, tick/untick, aborts, cached reuse, project/site changes, selection limits, errors and reference cards.
- [x] Implement `usePublicDataLayers.ts` and `PublicDataLayersPanel.tsx`.
- [x] Connect the panel to ProjectViewPage and merge selected ephemeral layers into existing reference overlays without saved project mutations.
- [x] Run focused new and reference-layer tests plus TypeScript checking; record evidence and commit after diff checks.

### Task 3: Student trial and final review

- [x] Check the real bounded public API requests and a local browser session, including network inactivity with options off and error/empty states.
- [x] Request a fresh whole-branch review following requesting-code-review; resolve important findings with targeted tests.
- [x] Run final relevant checks, inspect diff/status, and commit any coherent fixes.
- [x] Report what is available, performance limits, verification and local-only delivery.
