# SiteForge Mapping + Accuracy Tooling Plan (v3)

**Status:** Proposed, not yet executed
**Authored:** 2026-04-18
**Intended reader:** A Claude Code session (or engineer) picking this up cold

---

## 0. Purpose of this document

This is a self-contained execution plan for installing, configuring, and authoring Claude Code skills + reference documentation that will accelerate SiteForge's mapping and render-accuracy work. It was built from three rounds of investigation: a review of the project's accumulated memory, a codebase audit of rendering/mapping hotspots, and a GitHub skill research pass.

If you are a fresh Claude Code session reading this to execute the plan: start at §8 "The Plan" and gate each phase on the previous one. §2–§7 give you the context you need to make judgement calls.

---

## 1. What is SiteForge?

SiteForge is an AI-powered architectural site planning app. Architects draw zones on a map, assign building archetypes to each zone, and generate photomontage-quality AI renders (aerial + street view) of what the site could look like.

**Tech stack:**
- **Frontend:** React 18, TypeScript 5.6, Vite 6, Three.js, `@react-three/fiber`, Cesium, Mapbox GL, Zustand, TanStack Query, Tailwind — runs on port 5174
- **Backend:** Python FastAPI, SQLAlchemy 2 + asyncpg, PostgreSQL + PostGIS, Redis, Celery — runs on port 8000
- **AI pipeline:** Google Gemini 3.1 (`gemini-3.1-flash-image-preview`) via REST, with multi-image prompt assembly (clay massing anchor + previous render + layout image + archetype reference images)
- **Mapping:** Recently migrated from Mapbox Satellite to Google 3D Photorealistic Tiles via Cesium + Three.js (r170). Mapbox still used for 2D overlays.

**Render pipeline at a glance:**
1. User draws zones on map → assigns archetype per zone
2. Each archetype gets a unique polygon color (`archetypeShadeMap.ts`)
3. Screenshot + binary mask generated from zone colors
4. Prompt assembled from archetype metadata + style + constraints + reference images
5. `POST /api/v1/render` → Gemini API
6. Post-processing (sharpen, contrast, color) → composite onto map

**Relevant large files (read specific line ranges, not whole files):**
- `frontend/src/components/viewer/useAIRender.ts` (134 KB) — aerial render, prompt building, mask generation, stitching
- `frontend/src/components/viewer/useStreetViewRender.ts` (87 KB) — street view, SCHEMA-style prompts, depth planes
- `frontend/src/components/viewer/ZonePropertiesPanel.tsx` (147 KB)
- `frontend/src/components/viewer/SiteZonesGroup.tsx` (113 KB)
- `backend/app/api/v1/site_zones.py` (93 KB)
- `backend/app/api/v1/render.py` — Gemini proxy
- `frontend/src/data/buildingArchetypes.json` (841 KB) — 97 building archetypes
- `frontend/src/data/streetPathArchetypes.json` — 36 street types
- `frontend/src/data/openSpaceArchetypes.json` — parks & plazas

**See also:** `CLAUDE.md` at project root for authoritative project conventions.

---

## 2. Why this work matters: the problem

SiteForge's priority accuracy goals, in order:
1. **Spatial accuracy** — polygons the user draws must become buildings in the correct location, orientation, and scale in the rendered image
2. **Archetype accuracy** — the building type the user assigns must be recognizably rendered (not a hallucinated plausible-but-wrong variant)
3. **Render quality** — photomontage-quality output, correct color temperature, no hallucinated content outside polygon boundaries

The current tooling is under-equipped for these. Debug sessions mix multiple variables (logged 2026-04-17), reference image generation hallucinates (skatepark appearing under tennis courts), and coordinate math is duplicated across 4 files — including a self-contradicting mix of `110_540` and `111_320` inside `useStreetViewRender.ts` alone. A code audit on 2026-04-18 also surfaced a broken `video.py` endpoint (never registered, missing config), an insecure default JWT secret, and a stale `CLAUDE.md` temperature claim that was corrected the same day.

Given the Gemini model treats the mask as *advisory* (not a hard constraint), prompting and reference-image quality are load-bearing. Skill-shaped tooling can accelerate those workflows in ways raw code fixes cannot.

---

## 3. Investigation summary (how this plan was built)

### 3.1 Memory review

All files in `C:\Users\andre\.claude\projects\C--Users-andre-OneDrive-Documents-Playground\memory\` were read. Key memory files that informed this plan:

- `feedback_containment_session_2026_04_17.md` — 2026-04-17: red-mask + zone-crop + auto-frame all tested together, lost attribution; manual zoom still wins
- `feedback_render_zoom_level.md` — polygon containment fails when zone is <8–15% of canvas
- `feedback_globe_render_experiments.md` — numbered labels/rainbow colors fail; archetype images are the key accuracy lever; short prompts win
- `feedback_reference_image_quality.md` — AI-generated refs hallucinate; must research real buildings first
- `project_google_3d_tiles.md` — globe render pipeline, archetype images, boundary clipping, DRACOLoader, experiment results
- `project_occluded_zone_rendering.md` — occluded zone fix via mask subtraction, two-pass, 3D annotations
- `project_z_axis_nadir_refs.md` — Z-axis collapse at 0° nadir, orthographic ground-truth refs
- `project_multi_view_references.md` — multi-angle aerial refs (90°/60°/30°) dramatically improve accuracy
- `project_globe_viewport_shim.md` — globe's map shim lacks `getZoom`/`fitBounds`/`easeTo`/`on` — feature-detect before calling Mapbox-only methods
- `project_render_accuracy.md` — per-zone sequential rendering + Meshy 3D model integration research
- `project_hybrid_render_architecture.md` — 5 pillars: LOD timing, GPU occlusion, stencil masking, hybrid prompts, memory

### 3.2 Research docs reviewed

From `docs/`:
- `GOOGLE_3D_TILES_RESEARCH.md`
- `SAME_ANGLE_DEGRADATION_DIAGNOSTIC.md` — **stale on seed claim**: identifies a seed-forwarding bug as highest-ROI fix, but the 2026-04-18 code audit found seed IS forwarded correctly at `render.py:512`. The remaining non-determinism has a different root cause (LOD streaming, fade animations).
- `BUILDING_TAXONOMY_RESEARCH.md`
- `ADAPTIVE_REUSE_VARIANTS_RESEARCH.md`
- `BUILDING_ORIENTATION_RESEARCH.md`
- `DISTRICT_KITS_RESEARCH.md`
- `SCHEMA_COLOR_FIDELITY_RESEARCH.md`
- `IMAGE_CARD_GAP_ANALYSIS.md` — city-kit directory/ID mismatch
- `CATEGORY_AUDIT_REPORT.md`

Also at project root: `NADIR_REFS_TASK.md`.

### 3.3 Codebase audit (fragility hotspots)

Top hotspots from the 2026-04-18 audit (corrected from earlier incomplete findings):

**BLOCKERs:**
- `backend/app/api/v1/video.py` (298 lines, untracked) — unregistered in router, `settings.veo_model` undefined, in-memory ops. `VideoGeneratePanel.tsx` frontend also orphaned. Appears to be abandoned POC.
- `backend/app/core/config.py:70` — `jwt_secret_key: str = "change-this-in-production"` — all tokens forgeable if env not set; no startup check.
- `frontend/src/components/viewer/useStreetViewRender.ts:26` vs `:178` — file contradicts itself: local constant `110_540` at line 26, hardcoded `111_320` at line 178 in the same file. ±780 m/deg error.

**HIGH:**
- `backend/app/api/v1/render.py:378-430` — ad-hoc multi-image `parts[]` assembly (no validation, hardcoded max of 6 archetype images, brittle MIME detection)
- `frontend/src/components/viewer/` — `METERS_PER_DEG_LAT` defined 4× with drift: `massingUtils.ts:16` (111320), `geoUtils.ts:301` (111320), `coordTransform.ts:8` (111320), `useStreetViewRender.ts:26` (110540)
- Three archetype resolvers return incompatible shapes: `collectArchetypeRenderInputs.ts:93`, `useGlobeAIRender.ts:677`, `useStreetViewRender.ts:99` — different fields, different prompt formats
- `frontend/src/components/viewer/useAIRender.ts:814-940` — binary mask generation via `getImageData` loops
- `frontend/src/components/viewer/useAIRender.ts:1200-1359` — hybrid stitch compositing with pixel-diff

**RESOLVED on re-audit (prior plans were wrong):**
- ~~Seed forwarding bug~~ — FALSE. `render.py:512` correctly forwards seed to Gemini `generationConfig`.
- ~~Hand-rolled WGS84 projection~~ — FALSE. `globe/globeProjection.ts:17-40` uses `WGS84_ELLIPSOID.getCartographicToPosition()` from `3d-tiles-renderer`.

**Docs-code contradictions found:**
- `CLAUDE.md` previously said "Temperature 0.0 for aerial renders" — code at `render.py:501` uses `temperature = 1.0` (Gemini 3 tuned for 1.0 per Google's guide). `CLAUDE.md` corrected 2026-04-18; see `project_gemini3_temperature.md` memory.
- Building `rotation_degrees` is set in UI (`types/index.ts:50`, `undoActions.ts:226`) but **never threaded into any render prompt**.
- `useGlobeAIRender.ts:1105` has `PERZONE_THRESHOLD = 99` with comment "per-zone disabled" — resolves prior single-shot vs per-zone ambiguity.

**Dead / unused in backend:**
- `core/config.py` has unused env vars: `fal_key`, `fal_style_model`, `layout_ai_provider`, `master_plan_2d_image_provider`, `master_plan_3d_image_provider`, `default_generation_engine`, `sentry_dsn` (loaded but never initialized).
- `.env.example` is only 4 lines; missing most required vars.

### 3.4 GitHub skill research

Evaluated:
- `obra/superpowers-marketplace` + underlying `obra/superpowers` repo
- `Nice-Wolf-Studio/claude-skills-threejs-ecs-ts`
- `CloudAI-X/threejs-skills`
- `mrgoonie/claudekit-skills`
- `anthropics/skills` (official)
- `google-gemini/gemini-skills` (official) — **surfaced in research, not initial plan**
- `b-open-io/gemskills` — **surfaced in research; biggest find**
- `mapbox/mapbox-agent-skills` (official)
- `AlpacaLabsLLC/skills-for-architects`
- `guinacio/claude-image-gen`
- `kingbootoshi/nano-banana-2-skill`
- Various awesome-list aggregators (VoltAgent, ComposioHQ, travisvn, karanb192, etc.)

Skills verified via direct WebFetch of repo pages and SKILL.md files. Not all initial agent claims survived verification — see §7 for the rejected list.

---

## 4. Desired outcomes (what "done" looks like)

After this plan executes:

1. **BLOCKER cleanup landed.** `video.py` decision made (deleted or finished), JWT default secret hardened, `useStreetViewRender.ts` meter constants unified. These were discovered by the 2026-04-18 code audit and block trustworthy validation downstream.

2. **External skills are installed with justified scope.** Every skill in `~/.claude/skills/` (or project `.claude/skills/`) has a one-sentence justification tied to a specific audit finding in this document. No general-purpose 3D or generic Gemini skills — only those matching actual pain points.

3. **Custom skills exist for real gaps.** At least one custom skill exists for Cesium/photorealistic-tiles work (no public equivalent). Additional custom skills only if gemskills + official Gemini skills don't cover the pain point.

4. **Trigger conflicts are resolved.** Enumerated matrix of all skill triggers shows no overlap — fresh sessions will route tasks to the correct skill every time.

5. **`CLAUDE.md` reflects the new tooling state.** A fresh session reading `CLAUDE.md` knows which skills are installed, which are explicitly rejected, and why.

6. **Reference docs exist for non-triggerable knowledge.** Version matrices, attribution requirements, and Gemini prompt conventions live in `docs/` where they don't bloat skill triggers.

7. **Code-shaped fixes are identified.** The audit findings that need code changes (not skills) are listed as separate follow-up tasks, scoped and ready to execute.

8. **A go/no-go on visual regression is documented** with reasoning — not punted indefinitely.

---

## 5. Confirmed pain points (prioritized)

Every item below is backed by a specific memory file or code location. Items marked **SKILL** are skill-shaped (procedural knowledge / prompting / workflow). Items marked **CODE** need a code change, not a skill. Items marked **BOTH** benefit from both.

### 5.1 Spatial accuracy

- **[CODE, BLOCKER]** `useStreetViewRender.ts` self-contradicts on `METERS_PER_DEG_LAT` — local constant is `110_540` at line 26, hardcoded `111_320` at line 178. Values diverge ±780 m/deg in the same file. Addressed in Phase 0a.
- **[CODE, BLOCKER]** `video.py` + orphaned `VideoGeneratePanel.tsx` — abandoned POC, blocks unrelated work and risks `AttributeError` at runtime. Addressed in Phase 0b.
- **[CODE, BLOCKER]** Default JWT secret in `core/config.py:70` — all tokens forgeable if env not set. Addressed in Phase 0c.
- **[SKILL]** Polygon containment fails at low zoom (<8–15% of canvas). Gemini over-scales building ~10×. Source: `feedback_render_zoom_level.md`, `feedback_containment_session_2026_04_17.md`. Needs systematic multi-zoom A/B testing methodology.
- **[CODE]** Screenshot non-determinism from tile LOD streaming + fade animations + `map.once('idle')` race. Source: `SAME_ANGLE_DEGRADATION_DIAGNOSTIC.md` — note: that doc's seed claim is stale; the non-determinism is real but has a different root cause.
- **[CODE]** Globe viewport shim missing Mapbox methods (`getZoom`, `fitBounds`, `easeTo`, `on`) — `useAIRender.ts` uses them; feature-detect currently skips silently. Source: `project_globe_viewport_shim.md`. ~60-100 LOC Three.js math to implement properly.
- **[CODE]** `METERS_PER_DEG_LAT` defined 4× (drift across 4 files). Locations: `massingUtils.ts:16`, `geoUtils.ts:301`, `coordTransform.ts:8`, `useStreetViewRender.ts:26`. `metersPerDegLon()` also duplicated with inconsistent `Math.abs()` handling.
- **[SKILL]** Z-axis collapse at 0° nadir — students get paper-thin, watercolor buildings with no height. Fix: orthographic ground-truth reference images per archetype (pilot pending). Source: `project_z_axis_nadir_refs.md`, `NADIR_REFS_TASK.md`. Research + prompt engineering problem.

### 5.2 Archetype accuracy

- **[BOTH]** 81 color pairs in `archetypeShadeMap` have RGB distance <15 — confusable by Gemini. Per-zone sequential rendering is the only reliable fix but takes ~10–15s per zone (impractical for 29-zone sites). Source: `project_google_3d_tiles.md`. Swatch-image multimodal approach is a skill-shaped alternative.
- **[SKILL]** AI-generated reference images hallucinate. Vague archetype prompts cause model to invent plausible-but-wrong architecture (skatepark example). Source: `feedback_reference_image_quality.md`. Research-first workflow skill needed.
- **[SKILL]** 97 archetypes × 4 angles = 388 multi-view reference images needed; only 4 archetypes done. Source: `project_multi_view_references.md`. Workflow automation opportunity.
- **[CODE]** Building `rotation_degrees` never threaded into render prompts. Source: `BUILDING_ORIENTATION_RESEARCH.md`. Quick code addition.
- **[CODE]** Domain-prefix archetype resolver duplicated across `collectArchetypeRenderInputs.ts:93-172`, `useGlobeAIRender.ts:650-671`, `useStreetViewRender.ts:99-150`.
- **[CODE]** City-kit directory/ID mismatches — 68 city-kit archetypes have hyphenated directory names (`parisian-corner-with-dome`) but underscored JSON IDs (`parisian_corner_dome`). Source: `IMAGE_CARD_GAP_ANALYSIS.md`.

### 5.3 Render quality

- **[SKILL]** Gemini multi-image prompt assembly is ad-hoc. `backend/render.py:378-430` builds `parts[]` manually: clay anchor + previous render + layout + archetype refs. Each wrapped in `text()` + `inlineData()` by hand. Could benefit from standardized multi-image assembly conventions.
- **[CODE]** Mask hallucinations outside polygon boundary. Erode→blur→clamp (inward-only feather) upgrade designed but not implemented. Source: `project_google_3d_tiles.md`, `feedback_globe_render_experiments.md`. ~20 LOC.
- **[CODE]** Drag performance sluggish on globe — R3F re-renders entire tile scene per drag tick. Needs `useFrame`-based geometry updates to bypass React rendering. ~50 LOC.
- **[CODE]** Photogrammetry artifacts from Google 3D Tiles (texture stretch, mesh holes). `@react-three/postprocessing` DepthOfField already in `package.json` but not wired up.
- **[KNOWN]** Prompt length sweet spot ~200 chars per zone; longer degrades. Already encoded in memory, no action needed.

### 5.4 Recurring debug patterns

- A/B test isolation failures — multiple variables changed at once (2026-04-17 session)
- Runtime type assumptions — assumed Mapbox API exists; got shim
- Coordinate-space mismatches — DPR-scaled canvas vs logical coords
- Mask advisory confusion — users expect hard constraints, Gemini treats mask as visual context
- Screenshot non-determinism hidden by other variables

---

## 6. External skills evaluated

### 6.1 Install (matched to pain points)

| Skill | Source | Repo URL | Pain point addressed |
|---|---|---|---|
| `generate-image` | b-open-io/gemskills | https://github.com/b-open-io/gemskills | Gemini multi-image assembly (§5.3); 14-ref multimodal pattern |
| `edit-image` | b-open-io/gemskills | https://github.com/b-open-io/gemskills | Mask-based inpaint/outpaint (§5.1 occluded zones, §5.3 mask bleed) |
| `ask-gemini` | b-open-io/gemskills | https://github.com/b-open-io/gemskills | Research-first refs + visual QA (§5.2 hallucination) |
| `browsing-styles` | b-open-io/gemskills | https://github.com/b-open-io/gemskills | 169-style library exploration for archetype refs |
| `gemini-api-dev` | google-gemini/gemini-skills | https://github.com/google-gemini/gemini-skills | Backend API correctness (§5.3 assembly) |
| `gemini-interactions-api` | google-gemini/gemini-skills | https://github.com/google-gemini/gemini-skills | Multi-turn, image generation, structured output |
| `systematic-debugging` | obra/superpowers | https://github.com/obra/superpowers | A/B isolation methodology (§5.4) |
| `writing-skills` | obra/superpowers | https://github.com/obra/superpowers | Enables Phase 4 custom skill authoring |
| `mapbox-web-performance-patterns` | mapbox/mapbox-agent-skills | https://github.com/mapbox/mapbox-agent-skills | Drag perf on globe (§5.3) |

**Install method:** symlink individual skills, never full plugin installs. Gemskills targets `gemini-3-pro-image-preview` (Nano Banana Pro) while SiteForge uses `gemini-3.1-flash-image-preview` — procedural knowledge transfers; verify API shape during install.

### 6.2 Rejected (document in `skills/README.md` so future sessions don't re-evaluate)

| Skill / collection | Why rejected |
|---|---|
| `AlpacaLabsLLC/skills-for-architects` | Domain-adjacent but wrong problem. Covers NYC permit lookup (DOB, HPD, ACRIS, landmarks), zoning envelopes, materials research. SiteForge's pain is render engine accuracy, not site analysis. Would trigger on "architectural" prompts and give wrong help. |
| `guinacio/claude-image-gen` | Too-broad trigger ("building websites with hero sections, presentations, marketing"). No multimodal handling. Would fire in unrelated contexts. |
| `kingbootoshi/nano-banana-2-skill` | CLI tool, not skill-shaped. Uses same Gemini 3.1 Flash model as SiteForge — worth **reading source for reference patterns**, don't install as skill. |
| `CloudAI-X/threejs-skills` (all 14) | Generic Three.js (geometry, textures, lighting, animation, loaders, interaction). Zero overlap with WGS84/Cesium/photorealistic-tiles. |
| `Nice-Wolf-Studio/claude-skills-threejs-ecs-ts` | Game dev focus (ECS, input handling, mobile FPS). Wrong domain. |
| `anthropics/skills canvas-design` | About aesthetic composition (PDF/PNG art output). Does not address pixel-level masking / feathering / polygon clipping that `useAIRender.ts` needs. |
| `mrgoonie/claudekit-skills` (most) | Generic web/backend/auth patterns. `ai-multimodal` is too shallow to help. |
| VoltAgent/awesome-agent-skills aggregators | Mostly re-packaging other skills; surface noise. |

### 6.3 Confirmed gaps (no public skill exists)

These drive the §8.4 custom skill work:

- **Three.js + Cesium coordinate projection / WGS84 ellipsoid math** — nothing public
- **Canvas-based image masking primitives** — gemskills `edit-image` is server-side Gemini, not client-side canvas
- **Research-first architectural reference generation workflow** — research skills exist, image gen skills exist, but no skill chains them with visual QA loop

---

## 7. Guiding principles

1. **Evidence before installation.** Every install maps to a specific audit finding in §5.
2. **External skills before custom.** Audit gemskills against `render.py` before writing custom Gemini skills.
3. **Resolve triggers before installing.** Enumerate all trigger descriptions; resolve conflicts before symlinking.
4. **BLOCKER cleanup before big tools.** The `useStreetViewRender.ts` meter-constant bug, `video.py` cruft, and default JWT secret all block trustworthy downstream work. Fix them first.
5. **Narrow triggers for custom skills.** Every custom skill's trigger description must exclude situations better-served by external skills.

---

## 8. The plan

Phases gate each other. Do not start phase N+1 until phase N's deliverable exists.

### Phase 0 — BLOCKER cleanup

**Why first:** The 2026-04-18 audit surfaced three blockers that poison downstream work — a self-contradicting coordinate constant in street view, an abandoned `video.py` POC that crashes at runtime, and a default JWT secret. Until these are resolved, any A/B validation, security posture, or new feature work risks being contaminated or broken.

**Action (three small, parallel fixes):**

**0a. `useStreetViewRender.ts` meter-constant unification**
1. Read `frontend/src/components/viewer/useStreetViewRender.ts:26` and line `:178`
2. Decide authoritative value — `111320` matches the other three files (`massingUtils.ts`, `geoUtils.ts`, `coordTransform.ts`). `110540` is an outlier — likely a transcription error or stale value.
3. Unify on `111320`, remove the hardcoded `111_320` at line 178 and reference the local constant.
4. If street view coord math breaks after the change, the outlier may have been compensating for another bug — investigate rather than revert.

**0b. `video.py` decision**
1. Confirm with the user: delete or finish? Evidence strongly favors delete (never committed, no router registration, missing `veo_model` config, orphaned frontend panel, "local prototype" comment at `video.py:113`).
2. If delete: remove `backend/app/api/v1/video.py` and `frontend/src/components/viewer/VideoGeneratePanel.tsx`. Grep for any remaining references.
3. If finish: add `veo_model` to `config.py`, register router in `api/v1/router.py`, persist `_operations` to Redis with TTL, make token deduction transactional. Substantial work — should be its own plan.

**0c. JWT secret hardening**
1. `backend/app/core/config.py:70` — change default from `"change-this-in-production"` to raising `ValueError` if env var unset.
2. Add startup check that validates secret is at least 32 random chars.
3. Ensure `.env.example` documents `JWT_SECRET_KEY` as required (`.env.example` is currently 4 lines and incomplete — extend it with all required vars as a side benefit).

**What Phase 0 is NOT:**
- **Not a seed-forwarding fix.** Prior plans cited a seed discard bug at `render.py:476`. The 2026-04-18 audit confirmed seed IS forwarded correctly at `render.py:512`. `docs/SAME_ANGLE_DEGRADATION_DIAGNOSTIC.md` is stale on this point.
- **Not hand-rolled WGS84 cleanup.** Prior audits flagged `globeProjection.ts:17-40` as hand-rolled. It actually uses `WGS84_ELLIPSOID` from `3d-tiles-renderer` — no cleanup needed.

**Gate:** three fixes land, backend starts without errors, street view coord math verified against current test cases.

### Phase 1 — Audit

**Output:** `docs/cesium-audit.md`

Answer these questions:

**Cesium integration:**
- Is `Cesium.RequestScheduler.requestsByServer["tile.googleapis.com:443"]` tuned above the default 6?
- Is `showCreditsOnScreen: true` on the tileset? (Google ToS requires it.)
- Is the Cesium ion access token in env vars, uncommitted?
- Is `requestRenderMode: true` on the Viewer?
- Three.js + Cesium: shared WebGL context or separate canvases?
- Single source of truth for the camera matrix, or is it reconstructed across call sites?

**Codebase hotspots (post-Phase 0 consolidation):**
- After Phase 0a unifies `useStreetViewRender.ts`, diff all four `METERS_PER_DEG_LAT` definitions and consolidate to a single exported constant. Verify `metersPerDegLon()` uses consistent cosine handling (`coordTransform.ts:11` uses `Math.abs()`; others don't — determine if intentional).
- Diff `collectArchetypeRenderInputs.ts:93-172` vs `globe/useGlobeAIRender.ts:650-671` vs `useStreetViewRender.ts:99-150` — three resolvers return incompatible shapes with different facade-description formats. Decide on unified return type before consolidating.
- Confirm `globeProjection.ts:17-40` continues to use `WGS84_ELLIPSOID.getCartographicToPosition()` from `3d-tiles-renderer` (post-audit finding). No cleanup needed unless additional hand-rolled projection appears.
- Building `rotation_degrees` (set at `undoActions.ts:226`) is never read by any render hook. Decide: thread it into prompts (pain-point fix) or remove the UI control (dead-feature cleanup).
- `PERZONE_THRESHOLD = 99` at `useGlobeAIRender.ts:1105` effectively disables per-zone path. Decide whether to enable, lower the threshold, or delete the per-zone code.

**Compare-and-contrast with external skills:**
- Diff `backend/render.py:378-430` (manual `parts[]` assembly) against `gemskills/generate-image` multimodal pattern. Where does SiteForge's assembly diverge?
- Diff mask handling in `useAIRender.ts:697-710` against `gemskills/edit-image` inpainting conventions.

Tag each finding: **blocker** / **improvement** / **nice-to-have** / **out-of-scope**.

**Gate:** `docs/cesium-audit.md` written, every §5 pain point either confirmed, refuted, or scoped.

### Phase 2 — Install external skills

For each skill in §6.1, symlink it and add a one-sentence justification tied to an audit finding. Never install a full plugin.

**Deliverables:**
- Symlinks created (platform-specific — document the approach in `skills/README.md`)
- `skills/README.md` listing every installed skill, source, and justification
- `skills/README.md` also lists §6.2 rejects so future sessions don't re-evaluate
- `package.json` versions pinned for `three`, `cesium`, and any related packages

**Secrets check:** verify `.gitignore` covers any `.env` that holds Cesium ion tokens or Google Maps API keys. Never commit secrets.

**Gate:** all skills installed and justified; `skills/README.md` complete.

### Phase 3 — Trigger-conflict resolution

Enumerate every installed skill's trigger description. Any two that could fire on the same prompt — pick one or rewrite descriptions.

**Known conflict risks:**

| Conflict | Resolution |
|---|---|
| `ask-gemini` (gemskills) vs. `gemini-api-dev` (official) | Scope `ask-gemini` to image-generation/spatial-analysis/visual-critique; scope `gemini-api-dev` to SDK usage/API correctness |
| `systematic-debugging` (broad) vs. future `siteforge-render-diagnostics` | Narrow custom skill's trigger to "render pipeline A/B validation across zoom levels" |
| `generate-image` (gemskills) vs. future `siteforge-archetype-reference-gen` | Narrow custom skill to "research-first architectural reference generation" |
| Any Three.js skill vs. future `siteforge-cesium-tiles` | Custom skill triggers only on Cesium/photorealistic-tiles/Google 3D Tiles |

Document final trigger matrix in `skills/README.md`.

**Gate:** no two installed skills have overlapping triggers.

### Phase 4 — Custom skills (only for confirmed gaps)

Use `writing-skills` methodology (TDD for docs: write failing tests first).

#### 4a. `siteforge-cesium-tiles` (likely still needed)

No external skill covers WGS84 projection, `3d-tiles-renderer` interop, request scheduler tuning for Google photorealistic tiles.

Content (procedural only):
- Tileset initialization via `createGooglePhotorealistic3DTileset`
- Request scheduler tuning for `tile.googleapis.com`
- Camera setup + stable matrix for screenshot capture
- Lat/lng → screen pixel projection (consolidated from the 3 current sites)
- Globe disable pattern (`globe: false` or `scene.globe.show = false`)

Trigger description: narrow, only fires for Cesium / photorealistic-tiles / Google 3D Tiles work. Not general 3D.

Validate against two scenarios, both captured in `skills/siteforge-cesium-tiles/validation.md`:
1. "Set up a Cesium viewer with Google tiles centered on Stampede Park, 300m altitude, 45° pitch"
2. "Project these four lat/lng corners to pixel coordinates against the current camera"

#### 4b. `siteforge-render-diagnostics` (likely still needed)

Complements `systematic-debugging` with SiteForge-specific A/B methodology:
- Multi-zoom containment testing (addresses `feedback_render_zoom_level.md`)
- Pixel-diff variance measurement
- Seed-forwarding validation harness
- Single-variable-change enforcement for render experiments

Trigger description: narrow to render pipeline A/B testing.

#### 4c. `siteforge-archetype-reference-gen` (audit first — may not be needed)

After Phase 2, check if `gemskills/generate-image` + `gemskills/ask-gemini` + a research skill already covers the "find 4 real buildings → extract constraints → generate → visual QA" loop. **If yes, skip this skill.** If it leaves gaps, author a thin wrapper that chains the three.

#### 4d. Reference docs (not skills)

Split reference material out — skills trigger poorly when they carry reference bloat.

**→ `docs/cesium-setup.md`:**
- Version compatibility matrix
- Attribution / ToS requirements
- Token handling conventions
- Known-broken combinations (Three.js r170 + Mapbox Satellite framebuffer)

**→ `docs/gemini-prompt-conventions.md`:**
- SiteForge's multi-image ordering (clay anchor → previous render → layout → archetype refs)
- Gemini 3 temperature = 1.0 convention (Google-tuned; do NOT lower) — see `CLAUDE.md` and `project_gemini3_temperature.md` memory
- Seed forwarding is already working at `render.py:512`; document the expected determinism
- Color-fidelity guidance (including swatch-image approach if tested)

**Gate:** custom skills validated against their scenarios; reference docs written.

### Phase 5 — CLAUDE.md update

`CLAUDE.md` loads automatically in every Claude Code session, so pointers there matter more than their content.

Add a **Mapping Stack** section:
- Token handling rule (env vars only, never commit)
- Attribution requirement (one line)
- Link to `docs/cesium-setup.md` and custom skills
- Globe viewport shim caveat (feature-detect before calling Mapbox-only methods in `useAIRender`)
- Phase 0 BLOCKER cleanup status (video.py decision, JWT hardening, street view meters)

Add a **Render Pipeline Skills** section:
- Which external skills are installed and what they handle
- Which custom skills exist and what they cover
- Explicit "do not install general Three.js or generic Gemini skills" note to prevent future drift

**Gate:** fresh Claude Code session reading `CLAUDE.md` understands the tooling state.

### Phase 6 — Validate skill routing

Before declaring tooling work done, test each installed skill triggers correctly against real SiteForge tasks. For each test prompt, record which skill(s) fire.

| Test prompt | Expected to fire | Should NOT fire |
|---|---|---|
| "Add a new archetype reference image for a brownstone" | `generate-image`, `ask-gemini` | `AlpacaLabsLLC/*`, `canvas-design` |
| "Debug why Zone 3 renders outside its polygon" | `systematic-debugging`, `siteforge-render-diagnostics` | random Three.js skills |
| "Set up a new Cesium viewer centered on Calgary" | `siteforge-cesium-tiles` | `threejs-scene-setup` |
| "Project these corners to pixels against the current camera" | `siteforge-cesium-tiles` | — |
| "Wire up image editing with an inpaint mask" | `edit-image`, `gemini-interactions-api` | `canvas-design` |

Fix any routing mismatches by narrowing trigger descriptions. Re-test.

**Gate:** all routing tests pass.

### Phase 7 — Code-shaped fixes (parallel track, separate PRs)

These surfaced in the audit (§5) but are code changes, not tooling. Flag each as a separate follow-up task once tooling is in place:

1. `METERS_PER_DEG_LAT` consolidation — single source of truth across all 4 files, ~100 LOC savings (builds on Phase 0a)
2. Domain-prefix archetype resolver dedup across 3 files — unify return type, then consolidate
3. Globe viewport shim — add `getZoom` / `fitBounds` / `easeTo` with Three.js math (~60-100 LOC)
4. Erode→blur→clamp feather upgrade — mask edge cleanup (~20 LOC)
5. City-kit directory/ID mapping layer — unblock 68 city-kit archetypes
6. Building `rotation_degrees` — either thread into prompts or remove the UI control
7. DepthOfField post-process for photogrammetry artifacts (already in `package.json`)
8. Drag performance via `useFrame` geometry updates (~50 LOC)
9. `.env.example` extension — document all required env vars (currently only 4 lines)
10. Remove unused config vars from `core/config.py`: `fal_key`, `fal_style_model`, `layout_ai_provider`, `master_plan_2d_image_provider`, `master_plan_3d_image_provider`, `default_generation_engine`, `sentry_dsn`

Do not block this plan on any of these — they become separate tasks after the tooling lands.

### Phase 8 — Visual regression decision

Append to `docs/cesium-audit.md`:

**Default bias: no-go** until the Cesium layer stabilizes. Visual regression on a moving target burns time on drifting fixtures. Revisit after:
- Phase 0 BLOCKER cleanup validated
- Phase 7 consolidations land
- At least one stable Cesium integration release cycle

If reconsidered, start with a minimal Puppeteer harness on 3 fixed camera angles, not a full visual regression suite. Consider `chrome-devtools` from `mrgoonie/claudekit-skills` at that point.

---

## 9. Deliverables (gated)

| # | Deliverable | Produced in |
|---|---|---|
| 1 | Phase 0 BLOCKER cleanup: `video.py` decision executed, JWT secret hardened, `useStreetViewRender.ts` meter constants unified | Phase 0 |
| 2 | `docs/cesium-audit.md` with tagged findings | Phase 1 |
| 3 | Symlinked external skills + `skills/README.md` with justifications and rejects | Phase 2 |
| 4 | Trigger matrix appended to `skills/README.md` | Phase 3 |
| 5 | `skills/siteforge-cesium-tiles/SKILL.md` + validation; `skills/siteforge-render-diagnostics/SKILL.md` + validation; `skills/siteforge-archetype-reference-gen/SKILL.md` *if needed* | Phase 4 |
| 6 | `docs/cesium-setup.md` + `docs/gemini-prompt-conventions.md` | Phase 4 |
| 7 | `CLAUDE.md` updated with Mapping Stack + Render Pipeline Skills sections | Phase 5 |
| 8 | Skill routing test results (documented, pass) | Phase 6 |
| 9 | Chrome-devtools go/no-go in `docs/cesium-audit.md` | Phase 8 |

Phase 7 items become separate tasks post-plan, not gated here.

---

## 10. Constraints

- **Gemini pipeline constraint** from prior `CLAUDE.md` carried forward — Phase 0 items are all orthogonal to the Gemini render path, so no exception needed. If later work touches prompt assembly, confirm with user first.
- **No tool installed without a Phase 1 audit finding** backing it
- **No full plugin installs** — symlink individual skills only
- **No overlapping skill triggers** — enforce at Phase 3 before finalizing
- **Never commit** Cesium ion tokens, Google Maps API keys, or any secrets
- **Stop and report** if a tool conflicts with existing code rather than forcing it in
- **Do not `json.dump()`** `buildingArchetypes.json` — corrupts `thumbnailUrl` paths. Use text-level splice insertion. (From `CLAUDE.md`.)
- **Test locally on `localhost:5174`** before committing any frontend changes. (From `CLAUDE.md`.)
- **Two remotes must stay in sync:** `origin` → `aasedor/2D-Maps`, `beeman` → `beemanbesh/2D-Maps2`. Check both with `git log origin/master --oneline -5` and `git log beeman/master --oneline -5` before pushing. (From `CLAUDE.md`.)

## 11. Out of scope

- Prompt-engineering changes (Phase 0 items don't touch prompts)
- Archetype system restructuring
- UI polish / demo page styling
- MapleCard or any other project
- Rendering pipeline redesign (Phase 7 code-shaped fixes land in separate PRs)

---

## 12. For the Claude Code session executing this

1. **Start with Phase 0.** Three small orthogonal fixes (street view meters, `video.py` decision, JWT secret). For 0b, confirm delete-vs-finish with the user before acting.
2. **Do not skip phases.** The gates exist because each phase's output is input for the next.
3. **Read the memory files listed in §3.1** before making judgement calls about pain-point priorities. Note that two memories are superseded: `feedback_render_prompts.md`'s temperature claim is now in `project_gemini3_temperature.md`, and `SAME_ANGLE_DEGRADATION_DIAGNOSTIC.md`'s seed claim is stale.
4. **Do not re-evaluate §6.2 rejects** unless the user explicitly asks. That evaluation has been done.
5. **When authoring custom skills in Phase 4,** use the `writing-skills` methodology from obra/superpowers. Skills should trigger on symptoms, not solutions.
6. **When any skill's trigger seems broad,** rewrite it before installing — do not trust the upstream description blindly.
7. **Verify — do not assume** — before recommending something from a skill's docs, verify the actual API shape against SiteForge's `gemini-3.1-flash-image-preview` model (gemskills targets `gemini-3-pro-image-preview`).
8. **Update this document** if a phase's findings change the plan. Mark changes with date in §14 Revision history.

---

## 13. Appendix: URLs for external skills

- obra/superpowers: https://github.com/obra/superpowers
- obra/superpowers-marketplace: https://github.com/obra/superpowers-marketplace
- b-open-io/gemskills: https://github.com/b-open-io/gemskills
- google-gemini/gemini-skills: https://github.com/google-gemini/gemini-skills
- mapbox/mapbox-agent-skills: https://github.com/mapbox/mapbox-agent-skills
- anthropics/skills: https://github.com/anthropics/skills

---

## 14. Revision history

- **2026-04-18 (initial)** — Plan authored from three rounds of investigation (memory review, codebase audit, GitHub skill research).
- **2026-04-18 (post-audit revision)** — Phase 0 rewritten after a second code audit invalidated three premises:
  - Seed forwarding IS correctly implemented at `render.py:512` (prior plans claimed it was broken at `:476`)
  - `globeProjection.ts` is NOT hand-rolled — uses `3d-tiles-renderer`'s `WGS84_ELLIPSOID`
  - `CLAUDE.md` temperature claim was stale (0.0 → corrected to 1.0 for Gemini 3)

  NEW BLOCKERs surfaced: `useStreetViewRender.ts` self-contradicting meter constants, abandoned `video.py` POC with undefined config, default JWT secret. Phase 0, §5.1, §7.4, §9.1, and §10 updated to reflect.

---

**End of plan.** If you're picking this up cold in a fresh session, §1 (project context), §4 (desired outcomes), §5 (pain points), §8 (the plan), and §12 (execution notes) are the minimum you need to read before starting Phase 0.
