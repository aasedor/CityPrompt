# Making Aerial Renders As Good As Street View

_Research + trial plan — 2026-04-18_
_Branch context: `feature/merge-codex-ux-onto-stable`_

## TL;DR

Street-view renders consistently outperform aerial renders because the street-view pipeline does **seven specific things differently**, not because it has access to better reference material. Both pipelines send the same archetype card images and metadata to Gemini. The gap is in how the pipeline **frames the task** for the model.

The highest-leverage experiments, in order of bang-for-effort:

| # | Experiment | Time | Expected impact |
|---|---|---|---|
| **0** | **🔥 Aerial reference images instead of street-view** (port multi-view logic from codex; 4 archetypes already have data ready) | ~1.5 hrs | **VERY HIGH — likely the single biggest lever** |
| 1 | **Colored-massing depth reference image** (port from street view) | ~3 hrs | HIGH — structural |
| 2 | **Entourage specification** in the prompt | ~30 min | MEDIUM–HIGH |
| 3 | **Explicit camera lens / aperture / focal-length** in photomontage style | ~1 hr | MEDIUM–HIGH |
| 4 | **Per-depth-plane optical instructions** (foreground / mid / background) | ~1 hr | MEDIUM |
| 5 | **Lower default pitch to ~30° oblique** | ~15 min | MEDIUM |
| 6 | **Add PBR material language** (roughness, specularity, refraction) | ~30 min | LOW–MEDIUM |
| 7 | **Per-zone low-oblique render → composite back** | days | HIGH but invasive |

**Start with #0.** It's likely the single biggest reason aerial underperforms: we currently send Gemini street-view reference photos when asking for an aerial render. The model has to mentally rotate the building 60–90° before it even starts rendering. That's cognitive tax we're paying for nothing — aerial reference data already exists on disk for 4 archetypes (April 15 pilot).

After #0 lands and you can see the magnitude of the effect, proceed to #2, #3, #5 (cheap high-impact) before tackling #1 (the structural depth-map port).

---

## Why aerial underperforms street view

### 1. The task is harder for the model, not our refs

Both pipelines feed Gemini:
- The same archetype card images (compressed to 512px JPEG @ 0.7 quality, max 6)
- The same archetype metadata (facade description, materials, aerial appearance, etc.)
- The same Gemini 3 Flash Image backend

So **it's not what we feed the model — it's the task framing itself**. Specifically:

### 2. Viewing-angle familiarity

- **Street view** is the dominant architectural-photography genre in Gemini's general training data. Billions of street-level images, eye-level buildings, and photojournalistic compositions.
- **Aerial** is a niche within drone / real-estate imagery. Orders of magnitude less training data. The model's priors are thinner here.

This isn't something we can fix with better prompts, but it is something we can **work around** by making aerial inputs look more like photographic genres the model IS strong at (oblique drone, not top-down map).

### 3. Spatial arrangement in the frame

- **Street view** naturally segregates zones into **depth planes** — foreground park at the bottom of the frame, background building at the top. No two zones compete for the same pixel neighborhood.
- **Aerial** puts all zones **side-by-side on one ground plane**. Building next to park next to road, all sharing similar visual register (rooftops from above look superficially alike). The only strong discriminator is polygon color, and when colors are close the model confuses zones.

### 4. Boundary task difficulty

- **Street view** boundary is a 1D line — where brick meets sidewalk. Gemini has trillions of examples.
- **Aerial** boundary is a 2D polygon perimeter AND a 3D extrusion silhouette. Many more places to get wrong. Shadow casts, roof overhangs, awnings all move the visible edge away from the polygon edge.

### 5. Compositional priors

- **Street view** has built-in conventions the model already knows: subject centered, sky above, sidewalk below, trees framing. Gemini doesn't have to synthesize layout.
- **Aerial** requires the model to reason about multiple zones simultaneously at varying scales with no strong photographic prior telling it "this is how these things look together from above."

### 6. What street view does that aerial doesn't (pipeline level)

From a file-by-file comparison of `useStreetViewRender.ts` vs `useGlobeAIRender.ts` on this branch, the street-view pipeline has **six specific structural advantages**:

| Axis | Street view | Aerial | Notes |
|---|---|---|---|
| **Camera spec** | Fixed 70° FOV, 50mm f/8, 1.7m height — **prescriptive** | Dynamic pitch, no lens spec — **descriptive** | Prescriptive lens anchors Gemini's perspective model |
| **Depth reference** | Separate colored-massing image sent as "Image 1" (1024×576, 16:9, sky + ground + colored zone blocks) | None — only a binary white/black mask | The depth map is a *spatial trust anchor* |
| **Prompt structure** | 3-plane depth frustum with per-plane optical instructions and per-zone frame percentages | Single-composition SCHEMA | Depth-planes geometrically constrain zone placement |
| **Entourage** | Explicit 5–10 human figures with anatomical + scale constraints | None | People give scale reference and life |
| **Photomontage style language** | Canon EOS R5, 35mm, f/8, ISO 200, 1.6m tripod height, dust + stains + fingerprint patina | "DJI Mavic 3, 24mm f/5.6, 60m altitude" — less specific | Specificity anchors lens physics |
| **Occlusion culling** | 80% threshold, angular bearing-based | 95% threshold, pixel-rasterization-based | Aggressive culling = sparser, cleaner scene |

### 7. What the broader AI-rendering field corroborates

Web research on architectural AI rendering converges on similar conclusions:

- **Depth maps as ControlNet conditioning** are a proven technique for anchoring spatial structure in diffusion-model architectural rendering. Gemini isn't a ControlNet pipeline but benefits from the same principle when depth is provided as a secondary reference image.
- **PBR (Physically Based Rendering) language** — specifying refraction, roughness, subsurface scattering — improves material photorealism.
- **Cinematic camera language** — focal length, aperture, ISO, lens model — gives Gemini a physical camera to simulate rather than a vague viewing angle.
- **Gemini's own docs** note that prompt quality is orthogonal to resolution, and that compositional terms (wide-angle, low-angle, 85mm portrait lens, Dutch angle) give precise control.
- **Architectural visualization practitioners** explicitly treat aerial and street-level as separate disciplines with different goals — aerial for *scale understanding*, street-level for *emotional connection*. Aerial's goal is partially inherent, not purely a technical shortcoming.

---

## Trial plan

Each experiment is scoped to be tested in isolation. Run them one at a time so you can tell which contributed what.

### Experiment 0 — Aerial reference images instead of street-view (🔥 DO FIRST)

**The critical insight:** Every reference image we currently send to Gemini is a **street-level photograph** of the archetype. When Gemini is asked for an aerial/oblique render, it has to mentally rotate the reference 60–90° AND rebuild the 3D form. That's a task the model is measurably bad at — it's why codex's buildings "looked prettier but were in the wrong spot" (material style transferred; spatial mapping didn't).

Street view renders work because the reference image IS at street-level — direct visual match between ref and output. Aerial has a built-in viewpoint mismatch we're not addressing.

**Hypothesis:** Sending aerial-angle reference images (90°/60°/30° drone photos) for aerial renders will close a significant fraction of the quality gap, because the model no longer has to extrapolate between reference and output perspectives.

**Pre-existing work we can leverage (April 15 pilot, per memory `project_multi_view_references.md`):**
- Aerial reference images already generated for 4 archetypes:
  - `civic_monumental_institution` variant 0 (maps to "Grand Magasin"-style)
  - `tennis-court-cluster` variant 3
  - `beach-volleyball-courts` variant 3
  - `pedestrian-promenade` variant 0
- Each has `variant_N_angle_{30,45,60,75,90}.jpg` files on disk
- Pilot validated "3 angles (90°, 60°, 30°) is the sweet spot"
- Pilot found: street-view rear/side views are USELESS; only aerial views help
- Image cap was raised from 6 → 48 in codex to support this

**What the merged branch is doing wrong right now** (`useGlobeAIRender.ts:366-410`):
- `collectArchetypeImagesForZones()` fetches one image per zone via `getZoneArchetypeCard()`, which returns the `thumbnailUrl` — always street-view.
- Cap at 6 images total.
- No awareness of angle variants.
- No MULTI_VIEW_IMAGES map.

**Implementation (minimal — just enough to test the hypothesis):**

1. **Extend the archetype loader to check for aerial variants.** In `getZoneArchetypeCard()`, after resolving `thumbnailUrl`, also check for sibling files at `variant_{N}_angle_90.jpg`, `_angle_60.jpg`, `_angle_30.jpg`. Return an array of URLs (angles that exist), not a single URL.

2. **Update `collectArchetypeImagesForZones()` to return multiple images per zone.** Keep the compression + JPEG 512px pipeline for each. Flatten the per-zone arrays into one flat array sent to Gemini. Tag each image with its angle in the label (`"Vertical Farm — aerial 90°"`, `"Vertical Farm — aerial 60°"`, `"Vertical Farm — aerial 30°"`).

3. **Raise the image cap from 6 → 48.** Per the codex memory, Gemini accepts 3600 images / 20MB; 48 is well under. With 3 angles × up to 16 zones, we have headroom.

4. **Update the prompt** so Gemini knows what to do with multiple angles:
   ```
   REFERENCE IMAGES: Each archetype is accompanied by up to 3 aerial drone
   reference photographs at different downward angles (90° = top-down, 60° =
   oblique aerial, 30° = low oblique). Use these to build your understanding
   of the archetype's 3D form — roofline, massing, setback, material patterns
   from above. These match the viewing angle of the scene you are generating.
   ```

5. **Gate on render mode.** Street-view renders should STILL use the street-level thumbnail (the existing `useStreetViewRender.ts` path). Only aerial renders should prefer aerial variants.

**Test it with the 4 pilot archetypes:**
- Set up a small site with a Grand Magasin zone (uses `civic_monumental_institution` archetype) and a park with tennis courts.
- Render before/after with the multi-view change.
- Compare polygon accuracy, spatial fidelity, material correctness.

**Time:** ~1.5 hours for the port. The data generation for the remaining 93 archetypes is a separate async project (script exists at `scripts/generate_angle_images_batch.py`).

**Success criteria:** On the 4 pilot archetypes, aerial renders should show dramatically better polygon fit and proportion accuracy. If it doesn't move the needle noticeably, the multi-view theory is wrong and we skip generating the remaining 93 (saving a lot of work). If it does — generate the rest.

**Risk:** Low. The worst case is that we add 3x reference payload for no quality gain, and we revert. The upside case is this was the single missing puzzle piece.

**Rollout to remaining 93 archetypes (after validation):**
- The generation script (`scripts/generate_angle_images_batch.py`) uses Gemini itself to produce the drone photos. Per the memory: the prompt must say "drone photograph, camera 100m above ground, NOT street level" to avoid Gemini defaulting to street-level.
- Batch-generate at 3 angles (90°, 60°, 30°) per archetype variant.
- Estimated time: ~1 Gemini call per image, 3 images × 97 archetypes × 1-2 variants each = ~300-600 calls. Manageable as a one-time batch job.

---

### Experiment 1 — Colored-massing depth reference image

**Hypothesis:** Street view's secret sauce is the separate depth-map reference image it sends as "Image 1." Adding an equivalent to aerial (generated from the current camera angle, showing zones as colored 3D-ish boxes on a simplified sky/ground gradient) will anchor Gemini's spatial understanding without needing photorealistic tile context.

**Implementation:**
- Port the depth-map generator from `useStreetViewRender.ts:1258-1299` (see `buildDepthMap()` logic).
- Adapt it for oblique-aerial view: project each zone's footprint + extruded roof (for buildings) or flat fill (for ground zones) using the same `projectToPixels()` function the mask uses.
- Color-code by zone type (same palette as the mask) or by archetype shade.
- Generate at 1024×768 (match canvas aspect), JPEG @ 0.85.
- Send as an additional image in the backend call, with a prompt reference: `"Image 2 is a simplified 3D massing reference showing zone geometry and spatial depth. Use it to verify volumetric proportions and relative positions before rendering."`

**Time:** ~3 hours (most complex; worth it)
**Success criteria:** Multi-zone sites with adjacent zones should show less archetype-swapping and better proportion fidelity.
**Risk:** If the massing reference is poorly rendered or misaligned with the actual screenshot, it could confuse the model. Validate visually (log the generated image) before committing.

### Experiment 2 — Entourage specification in the prompt

**Hypothesis:** Aerial renders feel empty/sterile because there are no people, cars, or activity. Street view's prompt explicitly requests 5-10 human figures with anatomical constraints. Adding an entourage clause to aerial will make renders feel lived-in at minimal cost.

**Implementation:**
- After `ZONES:` in `buildPrompt()` in `useGlobeAIRender.ts`, add a new section:
  ```
  ENTOURAGE: Populate the scene with 6-12 human figures appropriate to each zone type —
  pedestrians on sidewalks and paths, people seated in parks and plazas, small groups
  near building entrances. Figures should be anatomically correct, diverse in age and
  clothing, at realistic scale (~1.7m tall). Place them at mid-distance (no figures
  filling the foreground). Include a few parked cars along streets and cyclists on
  multi-use trails where appropriate. Avoid clustering; scatter naturally.
  ```
- Gate on zone types: if there are parks/plazas include park-goers; if there are streets include cyclists; etc.

**Time:** ~30 minutes
**Success criteria:** Renders feature people and cars visible at appropriate scale.
**Risk:** Very low. Entourage is a soft constraint — if Gemini can't fit figures they're dropped, not forced.

### Experiment 3 — Explicit camera lens, aperture, focal-length

**Hypothesis:** Street view's photomontage prompt is hyper-specific about the camera model (Canon EOS R5, 35mm, f/8, ISO 200). Aerial says "DJI Mavic 3" without ISO or aperture details. More specificity anchors Gemini's lens model, affecting perspective distortion and depth of field.

**Implementation:**
- Compute camera altitude and subject distance from THREE camera state.
- Derive equivalent focal length from camera FOV.
- Inject into photomontage/photorealistic style prompts:
  ```
  CAMERA: DJI Air 3S at {altitude}m altitude, {focal_length}mm equivalent lens,
  f/5.6 at ISO 100. Subject distance {distance}m. Natural lens vignetting, subtle
  chromatic aberration at frame edges, gentle falloff at extreme corners.
  Depth of field: foreground (<30m) tack-sharp; midground (30-80m) sharp;
  background (>80m) gently soft with aerial perspective.
  ```
- For photorealistic style (which currently says "cinematic lighting"): add matching specificity about lens, ISO, aperture.

**Time:** ~1 hour
**Success criteria:** Renders show natural lens artifacts (vignetting, corner softness, chromatic aberration) and consistent depth of field across runs.
**Risk:** If the derived focal length is wrong (e.g., camera FOV doesn't match real drone optics), Gemini may apply incorrect perspective distortion. Validate against known-good reference drone photos.

### Experiment 4 — Per-depth-plane optical instructions

**Hypothesis:** Street view breaks zones into foreground/midground/background and gives each a distinct optical instruction (sharpness, haze, saturation). Aerial treats the whole frame uniformly, so distant zones are rendered too crisply, breaking atmospheric perspective.

**Implementation:**
- During zone prep in `buildPrompt()`, compute each zone's distance from the camera (already done for occlusion culling — reuse).
- Bucket into foreground (<30m), midground (30-80m), background (>80m).
- In the ZONES list, prefix each zone with its depth bucket: `[color] @ UPPER-LEFT | FOREGROUND | ...`
- Add new clauses to the prompt:
  ```
  DEPTH OPTICS:
  - FOREGROUND zones (<30m from camera): maximum sharpness, full saturation,
    every material texture rendered with fine detail. Strong shadow contrast.
  - MIDGROUND zones (30-80m): sharp but slightly softer than foreground,
    slight atmospheric haze, full color.
  - BACKGROUND zones (>80m): enforce aerial perspective — desaturate by 15%,
    shift cool/blue, reduce facade detail, distant trees as soft silhouettes.
  ```

**Time:** ~1 hour
**Success criteria:** Distant zones visibly hazier and less detailed than near zones, creating natural depth.
**Risk:** Over-application can make backgrounds look unrealistically washed out. Language needs tuning ("subtle aerial perspective" may beat "desaturate 15%").

### Experiment 5 — Lower default pitch to ~30° oblique

**Hypothesis:** Near-top-down (60°+ from horizontal) is the angle Gemini is least trained on. An oblique 30° view is closer to architectural-photography genres the model knows well. Rather than fighting Gemini at the hard angle, just present the site from an angle Gemini is good at.

**Implementation:**
- Change the default camera pose in `GlobeSitePlannerMap.tsx` so it initializes at ~30° pitch instead of ~60°.
- Alternatively: add a "Rendering view" button that temporarily flies the camera to 30° before capture, renders, then restores.
- Users can still tilt higher for planning; lower angle is just the recommended render position.

**Time:** ~15 minutes (for the default change); ~1 hour (for the fly-to-render-then-restore flow)
**Success criteria:** Renders at the new default should show visibly better facade detail and material rendering.
**Risk:** Users may prefer top-down for site planning. Don't force — make it the **default for rendering** not the **default for planning**.

### Experiment 6 — PBR material language in style prompts

**Hypothesis:** Specifying material behavior in PBR terms (roughness, specularity, refraction, subsurface scattering) improves material photorealism. Current style prompts say "weathered brick" but don't specify how it should behave under light.

**Implementation:**
- Enhance the photorealistic style prompt:
  ```
  MATERIALS (PBR): Glass = high specularity (0.9), low roughness, sky reflections
  visible. Concrete = mid roughness (0.6), subtle specular highlights on wet areas.
  Brick/masonry = high roughness (0.85), course-line shadow relief, no specular.
  Metal cladding = low roughness (0.2), sharp specular highlights picking up warm
  sun. Wood = mid-high roughness (0.7), subtle anisotropic highlight along grain.
  ```
- Keep this conditional on the photorealistic / photomontage / atmospheric styles only.

**Time:** ~30 minutes
**Success criteria:** Materials visibly more tactile; glass shows real reflections; brick shows depth.
**Risk:** PBR language may be too technical for Gemini to parse usefully. If it doesn't move the needle, simplify to descriptive: "glass is mirror-like and reflects the sky; brick is rough and textured; metal is shiny and catches sunlight."

### Experiment 7 — Per-zone low-oblique render then composite

**Hypothesis:** Street view is easy because it's one-zone-per-frame. If we render each zone individually at a low-oblique angle (where Gemini is strong), then composite them back into a top-down site plan, we sidestep the multi-zone-in-one-aerial problem entirely.

**Implementation:** Much bigger. Requires:
- A pipeline that iterates zones, positions the camera to a zone-specific oblique angle, captures, renders, then pastes the render into the top-down composite at the zone's polygon location.
- Logic for scaling the oblique render to fit the polygon's top-down footprint.
- Handling occlusion between zones during composite.
- Codex already had a 4-face bearing render (`renderFull(singleView=false)`) that conceptually aligns — look at that for prior art.

**Time:** Multiple days — architectural change
**Success criteria:** Complex multi-zone sites render with per-zone quality matching street view.
**Risk:** Composite seams between zones; scale inconsistencies; significant engineering effort.

**Recommendation:** Don't attempt this experiment until 1-6 have been trialed. If 1-6 close most of the quality gap, this may not be worth the cost.

---

## Recommended trial order

1. **🔥 #0 Aerial reference images** — 1.5 hrs. **ABSOLUTE FIRST PRIORITY.** This is likely the single biggest lever; everything below is incremental next to this.
2. **#5 Lower default pitch** — 15 min (may stack with #0 for compounding effect)
3. **#2 Entourage** — 30 min (makes every render feel more alive)
4. **#3 Explicit camera lens** — 1 hr (targeted material quality win)
5. **#6 PBR materials** — 30 min (cheap experiment)
6. **#4 Depth-plane optics** — 1 hr (requires zone distance computation)
7. **#1 Massing reference image** — 3 hrs (structural; do only if 0-6 aren't enough)
8. **#7 Per-zone composite** — only if 0-7 leave a meaningful gap

Total time for #0-#6 bundled: **~7.5 hours**, ~5-level prompt test cycles.

**Critical path:** #0 alone may close so much of the gap that many downstream experiments become unnecessary. Test it first with the 4 pilot archetypes before generating the rest.

## Testing protocol

For each experiment:

1. **Before:** generate a baseline render on your standard Calgary 4-zone site (Vertical Farm + Disc Golf + Grand Magasin + Multi-Use Trail). Take a screenshot.
2. **Apply only that experiment's changes.** Don't bundle.
3. **After:** generate a render on the same site with the same seed if possible. Screenshot.
4. **Compare:** specifically on (a) polygon boundary fidelity, (b) material quality, (c) scene realism/liveliness, (d) archetype correctness.
5. **Keep or revert** based on whether the gain is worth the complexity.

Log which experiments you kept and the prompts/screenshots for each iteration. This becomes training data for the next round.

## Out-of-scope observations

- **Aerial's inherent purpose is different** from street view. Aerial serves scale + layout; street view serves emotional engagement. Closing the quality gap entirely may not be possible — and if closed, aerial still won't replace street view's persuasive power. Consider the UX implication: use aerial for layout validation, street view for client presentation.
- **Model switch** (Imagen 3 on Vertex AI instead of Gemini 3 Flash Image) would provide true hard-mask inpainting — see `docs/RENDER_HOOK_COMPARISON.md` for prior analysis. Trade-off is lower aesthetic quality. Not recommended at this time.
- **Training data augmentation** (fine-tuning a LoRA on user-provided aerial architectural renders) is a longer-term direction; out of scope for this session's experiments.

## Sources

### Codebase (this branch)

- [`useStreetViewRender.ts:325`, `:992-1095`, `:1258-1299`, `:1198-1227`, `:611-698`](frontend/src/components/viewer/useStreetViewRender.ts) — FOV, camera model, depth-plane descriptions, entourage, occlusion culling
- [`useGlobeAIRender.ts:27-48`, `:63-81`, `:244-330`, `:600-762`, `:114-237`](frontend/src/components/viewer/globe/useGlobeAIRender.ts) — aerial style prompts, capture, mask, prompt builder, occlusion culling

### Web

- [Gemini 3.1 Flash Image — Nano Banana 2](https://deepmind.google/models/gemini-image/flash/) — model documentation
- [How to prompt Gemini 2.5 Flash Image Generation for the best results](https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/) — Google's official prompting guide
- [Mastering Advanced Image Creation with Google Gemini and Imagen 3](https://leonnicholls.medium.com/mastering-advanced-image-creation-with-google-gemini-and-imagen-3-8309b2ec8097) — cinematic camera language for Gemini
- [Gemini Image High Resolution: HD Prompts, 4K Settings & Quality Guide (2026)](https://blog.laozhang.ai/en/posts/gemini-image-high-resolution-hd-prompt) — resolution vs prompt quality separation
- [AI Prompts for Architectural Rendering — BibLus](https://biblus.accasoftware.com/en/ai-prompts-for-architectural-rendering-effective-communication-guide/) — PBR language, morphology terms, density cues
- [Photorealistic Architectural Rendering Best Practices — MyArchitectAI](https://www.myarchitectai.com/blog/photorealistic-rendering) — general photorealism techniques
- [Eye-Level vs Aerial View Rendering Comparison Guide — JS Engineering](https://www.jsengineering.org/eye-level-vs-aerial-view-rendering-which-perspective-works-best/) — why the two serve different purposes
- [Streetscape Rendering Vs Aerial Rendering — McLine Studios](https://medium.com/@mclinestudios/streetscape-rendering-vs-aerial-rendering-a641b5d5c21a) — goal differences
- [ControlNet Depth — Hugging Face `lllyasviel/sd-controlnet-depth`](https://huggingface.co/lllyasviel/sd-controlnet-depth) — depth-map conditioning for spatial accuracy
- [Multi-View Depth Consistent Image Generation Using Generative AI Models (CAADRIA 2025)](https://papers.cumincad.org/data/works/att/caadria2025_567.pdf) — ControlNet multi-view architectural research
- [ReconFusion: 3D Reconstruction with Diffusion Priors](https://reconfusion.github.io/) — NeRF + diffusion for sparse-view reconstruction (future direction)
