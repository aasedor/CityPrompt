# Technical Diagrams as Conditioning Inputs — Research Report (2026-06-17)

**Question:** What characteristics of a technical road/street diagram make it work best as an INPUT/REFERENCE IMAGE for GPT Image 2 (primary) and Gemini 3 image (secondary), to produce a photorealistic, geometry-faithful, **building-free** render of a roadway/intersection treatment — and how should such diagrams be produced?

**Method:** deep-research harness — 5 search angles, 20 sources fetched, 90 claims extracted, 25 adversarially verified (3-vote, 2/3 refute to kill) → **15 confirmed, 10 killed**.

---

## TL;DR

1. **There is no hard structural conditioner.** Neither GPT Image 2 nor Gemini 3 exposes ControlNet-style canny/depth/scribble/segmentation. Both treat your diagram as a **soft** reference. This is the *structural reason* geometry drifts (protected intersection → generic roundabout). *(high confidence)*
2. **GPT Image 2 always runs at HIGH input fidelity** — the `input_fidelity` toggle is **removed and locked to high**. It biases toward preserving the source → it's the better engine when geometry must be reproduced exactly. Confirms the internal "GPT = best accuracy" finding. **Route geometry-critical diagram renders to GPT Image 2.** *(high)*
3. **Lock geometry in the PROMPT, not the image.** Explicitly enumerate the structural elements to keep (layout, proportions, perspective, specific feature placements) and the exclusions ("no buildings"). Repeat the preserve-list each iteration. *(high)*
4. **Keep the constraint list CONCISE (~5–8 items).** Beyond that the model starts *dropping* constraints — piling on 20 negatives backfires. *(high)*
5. **Strip embedded text** — callout numbers (1–15), legend keys, dimension labels. Image models don't encode spelling and *guess* at characters, so text in the input can surface as garbled artifacts. *(high; severity on current models untested)*
6. **Flatten to a Streetmix-style aesthetic** — simple silhouettes, one flat solid color per element, no gradients/feathered shadows, omit any detail not needed to identify the element. *(medium — Streetmix documents the aesthetic for legibility; the conditioning benefit is inference)*
7. **Match the diagram's projection to the output camera** — plan/nadir → aerial; cross-section/perspective → eye-level. Neither model reliably re-projects a plan into a correct oblique aerial. *(LOW — inferred, not tested; flagged as the #1 experiment to run)*
8. **Gemini feeds the diagram as an `inline_data` part and treats it as soft creative-direction/color conditioning** (sketch→realistic). Only **Gemini 3 Pro Image** has an explicit (still soft) style-reference channel (up to 3 images); Flash has none. *(high)*

---

## Verified findings (with confidence + citations)

| # | Finding | Conf. | Sources |
|---|---------|-------|---------|
| 1 | No hard structural conditioning on either model; ControlNet (edge/depth/scribble/seg/normal/pose) is comparison-only, not a capability of GPT Image 2 / Gemini 3. The soft-reference gap is why geometry drifts. | high | OpenAI API guide; Gemini image-gen docs; ControlNet arXiv:2302.05543 |
| 2 | GPT Image 2 processes **every** input at high fidelity; `input_fidelity` is removed/locked. Favors faithful preservation over improvisation. Reference image (not a knob) is the only conditioning-strength lever. *Caveat: directional bias, not pixel-perfect — background/lighting can still shift.* | high | OpenAI API guide + cookbook (high-input-fidelity); fal.ai |
| 3 | To lock geometry, the prompt must **enumerate** exact elements to keep (layout, horizon/perspective, proportions, feature placements); repeat the preserve-list per edit to cut drift. Complement to — not substitute for — the image. | high | fal.ai drawing-to-photo; OpenAI cookbook prompting guide |
| 4 | Phantom buildings/improvised geometry come from **under-constrained** prompts; bound with explicit exclusions. **Non-monotonic**: >~5–8 requirements → model drops constraints. Keep the list concise. | high | fal.ai; OpenAI cookbook |
| 5 | Embedded text (callouts, legend keys, labels) is a real **leak risk** — models don't precisely encode spelling, they guess at characters → stray/garbled text artifacts. Strip text from conditioning diagrams. *Caveat: mechanism is DALL·E-2/CLIP-BPE specific (arXiv:2204.06125); newer character-aware encoders are better, so severity on GPT Image 2 / Gemini 3 is likely lower and was not directly measured.* | high | DALL·E 2 paper; Google Gemini text-rendering blog; arXiv:2503.03595 |
| 6 | Cleanest aesthetic = **Streetmix convention**: simple silhouette, minimal detail, one solid flat color, no feathered shadows/gradients (sky excepted). Flat color-blocked schematic, not photoreal-shaded. | medium | Streetmix design-principles docs (conditioning linkage = inference) |
| 7 | Gemini-native path: diagram supplied as `inline_data`/`types.Blob` part to `generateContent`; treated as **soft** creative-direction/color reference (sketch→realistic) — *why* geometry drifts. Image + prompt are the only levers. | high | Gemini 3 guide; DeepMind Gemini-image page; Gemini API docs |
| 8 | **Gemini 3 Pro Image** (Nano Banana Pro) has a dedicated style-reference slot (up to 3 images; 14 standard inputs total); **Gemini 3.1 Flash Image** has none. Still soft appearance conditioning — does **not** solve geometry drift. | high | Gemini API docs; Google developer blog |
| 9 | Projection-match at input: nadir/plan → aerial; section/perspective → eye-level. Neither model reliably re-projects plan→oblique-aerial without distortion; pre-render the diagram to approximate the target camera and restate the camera in the prompt. | **low** | Inferred from [4][7] + fal.ai/DeepMind — not directly tested |

---

## Do / Don't rules for SiteForge conditioning diagrams

**DO**
- Strip ALL annotations: callout numbers, legend keys, dimension/leader lines, north arrows, scale bars, embedded labels.
- Flatten to clean flat-color silhouettes (Streetmix style); kill photoreal shading and gradients.
- Keep functional zone color-blocking (lanes/crossings/islands distinct) — *but treat as an open question (may bias palette); A/B it.*
- Match the diagram's projection to the desired render camera.
- Restate the geometry in the prompt: enumerate islands/tracks/crossings/lane count + "preserve layout/proportions/perspective" + "no buildings."
- Route geometry-critical diagram renders to **GPT Image 2**.

**DON'T**
- Don't feed annotated design-guide crops raw (the 1–15 callout plan you showed is the worst case).
- Don't rely on the image alone to hold geometry — both models treat it softly.
- Don't stack 15–20 negatives; concise wins (~5–8 max).
- Don't chase a fidelity/“contract” knob — none exists (see Refuted).

---

## SiteForge action mapping

- **Diagram production** → author clean, flat, annotation-free diagrams. Best candidates: programmatic SVG drawn from the to-scale section data (`_pilot_street_section.py` already renders to-scale sections), or recolored/cleaned Streetmix-style plans. The Calgary Street Manual / NACTO crops need their callouts and legends removed before use.
- **Prompt wiring** (already partly built) → the `technical-diagram` clause in `useGlobeAIRender.ts` / `useStreetViewRender.ts` should lean on the archetype's own `renderPrompt.mapOverlay` enumeration (it already lists "corner refuge islands, wrapped protected bike tracks, set-back crossings…"). Keep the *combined* negative/preserve list ≤~8 — audit `render.py` negatives + the clause + per-archetype negatives so they don't stack past the drop-off.
- **Routing** → make diagram-tagged archetypes prefer GPT Image 2 for the geometry-faithful path; Gemini for stylized/fast.

---

## Open questions — experiments worth running (research could not answer)

1. **Projection re-mapping (highest value):** does a nadir plan reliably yield a correct *oblique* aerial on GPT Image 2 / Gemini 3, or must the diagram be pre-rendered axonometric/oblique to match the globe camera?
2. **Color semantics:** do colored zones (pink/green bike lanes) help interpretation or contaminate the output palette? A/B colored vs. grayscale line-art.
3. **Abstraction optimum:** line-art vs. flat color-block vs. light-shaded vs. axonometric — exact line weight/contrast/resolution for these two models.
4. **Text-leak severity** on current (post-character-aware-encoder) models — is stripping text mandatory or just advisable?
5. **Production toolchain:** programmatic SVG vs. Streetmix renderer vs. cleaned guide crops — which is cleanest with least manual work?

---

## Refuted — do NOT rely on these (voted down)

- `input_fidelity='high'` as a usable lever on GPT Image 2 — **it's locked, not a toggle**.
- A "contract vs. suggestion" layout-binding control in GPT Image 2 — **fabricated mechanic** (0-3).
- Gemini regional/conversational inpainting as a hard selective-edit guarantee (1-2).
- "Models see glyphs as meaningless shapes" framing (refuted) — the real mechanism is *spelling not systematically encoded*, not "no comprehension."
- Streetmix "1px = 1cm" metric scale and "text-converted-to-vectors" export rules (refuted).

---

## Caveats

Model mechanics are current as of **June 2026** (GPT Image 2 shipped Apr 2026; Gemini 3 Pro Image is live flagship; Imagen line deprecates 2026-06-24) — re-verify before relying long-term. The "no mask/structural conditioner" finding is airtight only for the **Gemini-native** models fed via `generateContent`/`inline_data` (not Imagen-via-Vertex, which *does* document mask inpainting — a different API path). Strongest claims rest on OpenAI/Google primary docs; prompting tactics lean on fal.ai blog corroborated by OpenAI's cookbook.

## Primary sources
- OpenAI API image-generation guide + cookbook (high-input-fidelity; prompting guide) — `developers.openai.com`
- Gemini API image-generation + Gemini 3 guide; DeepMind Gemini-image page; Google developer blog
- ControlNet — arXiv:2302.05543 (comparison context)
- DALL·E 2 — arXiv:2204.06125 (text-spelling limitation); arXiv:2503.03595 (garbled-text failure mode)
- Streetmix illustration design-principles — `docs.streetmix.net`
