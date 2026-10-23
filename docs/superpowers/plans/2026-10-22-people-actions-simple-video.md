# People actions and simple video implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Complete the local People workflow and make Omni video intuitive.
**Architecture:** Extend existing rig, details storage and render/capture systems;
isolate assets, video UI and people-action integration into disjoint tasks.
**Tech Stack:** React/Three.js/TypeScript/Vitest, FastAPI/pytest, Blender/glTF.
**Spec:** `docs/superpowers/specs/2026-10-22-people-actions-simple-video.md`

## Global constraints

- Local only; no paid calls, pushes or deployment. Preserve legacy saved models/history.
- Twenty new adult assets from verified CC0 sources; immutable originals, exact hashes.
- Fifteen action IDs in the spec; persisted `people_action`; legacy default standing.
- Only Omni 1.1 selectable for new video; explicit paid submission/preflight remains.
- No per-frame actor animation while editing; share geometry, isolate skeleton/material state.

## Review focus

- Action changes cannot disappear in arrange-details, move/copy, undo or reload.
- Static and video captures carry the selected actions and do not override them with generic crowd instructions.
- Capture errors/cancellation restore actors and camera; route cache invalidates on action revision.
- Default video path takes <=3 primary steps without bypassing paid admission or creating hidden paid guides.
- Existing scenes with the original three actors and non-Omni history remain readable.

### Task 1: Finite character expansion (asset worker)

**Files:** new reusable builder/provenance in `tools/people_pilot/`; new catalogue
rows in `frontend/src/features/people/peopleCatalogue.json`; external assets/QA.
**Interface:** preserve existing rows; twenty new stable `people-community-*` IDs.
Rig contract retains Walk/Idle; additional action clips optional with declared names.

- [x] Inspect source/license and existing measured originals; build one visual pilot then finite20.
- [x] Measure/hash all assets and render thumbnails; inspect contact sheet and representative close views.
- [x] Validate loader-compatible meshes/skins/clips/units and byte delivery; document remaining limits.

### Task 2: Simplified Omni UI (video worker)

**Files:** `VideoGeneratePanel.tsx`, its tests, focused helpers as needed.
**Interface:** add optional `peopleDirection?: string` prop; include it in request
and guide prompts/signatures. Keep backend request schema and history compatible.

- [x] Write failing UI tests for Omni-only selection and <=3-step default preparation/generation.
- [x] Refactor student controls; preserve optional route/guide recovery and explicit paid boundary.
- [x] Run focused tests and scoped lint; report exact behavior and limits.

### Task 3: Saved actions, poses and prompt wiring (coordinator)

**Files:** people-actions module/tests, detail types/serializers/edit hook/editor,
PeopleModel/animation, backend project details and image/video prompt builders.
**Interface:** `people_action` stable IDs; canonical action text helper; backwards-compatible
default standing; action metadata on captured actors and current project detail claims.

- [x] Add and observe failing persistence, prompt and action-pose tests.
- [x] Implement selectors/storage/Undo/Redo and deterministic pose/capture behavior.
- [x] Wire image and video action directions, preserving exact scene freshness and legacy defaults.
- [x] Run narrow frontend/backend tests and verify old scenes remain readable.

### Task 4: Local integration and independent review

- [x] Verify every model/thumbnail URL/hash and all15 action presets; measure representative rendering costs.
- [x] Exercise actual local picker, selection highlight, actions, move/copy/delete/Undo/Redo/reload.
- [x] Free image/video preview tests for people actions and simple Omni workflow; no paid submissions.
- [x] Type-check, relevant regressions, scoped lint, diff/status; independent whole-change review.
- [x] Deliver local link/screenshots, tests and limitations. No live changes.

Verification evidence and remaining paid-output/hardware limits: `docs/PEOPLE_ACTIONS_SIMPLE_VIDEO_LOCAL_2026-10-22.md`. Browser interactions and automated tests are distinguished there.
