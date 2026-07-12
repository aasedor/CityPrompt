# Execution Run — 2026-07-12

One-day autonomous run against the plan in `~/.claude/plans/not-goodbye-yet-we-abundant-umbrella.md`
(follow-up to the Farewell Deep Dive). Locked decisions: ~$15 API + 100 Meshy credits,
scoped commits + feature-branch pushes only, render-accuracy priority.

## TL;DR

- **11 scoped commits banked and pushed** to origin2 + beeman (feature branch only) — three weeks
  of at-risk work (curvilinear engine + its production bugfix, 3D model library, Master Planner,
  park/globe frontend, transport standards, docs) is now off this machine.
- **Model migrated to GA `gemini-3.1-flash-image`** everywhere; the `guidance_scale` phantom that
  silently set temp 0.75 on every render is dead; `aspect_ratio` now threads end-to-end
  (verified in the backend log). The feared 1K preview cap did NOT reproduce on the REST path.
- **Pilot A (tiled park ref): mechanism CONFIRMED** — tiled ref → more, smaller courts. Cost:
  photorealism regressed + literal grid echo. Next form: tiled ref alongside a photoreal ref.
- **Pilots B + C are implemented, committed (flags OFF), and their mechanics verified in-app**:
  auto-frame flew the camera to ~55% framing of 99 zones in 856 ms; the clean-capture event
  round-trip produces an overlay-free composite base in the same coordinate space.
- **Vertex-Canada question CLOSED: no image model exists in northamerica-northeast1** (probe via
  service account; gemini-2.5-flash-image provably exists in us-central1 but 404s in Montreal;
  Imagen 3/4 gone everywhere post-shutdown). Compliance pack must lead with no-PII, not residency.
- **momepy 1.0 pilot: SUCCESS** — COINS + parcel metrics run on curvilinear plans and cleanly
  discriminate scenarios (economic 138 strokes/89 m · environmental 201/82 · city_beautiful 97/114).
- **Backend image rebuilt** — rembg/onnxruntime finally live in the running container.
- **Meshy balance-floor guard added** (`meshy_min_balance_floor=100`, there was NO spend guard).
  Multi-view chain pilot: see § Meshy below.
- **A concurrent session was live in this working tree** (master-planner style-family redesign +
  paneShim hardening). De-conflicted by ownership boundary; their in-flight files were left alone.

Spend: ≈ **$1.60 API** (13 Gemini images) + **Meshy pilot credits** (see below). Well under caps.

## Tonight's 10-minute review

1. Open `artifacts/exec-2026-07-12/contact-sheet.html` — judge Pilot A's tiled-vs-single renders
   and the 2×2 model comparison.
2. In the app (dev): set `localStorage.cc_auto_frame='1'` and `cc_clean_composite='1'`, run one
   render on a small project from a deliberately-wrong zoom, and compare against flags-off.
   Both flags are OFF by default and safe to leave on if you like what you see.
3. Meshy pilot GLB: `artifacts/exec-2026-07-12/meshy-pilot/` — check mullion straightness and
   rear faces vs the wave-1 model.
4. If all green: the branch is pushed; PR when you're ready.

## Phase 0 — Baseline

Containers all up; 310 dirty entries. Docker test baseline: **70 passed / 4 failed** — all 4 in
`test_master_planner.py` (palette/alternates; the concurrent session was mid-redesign of exactly
these — see Coordination). Curvilinear 19/19, block subdivision, placement, meshy all green.

## Phase 1 — Banking (11 commits, pushed)

`7cab772` plan_geometry tangle (curvilinear + module segmentation, +2211/−133, tests included) ·
`ea08cd2` 3D model library · `a44b80d` Master Planner + flags · `b85cc89` parks/globe frontend ·
`d518c4b` transport standards · `7f536ad` docs · `fea7549` orphaned parks_plazas PNG deletions
(140 files — verified unreferenced by grep before committing) · `41f015d` seededRandom
(**the branch was missing a file** — parkScatter + useStreetViewRender import it) + batch tooling ·
then `f614754` config truth pass · `d773151` variant-id port · `4f19fb4` pilots B+C ·
plus the Meshy guard. Hotfix extraction via `git add -p` was skipped deliberately: a plumbing-staged
partial file can't be tested without disturbing the working tree; an honest tested tangle commit
beats an untested "hotfix". The curvilinear ring-drop fix is inside `7cab772` and cherry-pickable.

Secrets scan on the config diff before push: names/empty defaults only.

## Phase 2 — Model id + config truth (`f614754`)

- 2×2 pilot: all four cells returned 2K-class output — **js-genai #1461's 1K cap did not reproduce
  on REST `generateContent`** (it's SDK/Vertex-path specific). GA + clean params ≥ current quality.
- Migrated ~15 pins (backend render.py/image_cleanup/config, frontend hooks + panel + parkGroundTexture,
  3 active scripts). Preview alias kept in allowed-models/cost-map for back-compat.
- Deleted the `guidance_scale`→temperature mapping; **no temperature is sent at all now** (docs list
  none for image config). Schema field kept accepted-but-ignored.
- `aspect_ratio` threads: frontend computes `nearestAspectRatio(canvas)`; backend whitelists and
  forwards into `imageConfig`. **Smoke-verified end-to-end**: 200, JPEG 2752×1536 at requested 16:9,
  log line `imageSize=2K, aspectRatio=16:9`.
- CLAUDE.md stale claims fixed (temp-0.0 rule retired, GA id noted).
- Frontend seed/temp UI: **does not exist** (stale memory) — nothing to remove. Street view's
  hardcoded `temperature: 0.35` left untouched (SV pipeline working; out of scope).

## Phase 3 — Render-accuracy pilots

**A · Tiled park ref** (4 renders, ~$0.30): single ref → ~28 photoreal courts; 3×3 tiled ref →
~36 smaller courts **but** flat/CGI style contamination + composition echoing the 3×3 grid.
Verdict: *the ref image sets rendered scale* (the 2026-05-29 hypothesis) is *confirmed*; the naive
tiled form costs photorealism. Next experiment: tiled ref as a SECOND ref beside the photoreal
card, or 2×2 with perspective-varied crops. Caveat: synthetic flat-colour scene, not in-app tiles.

**B · Auto-frame** (`4f19fb4`, flag `cc_auto_frame`): `frameZonesForRender` in GlobeSitePlannerMap —
iterative apply-pose→project→adjust-height to ~55% at the default oblique pitch, exposed on the DEV
`__globeDebug` handle, consumed in `render()`. **Verified in-app**: from a wide city view it framed
the Water Centre's 99 zones at ~50–55% in 856 ms (contact sheet 04). No camera restore yet (pilot
limitation). Paid quality A/B = your judgement tonight.

**C · Clean-composite base** (`4f19fb4`, flag `cc_clean_composite`): discovery — the July-7 work
already made the RAW capture the clip base (labels never leak), so the remaining gap was only the
**in-scene grey zone fills** polluting the feathered seam ring. Now: render() captures one
overlay-hidden frame (`cityprompt:hide-zone-overlays` event, honored by GlobeZoneLayer) and the
clip composites against it. **Verified in-app**: identical frame with overlays cleanly gone
(contact sheet 02 vs 01) — same camera, same coordinate space. Both captures exposed on
`window.__renderDebug`. Two-pass stylized base path unchanged.

**D · Variant-id port** (`d773151`): `useAIRender:2247` and `useStreetViewRender:1957` read the
stale `selected_variant` integer → user's variant choice silently fell back to variant 0/hero.
Ported the canonical `*_selected_variant_id` resolution; 35/35 related tests green.
NOT done: the SV "collected 0 archetype cards" root-cause diagnosis (needs a live SV render run;
the key-logging approach is specced in the plan).

## Phase 4 — Pipeline & data

- **Vertex-Canada probe (CLOSED)**: via the service account, `:predict` error-shape probe —
  Montreal 404s every image model incl. gemini-2.5-flash-image, which provably EXISTS in
  us-central1 (400 "wrong API surface"). Imagen 3/4 are 404 in BOTH regions (post-June-30 shutdown
  confirmed in practice). **There is no Canada-resident image generation on Google, Azure
  (July-8 matrix), or Bedrock today.** Municipal positioning: no-PII argument + PIA pack.
- **momepy pilot (SUCCESS)**: installed ephemeral in the container (NOT in requirements — adding
  geopandas/momepy to the image is a decision for you; ~200 MB layer). COINS + parcel-area metrics
  ran clean on three generated plans incl. curvilinear networks and discriminated scenarios.
  Numbers above. Wiring into plan_evaluator + scenario cards is a clean next step.
- **Docker image rebuilt + containers recreated** (compose project preserved, DB volume intact,
  health OK, `import rembg, onnxruntime` passes). Note: recreate needed `--force-recreate` —
  a plain `up -d` kept the old sha-pinned container.
- **Meshy balance-floor guard** (committed): `meshy_min_balance_floor=100` in config, enforced at
  the top of `MeshyEngine.run_generation` via `get_balance()`. Balance at run start: 9,020.
- **Meshy multi-view chain pilot**: PENDING at report-writing time — chain launched
  (i2i multiview nano-banana-pro → `multi_image_to_3d(input_task_id=…)`, 30k tris). Results land in
  `artifacts/exec-2026-07-12/meshy-pilot/` (progress.log, task JSONs, GLB, cardinal thumbnails).
  See the addendum at the bottom of this file.
- **NOT done** (time): Calgary trees/air DNA layers (specs verified available; adapter work
  ~1 day), lightingMap fill (`docs/RENDER_STYLES_DEEP_DIVE.md` does NOT exist in this tree —
  needs a `git log --all` hunt or fresh authoring), SV 0-cards diagnosis.

## Coordination note (important)

A **concurrent session was actively editing this working tree during the run**: master_planner
`agent.py` (+70/−18, style-family coherence redesign using `load_families`/archetype_families),
`test_master_planner.py`, `plan_geometry/archetypes.py`, and `frontend/index.html` (paneShim
localhost-gating) — mtimes updated seconds after my commits. My Phase-1 commits captured harmless
snapshots of their mid-flight state; their newer edits remain uncommitted in the working tree.
I declared those files off-limits from that point (skipped `build_archetype_families.py` +
`export_archetype_plan_dims.py` in the tooling commit for the same reason). **The 4 red
master-planner tests are theirs to land.** Files still dirty at end of run = their WIP + scratch.

## Environment notes for future sessions

- Browser-pane e2e: `resize_window` with EXPLICIT width/height (the desktop preset left the
  viewport 0×0); direct canvas capture + POST to a local receiver works where pane screenshots
  time out; **something already squats on port 5199** (an old capture receiver?) — use 5198.
- Auth for e2e: mint a JWT in-container (`create_access_token(user_id, role)` from
  app.core.security), set `access_token`/`refresh_token` in localStorage. The gmail user id is
  `651daf60-b797-4f95-b1e7-6364d6dc0665` (owns the 100-zone Water Centre:
  project `15d28a31-b90d-4e2f-8163-11f41aa499f8`).
- Zones endpoint: `/api/v1/site-zones/projects/{id}/zones`.
- Dev server: port 5174 was occupied (concurrent session) — vite auto-bumped to 5175 while the
  preview harness guessed another port; read the vite banner, not the harness.

## Spend

Gemini: 4 (2×2) + 1 (smoke) + 4 (tiled pilot) ≈ 9 images ≈ $1.20 · GPT: 0 ·
Meshy: pilot chain (see addendum; expected ~39 credits of the 100-credit cap).

## Test verification (Phase 5)

See addendum — re-run of the Phase-0 pytest command after all changes.

## Addendum — Meshy pilot result + final verification (written at end of run)

**Meshy multi-view chain pilot: SUCCEEDED end-to-end.** Card → `image_to_image_multiview`
(nano-banana-pro) → `multi_image_to_3d(input_task_id=…, 30k target)` → GLB.
- **39 credits exactly** (balance 9,020 → 8,981) — matching the memory's estimate; the
  100-credit floor guard held irrelevant headroom.
- **30,215 triangles** (right at target), single geometry, **14.9 MB GLB** — over the 8 MB budget
  because this supervised run bypassed the glb_optimizer texture pass; production path would
  shrink it. `artifacts/exec-2026-07-12/meshy-pilot/pilot_plus15.glb` + task JSONs.
- Oddities to know: the polled multiview task returned a MODEL-task shape (model_url) with
  `image_urls` empty, and `multi_view_thumbnails` came back empty; thumbnail URLs 403 outside the
  API client. **Judge the mesh in the GLB viewer tonight** (mullion straightness, rear faces,
  Plus-15 bridge) vs the wave-1 model.

**Final test verification: 83 passed, 0 failed** (Phase-0 baseline was 70 passed / 4 failed).
The 4 master-planner reds went green via the CONCURRENT session's style-family work landing in the
working tree during the day (they also added tests). No red introduced by any change in this run.

Final spend: ~$1.60 API + 39 Meshy credits — well under the $15 + 100 caps.
