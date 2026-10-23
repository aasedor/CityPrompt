# Realistic People picker implementation plan

> **For agentic workers:** Use superpowers:executing-plans inline, then one fresh whole-change review. No implementation subagents are needed.

**Goal:** Show approved-style realistic appearances for all 23 People choices.
**Architecture:** Keep source catalogue and model bytes; overlay a separate
appearance-preview manifest in detailCatalogue and prioritize it in detailThumbnail.
**Tech Stack:** TypeScript/React/Vitest, built-in image_gen, compact WebP assets.
**Spec:** `docs/superpowers/specs/2026-10-23-people-picker-realism.md`

## Constraints and review focus

Local only, stable IDs/GLBs/actions, immutable source thumbnails and generation
originals. Previews must not be described as exact 3D model captures. No missing
faces/limbs/shoes, unwanted extra people or outfit drift. Keep lazy loading and
avoid decoding GLBs for picker cards. Record unresolved visual limitations.

- [x] Generate remaining 22 portraits from inspected source images; review finite batches.
- [x] Save prompts/raw outputs/hash receipts; derive small WebPs and 23-entry manifest.
- [x] Write failing thumbnail precedence and AI-preview labelling tests.
- [x] Implement manifest overlay, labels and portrait framing; preserve other cards.
- [x] Check all image/model hashes, HTTP responses, tests/type-check/lint/browser.
- [x] Fresh review, local source checkpoint, screenshots and honest release limits.

User correction incorporated: distinct clothes/styles, not repeated source overshirts. Evidence: `docs/PEOPLE_PICKER_REALISM_LOCAL_2026-10-23.md`.
