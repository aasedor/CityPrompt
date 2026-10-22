# People Video Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build and validate a few animated adults in an authored CityPrompt street and produce high-quality four-second photographic Omni edits.

**Architecture:** Preserve the existing scene, route capture and paid-attempt machinery. Add bounded four-second capture and an optional character image; stage lightweight independent actors with deterministic animation in native Three.js scene capture. Use licensed source rigs with separately recorded character derivatives and photographic references.

**Tech Stack:** React, TypeScript, Three.js, glTF, FastAPI, Python, Gemini Omni 1.1, local PostgreSQL/MinIO, ffmpeg.

**Spec:** `docs/superpowers/specs/2026-10-21-people-video-pilot.md`

## Global Constraints

- At most ten paid four-second Omni edits; no automatic retries or purchases.
- Local pilot only; preserve production and unrelated hydrated LFS changes.
- Preserve eight-second compatibility and idempotent replay of prior requests.
- Metres, authored foot datum, deterministic animation and separate per-person skeleton state.
- Keep heavy source/QA/media outside Git; retain hashes, license and exact receipts.

## Review Focus

- A legacy replay with omitted new default fields must not make another paid call (Task 1).
- Malformed/oversized reference media must fail before provider submission (Task 1).
- Four-second warmup and final capture must use the same timeline and actor pose (Task 3).
- Independent characters must not share pose state or dispose cached resources (Tasks 2–3).
- Failed capture or cancellation must restore normal scene/camera/actor state (Task 3).

### Task 1: Bounded video and appearance-reference API

**Files:** `backend/app/api/v1/video.py`, `backend/app/services/omni_video.py`, `backend/app/services/video_media.py`, related narrow tests.

**Interfaces:** `duration_seconds: Literal[4,8]=8`; optional `character_reference_base64: str | None = None` and `character_reference_mime_type: Literal['image/png','image/jpeg']='image/png'`. Four seconds and references apply only to Omni `preview_video`. Decode and verify one image (max 8 MiB decoded, max 4096 px each dimension, nonzero pixels). Reference is identity/appearance, never an output first frame. Extend exact hashes, saved private metadata, privacy redaction and old replay compatibility.

- [x] Add failing tests for four-second source media, invalid reference, preview-only restrictions, provider input and replay/privacy.
- [x] Implement validated optional reference and duration without relaxing paid admission or retry behavior.
- [x] Run narrow pytest and report the exact result; do not call paid providers.

### Task 2: Three measured character derivatives

**Files:** external `C:/dev-artifacts/CityPrompt/people-video-pilot-2026-10-21/`; small provenance/code under `tools/people_pilot/` if reusable.

**Interfaces:** Three Y-up metre GLBs with feet at y=0, stable forward direction recorded, independent named `Walk` and `Idle` clips where supplied. Stable IDs `people-pilot-commuter`, `people-pilot-neighbour`, `people-pilot-creative`. A JSON manifest records source/license/hash, runtime hash, dimensions, animation names/duration, triangles, materials, decoded costs and limitations. Prefer standard free official character source; no paid generation.

- [x] Verify official license/download, inventory rigs and animation, preserve source.
- [x] Build distinctive clothed adult derivatives, export bounded runtime GLBs, inspect posed bounds/feet and all animation tracks.
- [x] Produce a free browser turnaround/animation preview and report exact artifacts; no invented readiness claims.

### Task 3: Deterministic native people and four-second UI/capture

**Files:** `frontend/src/components/viewer/VideoGeneratePanel.tsx`, `videoRouteControls.ts`, `videoRenderQuality.ts`, globe capture, focused new people animation module, Add Details glue and tests.

**Interfaces:** `durationSeconds: 4|8`; `buildVideoWarmupFrames(profile,durationSeconds=8)` and final frames use the same duration. Add optional image upload and four/eight-second controls only for supported Omni preview. Actors use a copied skeleton, shared geometry, isolated material state and absolute-time poses; initial static placement is saved through existing details. Opt-in capture animation follows authored paths/speed; idle in editing. Temporary capture state is restored in `finally`.

- [x] Add failing timeline/pose/isolation/UI tests, implement minimal supporting code, run narrow Vitest and type-check after integration.
- [x] Register local pilot assets safely and build one authored project without mutating user projects.
- [x] Browser-test placement/edit/persistence, free full-motion capture, actor ground contact and framing. Run scoped lint and configured build.

### Task 4: Bounded quality trials and review

**Files:** external per-attempt ledger, receipts, source/result MP4s, comparison page; concise report in `docs/video-pilots/`.

- [x] Create the immutable ten-call budget ledger before a provider call; inspect free source and matching original photographic reference.
- [x] Run one four-second identity/motion pilot through the app. Measure actual output; review complete gait, face/clothes stability, ground contact and architecture before any next batch.
- [x] Improve one variable at a time, up to ten total; stop when enough convincing results are obtained. Record rejected results honestly.
- [x] Independent implementation/visual review, final tests and source diff review; commit only this initiative if verified, no push/deploy.
- [x] Show best outputs, local scene and measured limitations.
