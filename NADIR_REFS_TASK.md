# Task: Implement Z-axis collapse fix for 0° nadir aerial renders

## Context

You're working on **City Prompt** (repo at `C:\Users\andre\OneDrive\Documents\Playground`, internally called SiteForge), an architectural site planning app used by university students. They draw zones on satellite maps → assign archetypes → generate AI renders via Gemini 3.1 Flash.

**Before starting, read:**
- `CLAUDE.md` at the repo root (critical rules, file sizes, architecture)
- `C:\Users\andre\.claude\projects\C--Users-andre-OneDrive-Documents-Playground\memory\MEMORY.md` (memory index)
- `memory/project_z_axis_nadir_refs.md` (the task brief)
- `memory/project_multi_view_references.md` (existing multi-angle refs system)
- `memory/feedback_globe_render_experiments.md` (lessons from 16+ render experiments)
- `memory/feedback_json_dump.md` (JSON corruption rule)

Current branch is `wip/render-reliability-snapshot` — stay on it. Do NOT push without explicit user approval.

## Problem

When students render site plans at camera pitch = 0° (true top-down / nadir, matching a traditional site plan), Gemini output suffers **Z-axis collapse**:
1. Paper-thin buildings with no height
2. Fallback to watercolor/illustrative instead of photorealistic
3. "Sticker effect" — buildings float on base map with no ambient occlusion or grounding

The fix is a library of orthographic ground-truth reference images per archetype. When fed as refs, Gemini copies the shadow math and materials and stops collapsing.

## Deliverables (in order)

### 1. Audit the render prompt at pitch=0 — NO CODE CHANGES YET

Read `frontend/src/components/viewer/globe/useGlobeAIRender.ts` (~800 lines). Find:
- Where camera pitch is computed from the Three.js quaternion
- Where pitch is inserted into the prompt (COMPOSITION line per memory)
- Exactly what text is emitted at pitch=0 vs pitch=45 vs pitch=90
- Any language that implies oblique perspective (e.g. "aerial perspective view", "bird's eye") that would conflict with nadir refs

Report findings with file:line citations. Recommend a nadir-specific prompt branch if warranted.

### 2. Extend `scripts/generate_angle_images_batch.py`

Add a nadir mode that generates orthographic top-down reference images.

**Filename convention:** match existing `variant_N_angle_90.jpg` (where `90` = pitch from horizon = nadir). Existing multi-view refs already use this. Read a few existing files in `frontend/public/archetypes/buildings/{slug}/` to confirm before writing.

**Spatial guardrails (use these corrected ones, NOT the original "Z-axis collapse" spec):**

- **View:** straight-down overhead, satellite-image style, camera directly above target
- **Projection:** orthographic — roof is the only visible face, no facades, no tilt
- **Lighting:** strong 45° sun from southwest, summer noon
- **Shadow:** length equals building height projected at 45° sun elevation. Do NOT hardcode "half the width of the building" (that's arbitrary and breaks for skyscrapers vs warehouses). Let the model compute shadow from height.
- **Textures:** photorealistic only, zero filters
- **Roof details — category-specific, pull archetype category from metadata:**
  - Commercial/industrial: HVAC units, gravel, parapet caps, drainage scuppers
  - Residential: pitched roof, shingles or tiles, chimneys, dormers
  - Civic/institutional: per-archetype (domes, skylights, flat roofs with specific features)
- **Negative prompt:** isometric, oblique, 3/4 view, axonometric, tilted perspective, vertical facades visible, watercolor, illustration

**API call details:**
- Model: `gemini-3.1-flash-image-preview`
- Temperature: 0.0 (aerial precision — see `feedback_render_prompts.md`)
- Image size: match existing aerial refs in archetype directories (check dimensions before generating)
- `thinking_budget=0` (saves 30-50% latency per experiments memory)

### 3. Run a 3-archetype pilot — STOP HERE for review

Before scaling to all ~97 archetypes, generate nadir refs for exactly three archetypes covering different categories:
- One residential (e.g., `brownstone`, `detached_suburban`, `nordic_house`)
- One commercial (e.g., `glass_office_tower`, `big_box_retail`)
- One civic (e.g., `civic_monumental_neoclassical`)

Save outputs to the appropriate `frontend/public/archetypes/buildings/{slug}/` directories. Report file paths.

**STOP.** Do not scale to more archetypes. Andrew will visually inspect the pilot, likely run a test render on localhost:5174, and tell you whether to proceed.

### 4. Do NOT touch `buildingArchetypes.json` in this task

Per `CLAUDE.md` and `memory/feedback_json_dump.md`: never `json.dump` this file — it corrupts thumbnailUrl paths (underscores → hyphens). If the JSON eventually needs new entries pointing at nadir refs, use text-level insertion only, AND only after the pilot is approved.

## Constraints

- Stay on `wip/render-reliability-snapshot` branch
- Do NOT push to `origin` or `beeman` remotes without explicit user approval
- Test changes locally before declaring done (backend on :8000, frontend on :5174)
- Never commit credentials — the Gemini API key lives in `backend/.env` as `GEMINI_API_KEY`

## Acceptance criteria

- [ ] Audit report for `useGlobeAIRender.ts` pitch=0 prompt behavior with exact line numbers
- [ ] Extended `scripts/generate_angle_images_batch.py` with nadir mode + docstring explaining the Z-axis collapse fix
- [ ] Three pilot nadir ref images generated to disk, paths reported
- [ ] No changes to `buildingArchetypes.json`
- [ ] No force-pushes, no pushes at all
- [ ] Pilot ready for Andrew's visual inspection

## Out of scope for this task

- Generating refs for all 97 archetypes (waits for pilot approval)
- Updating `buildingArchetypes.json` (waits for pilot approval)
- Modifying the render prompt code (audit only — implementation waits for audit review)
- Updating the landing page at cityprompt.ca (separate task)
