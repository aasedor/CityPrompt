# City Prompt — "What We've Already Tried · Do-Not-Retry" Report

**Date:** 2026-06-17 · **Branch:** work/beeman-main-2026-05-21b · **Goal:** avoid re-running anything that already failed.
**Method:** parallel sweep of memory + docs + git history + pilot scripts (7 agents), deduped and cross-checked against the proposed next steps. Successor/refresh of `docs/RENDER_EXPERIMENT_LEDGER_2026_05_29.md`.

**The single load-bearing fact** (re-verified 4× — 2026-05-21, 06-01, 06-07, 06-17): both shipped renderers (`gemini-3.1-flash-image-preview` and `gpt-image-2`) are **SOFT conditioners**. No commercial image API exposes a hard depth/segmentation/edge/mask channel as of June 2026. The mask is **advisory**; the only true enforcement is the post-process polygon clip. *Every* text-only spatial fix (containment, park-scale, occlusion, lane-count) has failed for this one reason. Treat any proposal whose premise is "tell the model to stay inside / don't enlarge / lock pixels" as already-refuted.

---

## 1. The Do-Not-Retry Ledger

Deduped across memory, docs, git, and scripts. "Revisit only if" = the one narrow condition under which a *variant* is defensible.

| # | What was tried | Why it failed | Source(s) | Revisit only if |
|---|---|---|---|---|
| 1 | **Text-only park-scale fix** (prompt scale-anchor: "benches 2m, soccer 100×60m, tile don't enlarge" + drop count phrases) | User: *"these do not work great. revert."* Gemini's fill-to-mask bias overrides text. | feedback_large_park_scale_prompt_fix_failed; OPEN_ISSUES P0#1; LEDGER §1 P3 | Never as text. Ref-image (pre-tiled grid) is the lever — §6. |
| 2 | **Any text-only containment** ("stay inside polygon", "polygon edges ARE the walls") | No spatial channel to obey. Root cause of Problems 1 & 3. | RENDER_FIX_IMPL §0; OPEN_ISSUES Part2; GLOBE_POLYGON_AUDIT | Never. |
| 3 | **Numbered label circles / markers on screenshot** | Gemini renders the circles INTO the scene as white discs. | RENDER_EXPERIMENTS Exp 5 (72f7724, rev 1ca17b8/dba53ae) | Never (visual-noise-bleed cluster). |
| 4 | **Rainbow / 30 vivid zone colors** | Vivid fills bleed → magenta walls, blue roofs. | RENDER_EXPERIMENTS Exp 7 (fa8483a, rev dba53ae) | Never — muted natural colors. |
| 5 | **3D wireframe building borders on screenshot** | Drawn overlays bleed into renders. | git 3699863 rev 79b6ea2; LEDGER §1 P1 | Never. |
| 6 | **Both-images approach** (satellite + separate zones-overlay image) | *"Worse — Gemini reproduced zone outlines."* | git 3d158d2 | Never. |
| 7 | **Longer per-zone prompts** (200→500 chars; verbose 3-block) | WORSE, reverted twice. *"More detail ≠ better."* ~200 chars is the sweet spot. | RENDER_EXPERIMENTS Exp 11 (d4b7c3d rev d9fce34) | Never for placement. |
| 8 | **Full 29-zone legend in one prompt / 3-pass category** | Generic buildings — model can't bind 29 polygons to archetypes (~40-50% placement). | RENDER_EXPERIMENTS Exp 3-4 | Never as a single long prompt. |
| 9 | **Per-zone sequential rendering on globe** | ~50s/call → ~17min/29 zones; cumulative degradation (Pass-1 output feeds Pass-2 input). `PERZONE_THRESHOLD=99` disables. | RENDER_EXPERIMENTS Exp 2; LEDGER §4 #3 | Only if globe calls ~10× faster AND heavy-site fallback. |
| 10 | **Per-zone CROP → generate → composite back** | Building landed OUTSIDE polygon — DPR canvas px vs logical clip coord mismatch. Reverted unfixed. | feedback_containment_session_2026_04_17 #2; RENDER_FIX_IMPL 3.4 | Only if the coord bug is fixed FIRST. |
| 11 | **1K output resolution** | Small polygons don't render at 1K. Reverted to 2K. | git 2f5d521 rev bfedf4d | Never. |
| 12 | **destination-in mask clip to boundary** | Entire mask turned black. | RENDER_EXPERIMENTS Exp 9.1 (85eb191 rev cc515b4) | Never — `ctx.clip()` is the replacement. |
| 13 | **White boundary outline on mask + "stay inside"** | Gemini ignored it; builds outside. | RENDER_EXPERIMENTS Exp 9.2 (3c45396 rev cc515b4) | Never. |
| 14 | **Gaussian blur(6px) outward feather** | Bled outward past polygon. → blur(4px)+inward clamp. | feedback_globe_render_experiments; LEDGER §6 | Never (erode→blur→clamp inward). |
| 15 | **Building headroom expansion (extend clip upward)** | "Worse," reverted. | CHAT_HISTORY | Never. |
| 16 | **Clean base screenshot (hide ALL zones)** | Didn't work, reverted. (Narrow "hide zone LAYERS for border-bleed" WAS kept.) | CHAT_HISTORY | Never (narrow layer-hide is kept). |
| 17 | **Occlusion culling at 40-60% threshold** | Culled partially-visible zones. Fixed at ≥95%. | project_occluded_zone_rendering; PORT_PLAN "Do NOT retry" | Never below 95%. |
| 18 | **Occluded-zone prompt hints + pixel/lat-lng coords in prompt** | Model ignores hints; coords have no spatial grounding. | project_occluded_zone_rendering; PORT_PLAN | Never — mask subtraction is the fix. |
| 19 | **0-1000 normalized grid / 3×3 placement directive** | Category error: 0-1000 is Gemini's *output* bbox format, not a generation *input*. | GEMINI_REVIEW_ASSESSMENT #6/#7 | Never. |
| 20 | **16 reference images (4 zones × 4 angles)** | >~6 hi-fi refs scramble placement. *Fewer accurate >>> many.* | RENDER_EXPERIMENTS Exp 12 | Cap ~6; single labeled grid is the untested variant (§6). |
| 21 | **AI-generated aerial refs not grounded in real buildings** | Hallucinations faithfully reproduced (skatepark under tennis ref). | RENDER_EXPERIMENTS Exp 12; feedback_reference_image_quality | Only refs grounded in real-building research. |
| 22 | **Street-level refs for an AERIAL render** | Model mentally rotates 60-90° → "prettier but wrong spot." | AERIAL_LIKE_STREETVIEW_PLAN Exp 0 | Never — match ref angle to camera. |
| 23 | **"ALONE in frame / no other buildings" clause** | Killed rowhouse/terrace typologies. | LEDGER §1 P2; feedback_aerial_subject_text_richness | Never. |
| 24 | **Metadata-list subject text** | "A shopping list gives Gemini no picture." → 6-element prose. | feedback_aerial_subject_text_richness | Never (use prose). |
| 25 | **Temperature 0.0 / 0.35 on Gemini 3 image** | Gemini 3 is tuned for 1.0; below degrades/loops. (CLAUDE.md "temp 0.0" is STALE.) | project_gemini3_temperature; git 9192748 rev 6b5972c | §4-C — unresolved part is what temp actually *reaches* Gemini. |
| 26 | **Gemini-3-Pro + forced temp-1.0 two-pass for street view** | HAZE/washed-out; wrong cause (real = stale satellite ref). Reverted. | project_render_debug_state_2026_06_15 | Never (diff vs last-known-good first). |
| 27 | **STRICT SCENE BOUNDARY prohibition + screenshot-after-hide + media_resolution HIGH** | "Worse," reverted. | git d4dc22b rev 6bc91b3 | Never. |
| 28 | **Hard-mask inpaint on the Gemini endpoint** | HALLUCINATED API — gemini-3.1-flash only does semantic editing; true inpaint only on Vertex imagen-3.0-capability-001. | feedback_verify_llm_api_claims | Never on this endpoint. |
| 29 | **thinkingBudget > 0 for image gen** | No benefit; -30-50% latency; caused 502s. Set to 0. | GEMINI_REVIEW #5 | Never (keep 0). |
| 30 | **FLUX as the WHOLE renderer** (2024 fal.ai, screenshot-estimated depth) | User: *"FLUX was not great."* Migrated away. | project_render_quality_tooling_direction_2026_05; git 9dd776a/bfec73d | Never as the whole renderer. |
| 31 | **FLUX depth-ControlNet as a 3rd in-app engine** | **WORST of three incl. massing — opposite of the offline pilot. Fully REVERTED.** In-app depth map was a flat-plate silhouette, not 3D volumes. | project_depth_conditioning_pilot_2026_06_07; artifacts/depth-pilot/ | Only with a genuinely-3D depth source + two-stage structure→finish, NEVER standalone. §4-E. |
| 32 | **GPT Image 2 always-on dual-render (`Promise.all`)** | ~3min/render; one engine 5xx kills the whole render. | project_render_debug_state_2026_06_15 | Never always-on; opt-in + `Promise.allSettled`. |
| 33 | **GPT Image 2 as default street-view engine** | 502s + business hallucination. Gemini-only/opt-in is the fix. | project_render_debug_state_2026_06_15 | Opt-in only on street-view. |
| 34 | **Coerce GPT Image 2 to stylize via prompt/style-ref** | Failed ×3 — stays photoreal; style-exemplar content bleeds through. | feedback_gpt_image2_vs_gemini_routing | Never — route artistic→Gemini. |
| 35 | **Empty-horizon VOID DEFINITION prompt** ("no buildings/towers") | Street dissolved into a glowing void. Softened to affirmative "continue surroundings, do NOT invent." | project_render_debug_state_2026_06_16 | Never — affirmative scene-completion. |
| 36 | **Vector cross-section as a soft REF for a PHOTOREAL card** | Clip-art icon cars/people pasted into the photo. → prompt-only photoreal cards. | project_calgary_street_manual_archetypes | Never for photoreal cards (≠ diagram-as-input, §4-A). |
| 37 | **Hardcoded Rockies/mountains/furniture in every Calgary prompt** | Phantom sidewalks/trees; Rockies on every street. → zone-derived + prairie horizon. | project_calgary_street_manual_archetypes | Never bake one backdrop into every render. |
| 38 | **Negative prompts that name unwanted scene objects** ("Do NOT include: buildings") | White-bear effect; no real negative field exists. (CONFLICT: an Apr note claimed 94% compliance — §4-C.) | RENDER_ISSUES #3; reference_prompt_language_bestpractice_2026; LEDGER §4 #1 | Keep ONLY meta-artifact negatives (watermark/text); rewrite scene ones affirmatively. |
| 39 | **Film grain + lens bloom post-fx** | "Reads as degraded/Nolan-film." Reverted. (Color/tone grade IS kept.) | feedback_render_post_processing_taste | Never — texture FX out, color/tone in. |
| 40 | **GPT's alley-edge & flat-median geometry biases** | Persist across seeds (real GPT behavior, not variance). | project_calgary_street_manual_archetypes | Re-rolling won't fix; route to Gemini. |
| 41 | **Node-type 90° nadirs re-rolled WITHOUT the prose fix** | "WORSE." Need "junction box fills frame, buildings cropped" clause. | project_traffic_safety_visualization_2026_06_12 | Only with the prose fix. |
| 42 | **Section-stylized diagram as variant `thumbnailUrl`** | Consumers derive render-ref + aerial stems from it → flattened renders. | project_calgary_street_manual_archetypes | Never — photoreal=ref, stylized=display-only. |
| 43 | **Drape shapefile vectors directly onto Google photogrammetry** | 4 failed iterations — canopy parallax drift on slopes. → bake onto bare-earth elevation. | project_shapefile_import_2026_06_10 | Never on steep vegetated slopes. |
| 44 | **Aggressive 3D-tile loading (errorTarget=1, loadSiblings)** | Overwhelmed loader → nothing rendered. | git 567e6cf | Never. |
| 45 | **OAuth CSRF httponly state cookie** | Breaks Google login (cross-domain callback). | git 27756ae rev aba1c8d | Only with server-side session. |
| 46 | **Semantic per-type color map for OBLIQUE aerial** | Works top-down only, breaks at steep angles. | CHAT_HISTORY | Top-down only. |
| 47 | **`generate_park_street_variants.py` (Gemini 2.5, NO_PEOPLE) for new cards** | "Visibly worse." Use `generate_card_images.py` Style 6. | feedback_style6_card_pipeline | Never for new cards. |
| 48 | **`json.dump()` on buildingArchetypes.json** | Corrupts `thumbnailUrl` (underscores→hyphens). | CLAUDE.md; feedback_json_dump | Never — splice raw text. |
| 49 | **GPT Image 2 `input_fidelity` toggle** | FABRICATED — parameter removed/locked-high; no settable fidelity knob. The lever is the reference image. | DIAGRAM_CONDITIONING_RESEARCH "Don't chase" | Never. |
| 50 | **"Contract vs suggestion" layout-lock directive** | FABRICATED — no such layout-lock exists. | DIAGRAM_CONDITIONING_RESEARCH "Don't chase" | Never. |
| 51 | **Re-blaming the SEED for same-angle drift** | DEAD DIAGNOSIS — seed forwarded (confirmed 04-18). Real cause = capture non-determinism (LOD/fade racing screenshot). | LEDGER §4 #4; SAME_ANGLE_DEGRADATION_DIAGNOSTIC; git 7fd8dd0 | Never — fix capture timing. |
| 52 | **Camera jitter / multi-sample averaging for drift** | DEPRIORITIZED before trying, behind seed+timing root-cause fix. | SAME_ANGLE_DEGRADATION_DIAGNOSTIC | Only after seed+timing fixes exhausted. |

---

## 2. Tried-and-Worked / Keep (do NOT undo)

**Masking & compositing baseline:** binary white-on-black mask (zone colors live ONLY in the screenshot); `ctx.clip()` boundary clip; post-process polygon clip `clipRenderToZones` with inward blur(4px)+clamp (the only real containment — but cosmetic, can't fix wrong-SHAPE generation); ~2m/8px mask dilation (a CONSTANT — biases small polygons); building silhouette extrusion in mask; **mask subtraction** (black-out occluders / OSM crossing roads — the only thing that physically prevents generation in a region; shipped, broad-test pending).

**Prompt language that worked:** color-temperature matching + atmospheric-perspective (killed "pasted-on" look); distinct color NAMES in text (≠ rainbow FILL); numbers/widths in TEXT for nadir lane structure (≠ numbers DRAWN on image); ~200 chars/zone simple natural prompts.

**References / multi-view (the #1 accuracy lever):** archetype reference images (512px/70% JPEG, cap ~6 — beats text, also fixed 502s); multi-view 90°+"60°" (really ~45°) aerial refs for verified archetypes; orthographic ground-truth nadir refs (Z-axis fix); SV Static photos as MATERIAL refs with Google tiles as geometry base (shipped PR #15/#16 — tiles=geometry authority, SV=material confirmation); forward SV plate per-engine split (GPT keeps, Gemini filters); **diagram-as-input conditioning** (buildings-free technical diagram as an inlineData part — 2026-06-17 WIN, in-app validated; still soft but the best anti-phantom-building lever to date).

**Infra / model:** temp 1.0 for Gemini 3 image (render.py:501); thinkingBudget=0; 2K output; render timeout 5min; seed forwarding; GPT=best accuracy / Gemini=2nd, 6× faster + only one that stylizes (route artistic→Gemini, photoreal→GPT opt-in); night/watercolor styles ONLY for labelled concept/mood (they HIDE geometric error); deterministic to-scale street-section renderer (PIL+SVG from metre widths — geometry from numbers can't drift); bare-earth elevation draping (PR #12).

---

## 3. Parked vs Abandoned (NOT failures)

**PARKED** (built/feasible, blocked on an external dep — retain, resurrect):
- **Route-by-style per-model prompt formatters** — BUILT, 43/43 tests, commit **32ae0b0** on `backup-2026-05-06-pre-clean-pull`. Resurrect, don't rewrite.
- **Render Video pipeline (Gemini Omni)** — BUILT. The earlier
  `gemini-omni-flash-preview` 404 was superseded by Google's June 30, 2026 public
  preview release. Restore behind a provider adapter with Veo 3.1 as fallback;
  do not rewrite the existing route/video service.
- **3D Gaussian splat basemap** — feasibility done; no global query-by-coordinate splat repo; per-site drone→Cesium ion only.
- **SV-photo-as-base photomontage** — works for clean corners; failed on oblique residential (GPT reframes→ghosting). Parked.
- **Inter-zone adjacency module** (forecourt building-bleed) — BUILT, 24 tests, UNCOMMITTED; A/B pending.
- **Meshy image-to-3D** — genuine massing; needs isolated input + polycount cap; not measurement-faithful.

**ABANDONED** (dropped for cost/scope, NOT quality failure): 30° low-oblique full rollout (cost; pilot pending); Vertex Imagen 3 era (dropped for quality — but it's the ONLY endpoint with TRUE hard-mask inpaint, = the retired `useAIRender.ts` codex/Mapbox path); fal.ai/FLUX engine era; model selector; Preserve-Existing zone; north-arrow picker; speculative archetypes (restorable); Maps Grounding APIs (wrong layer / US-only); Codex-as-base branch plan (pivoted to stable-as-base + port codex UX).

---

## 4. Cross-Check of Proposed Next Steps A–E (MOST IMPORTANT)

### A. Plumb the diagram flag → buildings-free diagram as AUTHORITATIVE geometry, suppressing the "apply exact materials" label, on BOTH paths.
**Verdict: SAFE-NEW — generalizes a 2026-06-17 WIN that is already in-app validated.** `project_diagram_conditioning_archetypes_2026_06_17` records ✅ TRIAL A WORKED ("pretty great job with GPT") on the live globe path; a buildings-free input gives the model nothing to scene-complete into phantom buildings. **Traps:** (1) still a SOFT ref — pilot each NEW projection (plan→oblique-aerial, section→eye-level are LOW-confidence); don't market as "locked." (2) Projection MUST match camera + strip all callout text/numbers, or you hit the #36 vector-section clip-art-leak. Diagram-as-INPUT works; vector-section-as-soft-REF-for-photo leaks — don't blur the two. (3) Constraint list ≤5-8; geometry-critical → GPT. (4) Don't chase fabricated lock mechanisms (#49/#50). Plumb the flag so the right label attaches per image-role (the backend also wrongly labels every primary image "a 3D clay massing model" — fix while there).

### B. Composite the REAL roadway back over the render (in `clipRenderToZones` before `applyStyleGrade`).
**Verdict: SAFE-NEW (strongly supported as defense-in-depth).** The deterministic composite-back is repeatedly validated (SV-montage feathered composite = pixel-perfect region "regardless of how the model behaves"); it's the recommended hedge against the unanswered "is GPT's mask hard?" question. **Traps:** (1) GPT reframes/resizes output → composite misalignment ghosting (why SV-photo-as-base was parked on oblique). Verify GPT output dims/crop before compositing, or apply on Gemini path / after reproject. (2) Cosmetic — fixes *where the roadway is*, not wrong-shape generation. (3) Only the single-shot path is live.

### C. Resolve the temp override (0.0 vs guidance_scale=15→0.75) via 0.0/0.75/1.0 bake-off; rewrite negatives affirmatively.
**Verdict: NUANCED — bake-off is SAFE-TO-A/B (settles a real open conflict); affirmative rewrite is SAFE-TO-A/B with a documented counter-claim to neutralize.** Nobody has measured what temp actually reaches Gemini end-to-end, so a controlled A/B is exactly the right methodology. **Traps:** judge over ≥3 renders (drift = LOD/fade racing capture, NOT temp, NOT the seed #51); confirm via `[GlobeAIRender]` log you're on the LIVE globe hook, not the dead Mapbox hook. **Negatives:** an April note claimed "Prohibitions = 94% compliance"; newer white-bear + vendor guidance override it, but it's not yet flipped in code — treat affirmative as a *lean to validate against the 94% counter-claim*, keep meta-artifact negatives (watermark/text), don't stack 15-20.

### D. Self-hosted VLM verification gate (phantom buildings / wrong-way cars / lane-count / leftover fills).
**Verdict: SAFE-NEW — genuinely untested, well-motivated.** Every failure class it targets is a documented real defect. **Traps:** (1) the detector is itself a soft VLM — validate precision/recall against the known-defect corpus before trusting it to gate publishing. (2) Defect base rates are UNMEASURED (text-leak severity was never directly measured) — instrument rates first. (3) It should FLAG and ROUTE (to the other engine), not blindly re-roll persistent-bias defects (#40/#41).

### E. Move toward HARD structural conditioning — self-hosted SD3.5 / FLUX.1[schnell] ControlNet, 3D z-buffer maps, ColPali RAG.
**Verdict: OVERLAPS-A-PAST-FAILURE (the biggest landmine) — proceed only with the depth-map SOURCE fixed FIRST.** FLUX lost twice (#30 whole renderer; #31 depth-ControlNet 3rd engine — WORST incl. massing, REVERTED). The offline pilot used an idealized SYNTHETIC depth map; in-app `buildZoneDepthMap` produced a flat-plate silhouette. **The lesson is NOT "FLUX is bad" — it's "depth-MAP GENERATION is the hard part; the diffuser comes after."** Swapping FLUX→SD3.5/Qwen does NOT fix this. And the clay z-buffer lives in `useStreetViewRender`; the globe pipeline has NO clay model — a globe control map needs porting clay in OR deriving depth from tiles (the unsolved part). **If pursued:** fix the 3D-volume depth source first (A/B vs the flat-plate failure); never standalone — only two-stage structure→finish; `jasperai` depth is NON-COMMERCIAL (use SD3.5/Qwen/Shakker). ColPali RAG is genuinely NEW + orthogonal (grounds text/specs, not pixels). **Diagram-conditioning (A) is the near-term, already-validated substitute for "hard geometry on the globe."**

**Highest-ROI untried alternative the record keeps flagging:** **AUTOMATE-THE-ZOOM.** Manual zoom to ~50-60% canvas is the most reliable containment method ever found (beat all 3 code automations in 04-17). Auto-frame failed ONLY because the globe viewport shim lacks `getZoom`/`fitBounds`/`easeTo` — an implementation gap, not a conceptual failure. Extend the shim, then auto-frame each zone. Cheaper/lower-risk than self-hosted ControlNet.

---

## 5. Patterns & Meta-Lessons

1. **The soft-conditioner ceiling (master pattern).** Spatial accuracy comes ONLY from camera framing/zoom, reference images, post-process mask-subtraction + composite-back, a buildings-free diagram-as-input, or a self-hosted structure model fed a *real* 3D source — never from prompt wording.
2. **Visual-noise-bleed cluster.** Anything drawn on the screenshot that isn't the muted zone fill renders literally: numbered circles, rainbow fills, wireframe borders, zone-overlay-as-2nd-image, white outlines.
3. **Verbosity hurts.** Longer prompts repeatedly made renders worse. ~200 chars/zone; simple > structured-verbose.
4. **Scale-on-large-mask.** Gemini enlarges items to fill big polygons; text can't override. Lever = reference image or hard conditioning. (Globe also misreports polygon area up to 21× — prints nominal `suggestedAreaSqm`, not the drawn polygon.)
5. **Verify LLM claims about the model's own API.** Hard-mask inpaint, thinking-locks-pixels, 0-1000 grid, `input_fidelity` knob, "contract vs suggestion" — all hallucinated mechanisms. The fidelity lever is the reference image.
6. **Two-stage / two-FLUX confusion is a trap.** Two FLUX rejections (whole-renderer; depth-layer) and two opposite diagram results (clean diagram-as-input WORKS; vector-section-as-photo-ref LEAKS) — don't collapse these.
7. **Methodology the record preserves:** isolate ONE variable per test; pilot→confirm→scale before any $50+ run; judge over ≥3 renders (non-determinism = LOD/fade racing capture, NOT the seed — it's forwarded); show images inline; diff vs last-known-good before theorizing; confirm which hook is live (`[GlobeAIRender]` log); refs grounded in real buildings; fix root cause before mitigations.
8. **Offline-GO ≠ in-app-GO.** The FLUX depth pilot's synthetic depth oversold readiness; in-app flat-plate reversed it. Validate the *real* input artifact. (The diagram win was confirmed in-app — why A is trustworthy where E is not.)

---

## 6. Gaps / Unknowns (untested, not failed)

- **Is GPT Image 2's `/edit` mask a HARD pixel boundary?** Never tested; conflicting forum reports. A 5-min pixel-diff test would settle it (makes B's "defense-in-depth regardless" correct).
- **GPT Image 2 fidelity is locked HIGH, not a settable knob** — the prod lever to test is the reference image.
- **AUTOMATE-THE-ZOOM** — highest-ROI flagged win; shim extension never built.
- **Pre-tiled reference grid for park scaling** — cheapest untried scale fix.
- **Single labeled-reference grid** (≤6 grounded insets) for multi-zone placement — sidesteps the 16-refs failure; never tried.
- **Mask subtraction / OSM crossing-road carving** — BUILT, compile-clean, NOT yet visually piloted = inconclusive.
- **Per-zone vs single-shot accuracy** — memories conflict; treat per-zone as unproven for accuracy.
- **Diagram-conditioning beyond top-down** — top-down 90° validated; oblique/eye-level projections LOW-confidence; pilot each.
- **ColPali RAG over standard PDFs** — no prior attempt; new; likely text-layer (won't fix massing).
- **Three priority docs (REFERENCE_IMAGE_ANGLE_AUDIT, RENDER_STYLES_DEEP_DIVE, PRE_LAUNCH_DEEP_DIVE) are NOT in the working tree** — live on other branches; survive only as distilled memory.
- **Git undercounts recent failures** — the June FLUX-depth revert and GPT-Image-2 street-view 502s left NO surviving commit. Don't infer "never tried" from git silence.

**Net:** A & B are SAFE-NEW (A already in-app validated; B deterministic defense-in-depth). C & D are SAFE-TO-A/B experiments that settle open conflicts — use the isolate-and-measure methodology. **E is the landmine** — it overlaps the twice-reverted FLUX work; pursue only after fixing the 3D depth-map *source*, never standalone, and weigh it against the cheaper AUTOMATE-THE-ZOOM win first. Across all five: do NOT chase the fabricated `input_fidelity` knob or "contract vs suggestion" lock — the fidelity lever is the reference image.

---

## 7. Settled 2026-07-12 (execution run — see docs/EXECUTION_REPORT_2026_07_12.md)

**Closed questions (evidence-verified, stop re-litigating):**
- **No frontier hard conditioning is coming.** Google discontinued Imagen Controlled Customization (~June 30, 2026, its only hard structural conditioner); BFL dropped FLUX.1 Depth/Canny from its API; FLUX.2 shipped without structural conditioning; Gemini 3.x image docs list zero mask/depth/segmentation params. Reopen-signals: a Gemini changelog adding mask/depth params; Maps Imagery Grounding reaching Canada with conditioning.
- **guidance_scale was a phantom** — undocumented Imagen-era SDK field; our mapping silently set temp 0.75 on every render. DELETED. No temperature is sent on Gemini image calls at all now. Every pre-2026-07-12 A/B was confounded by this + unset aspect_ratio.
- **The js-genai #1461 "preview always returns 1K" bug does NOT affect our REST generateContent path** — 2×2 pilot returned 2K on both ids. Migrated to GA `gemini-3.1-flash-image` anyway (deprecation is real).
- **Both vendors are seedless** (official docs); ref-anchoring + generate-N-and-pick is the substitute. There was never a seed/temp UI in StreetViewPanel (stale note).
- **AUTOMATE-THE-ZOOM: BUILT** (`cc_auto_frame`, 4f19fb4) — in-app verified framing 99 zones at ~55% in 856 ms. Paid-quality A/B pending user.
- **Pre-tiled reference grid: TESTED** — mechanism CONFIRMED (tiled ref → more/smaller courts; the ref image sets rendered scale), but naive 3×3 tiling costs photorealism + echoes the grid literally. Next form: tiled ref ALONGSIDE the photoreal card, not instead of it. Do NOT retry naive tiling alone.
- **Clean composite base: BUILT** (`cc_clean_composite`, 4f19fb4) — July-7 work already used the raw capture as clip base (labels never leak); the remaining polluter was in-scene grey zone fills at the feather ring; now captured overlay-free via event round-trip (in-app verified).
- **Vertex Canada: CLOSED — no image model in northamerica-northeast1** (predict-probe: gemini-2.5-flash-image exists in us-central1, 404 in Montreal; Imagen 3/4 404 everywhere post-shutdown). No Canada-resident image gen on Google/Azure/Bedrock as of 2026-07-12. Lead with no-PII, not residency.
- **momepy 1.0 works on our plans** incl. curvilinear locked networks and discriminates scenarios (COINS strokes: eco 138/89 m, env 201/82 m, beaux 97/114 m). Not yet in requirements (geopandas layer ~200 MB — user decision).
- **Meshy spend guard now exists** (`meshy_min_balance_floor`, default 100). There was previously none.
