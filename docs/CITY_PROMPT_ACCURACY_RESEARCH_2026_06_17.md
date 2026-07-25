# City Prompt: An Accuracy-First Roadmap for Safer-Streets & Intersection Renders

**Prepared for:** City of Calgary Mobility — June 17, 2026
**Scope:** How to make City Prompt's renders faithful enough to publish to staff and the public, within Alberta's data-residency / FOIP / POPA / procurement constraints.
**Method:** Multi-agent deep research (8 dimensions, 19 agents) with adversarial fact-checking of load-bearing claims against fresh sources before synthesis. Refuted/uncertain claims are flagged inline and in §"Items to verify."

---

## 1. Executive Summary + Top 5 Prioritized Moves

City Prompt's core problem is not "which image model is prettiest" — it is **structural fidelity**: lane widths, protected-intersection geometry, refuge islands, and curb extensions must be correct, with zero phantom buildings or wrong-way cars, because misleading renders in a government public-consultation context are a real reputational and legal risk. The research converges on a conclusion that aligns with the 2026-06-17 breakthrough: **the winning lever is structural conditioning on a dimensioned, buildings-free diagram, not better prompting.** Free-text and soft reference images (Gemini, GPT Image 2 reference mode) *recompose* geometry; only a hard structural input (diagram-as-canny/MLSD/segmentation, or true depth from a 3D model) *constrains* it.

**Headline finding:** **No commercial image API (OpenAI GPT Image 2, Gemini/Imagen, FLUX hosted) exposes a hard structural/depth/edge conditioning control as of June 2026.** Implication: **geometry fidelity is the customer's responsibility** — it must come from City Prompt's own upstream representation (buildings-free diagram, a 3D z-buffer, or a self-hosted ControlNet), never from waiting for a vendor toggle.

**Second load-bearing fact (defense-in-depth):** a credible but single-forum-sourced (UNVERIFIED) report says **GPT Image 2's `/edit` mask does not hard-lock unmasked pixels.** Rather than bet on whether it's true, **composite the original roadway/road-network back over every render** — this holds regardless of mask behavior. "Roadways are sacred" should not depend on an unverifiable mask guarantee.

**The procurement gate:** all three hyperscalers offer Canadian data residency for text/LLM workloads, but this research **could not confirm that ANY offers a hosted image-generation model with Canadian in-region data residency.** This reshapes the roadmap.

### Top 5 prioritized moves

1. **(Near-term, highest ROI) Generalize diagram-conditioning into a hard control, catalog-wide — on the pipeline that does the work.** The validated buildings-free-diagram win (`alberta_bike_design_guide`, `protected_intersection_diagram`) was wired into the **globe `useGlobeAIRender` compare path** — the same single-shot pipeline that does OSM-road-network-aware safer-streets renders. Make the dimensioned diagram the *authoritative* geometry input across all street/intersection archetypes; let text set only materials/lighting/entourage. Already built, already on the right pipeline, proven — scale it.

2. **(Near-term) Fix the depth/structure SOURCE before touching the diffuser — mind the pipeline split.** The clay-model z-buffer idea (`MeshDepthMaterial`/`MeshNormalMaterial` + edge pass + reuse the zone-color mask as segmentation) is sound, **but the clay model lives in the *street-view* pipeline (`useStreetViewRender`); safer-streets work runs through the *globe* pipeline, which screenshots Google 3D Tiles and has NO clay model.** Options: (a) treat **diagram-conditioning as the near-term geometry source for globe renders**, reserve z-buffer for street-view; or (b) fund porting clay geometry (or a derived depth/edge pass) into the globe path. Either way, **the depth/structure source is the hard part — the diffuser choice comes after.**

3. **(Near-term) Add a post-generation verification gate; composite the roadway back as defense-in-depth.** Composite the original roadway/road-network back over renders (crossing roads already carved black in `roadNetwork.ts`), and add a self-hosted VLM + open-vocabulary detector (Grounding DINO / Grounded-SAM, open weights, Canadian/on-prem infra — no new data-egress path) that asserts lane count, bike-facility side, no wrong-way vehicles, no phantom buildings before publish. Formalize the standing re-roll permission as a hard-fail checklist.

4. **(Mid-term) Anchor a structured design-rules table on the Canadian/Calgary hierarchy and ground it with RAG — and fix the prompt LANGUAGE.** Calgary Street Manual (draft) + TAC guides are *governing*; NACTO/AASHTO/FHWA *corroborate only*. The `TRAFFIC_SAFETY_DIMENSION_STANDARDS` table + `_traffic_safety_dims.py` exist — extend coverage, reconcile against the Street Manual, index source PDFs with ColPali page-image retrieval so every dimension carries a citation. **Prerequisite:** reconcile injection with prompt best-practice (affirmative > negation; scene-completion not deletion) — notes flag **negatives may be backfiring in `render.py`** and an open **temp-0.0 vs temp-1.0 audit**. End-placement is necessary but not sufficient; rewrite clauses affirmatively.

5. **(Mid-term, the gate) Pick the deployable engine deliberately — and one consistent vendor-origin rule.** Lead with **Azure OpenAI in Canada Central/East** (the vendor Calgary already cleared via M365 Copilot) — but **first verify the specific GPT image model is available as a true Canada-region regional deployment** (today GPT image models appear Global/Data-Zone only). For the sovereign self-hosted fallback, default to **SD3.5 Large ControlNets + FLUX.1 [schnell] (clean-origin, commercially usable)** as primary, with **Qwen-Image (Apache 2.0)** only as a "if City security clears PRC vendor-origin even when self-hosted" option (§8.4).

---

## 2. The Accuracy Problem, Framed

Three render pipelines: **globe** `useGlobeAIRender` (Google Photorealistic 3D Tiles — *runs the safer-streets / intersection / diagram-conditioning work*); the older aerial `useAIRender`; and street-view `useStreetViewRender` (Three.js clay/massing model — *separate pipeline*). Shared failure mode: **the image model treats geometry as suggestion, not specification.**

- **Soft conditioning recomposes.** Gemini/GPT reference inputs are soft conditioners — great for framing/style/identity, but silently distort dimensions. Wrong source of truth for geometry.
- **No vendor offers a hard lock** (§3). Geometry fidelity must originate upstream.
- **The edit mask can't be assumed to be a lock.** UNVERIFIED single-forum report says unmasked pixels can drift. Composite the roadway back regardless.
- **The depth/structure map, not the diffuser, is the hard part.** The June 2026 pilot proved it: FLUX depth ControlNet locked massing beautifully *offline*, but wired into the globe compare as a third engine it was the **WORST engine — including on massing — and was fully REVERTED**, because the in-app depth map was a flat plate, not real 3D volume. Swapping FLUX → SD3.5/Qwen ControlNet does NOT fix this unless the depth/structure source is fixed first.
- **Hallucinated buildings come from "scene completion."** A buildings-free diagram gives the model nothing to complete — why the breakthrough kills phantom buildings.

**Strategy:** separate "accurate geometry" from "pretty pixels." Author the design in a measurement-faithful upstream representation (diagram / clay model / parametric cross-section), use generative AI strictly as the final photorealism pass conditioned on that geometry, and verify before publish.

---

## 3. Models & Structural Fidelity

**Model choice affects photoreal quality, instruction-following, stylization, latency, cost, and residency — NOT geometry-locking.** Prior verdict holds: GPT Image 2 = best accuracy, Gemini 2nd.

| Model | Best at | Maturity / Access | Residency posture | Rough cost | Verification |
|---|---|---|---|---|---|
| **OpenAI GPT Image 2** (`gpt-image-2`, GA Apr 21 2026) | Instruction-following, spatial layout, legible in-image text; native "thinking" plans layout before drawing | GA; public API + Azure OpenAI | OpenAI direct = US; Azure Canada region **but image-model Canada availability unconfirmed** | ~$0.006/$0.053/$0.211 per 1024² (low/med/high); ~4.2s; thinking +15–30s | CONFIRMED (GA, reasoning pass) |
| **Gemini 3 Pro Image** (Nano Banana Pro, `gemini-3-pro-image-preview`) | Stylization, multi-reference (up to 14), style refs, search grounding | GA (preview label); Gemini API + Vertex | Vertex regional (MTL/TOR) **but image residency unconfirmed** | ~$0.13–0.14/image | Exists; specs checkable |
| **Gemini 3.1 Flash Image** (Nano Banana 2) | Fast/cheap drafts; current default | GA (preview); API + Vertex | Same | ~$0.067–0.08/image | Exists; specs checkable |
| **Ideogram 4.0** (Jun 3 2026) | **Bounding-box JSON layout control**; legible text | GA; API + open weights | US-origin; self-host = good residency | API per-image; weights free | Exists; license checkable |
| **FLUX.2 [pro]/[flex]** (Nov 25 2025) | Structured JSON prompting; multi-ref | GA; API (BFL/fal/Replicate) | Germany/EU; `[dev]` self-host non-commercial | $0.015–0.06/MP | Exists; specs checkable |
| **Seedream 5.0 / Qwen-Image** | Benchmark / open-weight conditioning | GA | **PRC-origin** (see §8.4) | ~$0.03/image | Seedream CONFIRMED |

**Routing by intent:**
- **Accuracy-critical finals → GPT Image 2.** Two real costs: ~**6× slower** than Gemini (budget as the slow-but-faithful batch path), and it **won't stylize via prompt** (artistic/concept styles MUST route to Gemini).
- **Fast drafts → Nano Banana 2.**
- **Stylized / concept-mood → Nano Banana Pro.**

`render.py` `_ALLOWED_MODELS` already supports Gemini + `gpt-image-2`. Make routing explicit by intent; treat the temp audit + negatives issue (§5.3) as prerequisites.

**Caveats to flag, not assert:** the "98.5% vs 94.8%" benchmark rests on a single reseller blog (Atlas Cloud) — cite as "per Atlas Cloud." The edit-mask claim is single-forum. **Do not measure faithfulness on vendor leaderboards** (they score typography/identity, not traffic-engineering correctness) — build your own spatial-fidelity eval (§10).

---

## 4. Spatial Conditioning Techniques (the depth-map problem & diagram conditioning)

**Key insight: fix the depth/structure SOURCE first, then choose the conditioning diffuser.**

### 4.1 Ground-truth control map from a 3D model (the unlock — mind which pipeline)
Render depth (`MeshDepthMaterial`), normals (`MeshNormalMaterial`), and an edge pass from a 3D massing model's z-buffer (Blender Z-pass idea). Captures real 3D volume, lane offsets, curb-extension footprints, refuge-island geometry exactly. **The documented fix for the June 2026 flat-plate failure.** **Pipeline caveat:** the clay model with a z-buffer lives in `useStreetViewRender`, NOT the globe pipeline (which screenshots Google 3D Tiles). Drop-in for street-view; for the globe safer-streets path it needs either porting clay geometry in or deriving the control map another way (diagram, §4.2). Zero marginal cost, client-side, no egress.

### 4.2 Diagram-as-conditioning (generalize the breakthrough — already on the right pipeline)
Feed the buildings-free, labeled 2D diagram (cross-section / plan / lane schematic) as the model input image. Line-heavy drawings act as canny/MLSD; color-coded zone diagrams act as segmentation. Validated 2026-06-17, **wired into the globe compare path.** Formalize as a hard canny/MLSD/seg ControlNet (vs a soft Gemini reference) where you control the diffuser, to convert "persuade the model" into "constrain the model." Auto-generate the diagram from a parametric section to stay in sync with the rules table.

### 4.3 The depth-map-generation problem (when no 3D model exists)
For depth from real imagery, **Depth Anything 3** (ByteDance Seed, Nov 14 2025) is SOTA.
- **LICENSING — do NOT state a per-variant split as fact:** the DA3 repo ships a single Apache-2.0 LICENSE. A per-variant NC carve-out is **inferred from the V2 pattern, NOT verified on DA3 model cards.** Confirm each model card before deploying. (V2 Base/Large/Giant CC-BY-NC IS confirmed.)
- **MLSD straight-line conditioning is uniquely suited to roadway/curb geometry** — prioritize for lane edges/curb lines.
- **Residency:** if used, DA3 must run on the SAME Canadian/on-prem GPU as the rest of the stack — don't split depth estimation to a US API.

### 4.4 The licensing gate on ControlNet stacks (hard procurement constraint, CONFIRMED)
- **The entire FLUX.1-dev ControlNet family is NON-COMMERCIAL** (FLUX.1-dev itself is): Shakker Union Pro 2.0, jasperai depth, XLabs. Disqualifying for direct self-hosted government deployment without a paid BFL license.
- **BFL deprecated its own first-party FLUX.1 Depth/Canny API** — FLUX depth now needs a paid BFL self-host license or a third-party host (fal `flux-general`) whose ToS covers the license.
- **Commercially-clean, self-hostable hard-conditioning stacks:**
  - **SD3.5 Large ControlNets (Blur/Canny/Depth)** — Stability Community License, free commercial **under $1M revenue**; Depth model **explicitly built for architectural rendering** (DepthFM). US/UK-origin. **Recommended primary.**
  - **FLUX.1 [schnell] — Apache 2.0** — clean license + clean (EU) origin. **Recommended primary co-engine.**
  - **Qwen-Image + InstantX Qwen-Image-ControlNet-Union — both Apache 2.0.** Cleanest license; native canny/soft-edge/depth/pose. **Caveat: PRC-origin** — hold behind §8.4 clearance.
- **Dependency reminder:** the reverted FLUX-depth pilot proved the diffuser isn't the bottleneck — the depth map is. Choosing SD3.5 / FLUX-schnell / Qwen does NOT fix the flat-plate problem. Fix the z-buffer/diagram source first.
- **Residency:** the entire self-hosted stack (depth model + ControlNet + diffuser + ComfyUI) must be **co-located on the same Canadian / on-prem GPU.** Don't split any hop to a US API.

**Recommendation:** standardize production hard-conditioning on **SD3.5 Large ControlNets + FLUX.1 [schnell]**. FLUX.1-dev for prototyping only, via licensed hosted APIs. Qwen-Image behind vendor-origin clearance.

### 4.5 Orchestration & complementary techniques
- **ComfyUI ControlNet workflows** stacking depth (massing) + canny (lane lines) + segmentation (road/sidewalk/bike), each weighted — self-hosted batch backend on Canadian GPU.
- **Regional prompting / mask-based inpainting** from the existing `archetypeShadeMap` zone colors (effectively a segmentation map) — directly serves "roadways sacred."
- **Never conflate IP-Adapter / multi-reference (style) with ControlNet (geometry).** Soft reference recomposes; only hard depth/canny/seg should be the source of truth for public-facing geometry.

---

## 5. Grounding in Design Standards + Methodology

### 5.1 Authoritative corpus and hierarchy (Canadian/Calgary-first)
1. **City of Calgary Street Manual** (DRAFT, successor to 2014 Complete Streets Guide) — source-of-truth for Calgary cross-sections. **TIMELINE — checkable:** live page states approval **"Anticipated Q4 2026"**, bylaw amendments 2027 — *not* "Winter 2027." Label renders **"draft-aligned."**
2. **TAC Geometric Design Guide for Canadian Roads** (Ch. 3, 5, 9 updated Dec 1 2025 — CONFIRMED) — governing geometric standard.
3. **TAC Bikeway Design Guide + Canadian Guide to Traffic Calming (2nd ed., 2017)** — Canadian device dimensions.
4. **Alberta Bicycle Facilities Design Guide** (CONFIRMED) — `alberta_bike_design_guide` set built from it.
5. **Calgary Safer Mobility Plan 2024–2028** (Safe System, 25% reduction target — CONFIRMED): 40 km/h residential default (since 2021), playground zones 30 km/h, 5 m daylighting at crosswalks.

**Corroborating only (US):** FHWA Proven Safety Countermeasures (the "28 / 5 categories" count is checkable); AASHTO Bike Guide 5th Ed. (Dec 2024, CONFIRMED); NACTO guides + "Don't Give Up at the Intersection"; MUTCD 11th Ed. (Dec 2023, CONFIRMED). **Use Canadian sign standards (MUTCDC), not US MUTCD, for Calgary-facing renders — and date the MUTCDC edition.**

### 5.2 Geometry figures to re-ground before baking into archetypes
- **Protected-intersection setback:** "~3 m typical" well-attested, but **"1.5–7.5 m envelope, >7.5 m = separate intersection"** could NOT be confirmed from the cited NACTO source — re-ground against TxDOT Roadway Design Manual Ch. 18 / NACTO / CROW.
- **FHWA refuge island:** 8 ft (2.4 m) preferred / 4 ft (1.2 m) min — CONFIRMED.
- **NACTO one-way protected bike lane:** 6.5–7 ft (2.0–2.1 m) min rideable, 3 ft (0.9 m) door-zone buffer — CONFIRMED.

### 5.3 Methodology — grounding levers in priority order
1. **Structured design-rules table + prompt injection** (PRIMARY; `TRAFFIC_SAFETY_DIMENSION_STANDARDS` + `_traffic_safety_dims.py` exist). **Prerequisite — fix prompt LANGUAGE:** rewrite injected clauses affirmatively ("a 3 m bike-lane setback at the corner," not "do NOT place the bike lane against the corner"), resolve the temp-0.0-vs-1.0 audit, then exploit end-of-prompt weighting.
2. **Buildings-free diagram conditioning** (highest-fidelity geometry lock, on the globe path) — §4.2.
3. **Multimodal RAG over the standards PDFs** using **ColPali page-image retrieval** — index Street Manual, TAC GDG, NACTO, Alberta Bike Guide as page images for verbatim dimensions + citation trail. Use RAG to populate/verify the table, not to feed raw text into image prompts. **Vendor-origin:** ColPali (PaliGemma-based) is the cleaner default; ColQwen2 (Qwen-derived) carries the §8.4 question. Self-host on Canadian infra.
4. **Automated VLM design-compliance checking** of the output (§10).

**Note:** there is no authoritative machine-readable encoding of NACTO/AASHTO/TAC dimensions. Streetmix/3DStreet schemas are simplified, US-default, editable — use as scaffold and *overwrite* widths with verified TAC/Calgary numbers. The hand-built rules table remains the source of truth.

---

## 6. Competitor / Adjacent Products to Learn From or Integrate

**Standards-grounded but diagrammatic (borrow their accuracy patterns):**
- **StreetPlan.net** — real-time **Red/Yellow/Green best-practice compliance check** vs ITE/CNU + NACTO templates (CONFIRMED). Adopt an inline standards validator on geometry *inputs* before rendering, with the citation in the caption.
- **Streetmix → 3DStreet pattern** — author to-scale cross-section, auto-extrude to 3D, AI-skin it (CONFIRMED). 3DStreet is open-source, 200+ accurately-scaled assets; extrusion/scaling logic studyable. Directly attacks the phantom-building failure.
- **Esri ArcGIS CityEngine 2025 "Street Designer"** + ArcGIS Urban — GIS-accurate per-lane geometry; Calgary is likely an Esri shop. Among the stronger residency stories (Esri Canada / on-prem). Position City Prompt as the photoreal layer *on top of* Esri data.

**Photoreal but ungrounded (differentiate against):**
- **Veras (EvolveLAB)** — closest architectural analog; **Geometry Override Slider** + **region-repaint** are proven UX to borrow ($59/mo). Expose a fidelity control + single-zone repaint.
- **UrbanistAI** — closest public-consultation competitor (Helsinki/Berlin/Cleveland/Pristina); pure photo-stylization, **no standards grounding** — the hallucination risk to avoid. Differentiate on faithfulness + Canadian residency; borrow its workshop UX.
- **betterstreets.org / ArchiVinci / Maket.ai** — commoditized "reimagine this street"; precision claims unsubstantiated.

**Do NOT repeat (REFUTED):** "Sidewalk Labs Delve disabled May 4, 2026" — an unsourced Wikipedia [citation needed]; Delve folded into Google over 2021–2022. Track **Google Earth's** urban/solar/3D tooling. Also don't attribute 3DStreet's built-in AI to Veo/FLUX (over-attributed).

**Data layer:** StreetLight Data and Replica supply speed/conflict/movement evidence to justify *which* intersection to redesign — turning renders into evidence-based proposals.

---

## 7. Accuracy-Adjacent Tech (3D / digital twin / simulation / compliance)

Biggest credibility multiplier: pair each render with **quantified safety evidence** and a **geometry-compliance check**.
- **Two-stage pipeline:** author geometry in 3DStreet or CityEngine 2025 Street Designer → export glTF/depth → conditioning reference → Gemini/GPT Image 2 as the final photorealism pass.
- **Quantified safety evidence:** before/after in **SUMO** (free, Eclipse, scriptable into FastAPI — 1.26.0 Jan 2026) or PTV Vissim; **FHWA SSAM** (free) for surrogate conflicts (TTC/PET). Existing-condition evidence: **Transoft Brisk** (Waterloo/McGill — acquisition was 2020, not recent) and **Miovision Continuous Safety Monitoring** (Kitchener, Jul 2025). Confirm Canadian data hosting before contract.
- **Geometry-compliance gate before rendering:** curb extensions/refuge islands/roundabouts through **AutoTURN/TORUS 2025** (swept-path, NCHRP 1043; Transoft is BC-HQ); operations via **SIDRA Intersection 11** (LOS/queue). **Correction (REFUTED):** Turbo Roundabouts / segments / real signal timings were **v10**, not v11; SIDRA 11 added the ASSIGN module, O-D matrices, Two-Loop Convergence. Only render designs that pass.
- **Near-drop-in basemap upgrade:** **CesiumJS 1.130** (Jun 30 2025) added imagery draping onto Cesium3DTileset — overlay accurate plan/lane-marking layers onto existing Google 3D Tiles, mitigating the shapefile-import parallax/drift.
- **Structure-preserving edit:** **FLUX.1 Kontext** for "add a raised crosswalk here / widen this buffer" (Kontext-dev open-weight, non-commercial — needs a commercial path).
- **Treat image-to-3D (Meshy/Tripo/Hunyuan3D) as secondary asset generation only** — the Meshy spike confirmed it isn't measurement-faithful. **Defer NVIDIA Omniverse/OpenUSD** unless committing to closed-loop simulation.

---

## 8. Data Residency & Procurement — THE GATE

### 8.1 The legal reality (CONFIRMED)
- **Alberta POPA** in force **June 11, 2025**, replacing FOIP's privacy provisions. **POPA does NOT mandate Canadian data residency**; requires *reasonable* safeguards + a mandatory PIA.
- **OIPC released a mandatory POPA PIA template March 26, 2026** (mandatory from May 1, 2026). Its jurisdictional-analysis section forces documenting where data is stored, who controls it, and **US CLOUD Act exposure** for US-parented vendors.
- **The real gate is procedural, not statutory:** (1) the City's internal AI risk-assessment/approval, and (2) a POPA PIA documenting cross-border/CLOUD Act exposure.

### 8.2 The decisive Calgary precedent (CONFIRMED)
The City **blocked ChatGPT on all networks/devices Feb 6, 2026** but **approved Microsoft 365 Copilot** after a risk assessment. Message: *govern AI, don't ban it.* **Consumer endpoints (api.openai.com, public Gemini/ChatGPT) are disqualified.** Run on an enterprise tenant with a completed risk assessment. **Strongly favors the Azure path.**

### 8.3 What is / isn't Calgary-deployable for IMAGE generation
| Path | Deployable today? | Notes |
|---|---|---|
| **Azure OpenAI GPT image, Canada Central/East regional** | **VERIFY FIRST** | GPT image models appear **NOT** in Canada regional deployments per the Foundry region table — only Global or US/EU Data Zone. Best fit *if* a Canada regional deployment appears. |
| **Vertex AI Gemini/Imagen image, Montréal/Toronto regional** | **VERIFY FIRST** | Text/LLM residency CONFIRMED (regional endpoints only). **No Gemini 3.x / current Imagen image model confirmed residency-available in Canada**; Imagen 4.0 was the only Canada-available image model, deprecating ~Jun 30 2026. |
| **AWS Bedrock image, ca-central-1** | **No** | No image-gen model found in ca-central-1; Nova Canvas/Titan G1 going Legacy/EOL. |
| **Azure US/EU "Data Zones"** | **TRAP — not Canada** | US Data Zone = US storage. Use **Canada-region regional deployments only.** |
| **Self-hosted open-weight on Canadian/on-prem GPU** | **YES** | The **only confirmed path to true Canadian-resident image generation today.** Default **SD3.5 + FLUX.1 [schnell]**; hold **Qwen-Image** behind PRC clearance. FLUX `[dev]` needs a paid BFL license. |

### 8.4 The vendor-origin rule + the CLOUD Act ceiling
**One consistent rule:** default the sovereign stack to clean-origin Apache/permissive models — **SD3.5 Large ControlNets + FLUX.1 [schnell]** as PRIMARY — sidestepping the PRC question. Treat **Qwen-Image / ColQwen2** as a "only if City security clears PRC vendor-origin even when self-hosted" option. Apply the same rule to Seedream, Qwen-Image, ColQwen2.

Any US hyperscaler in Canada **reduces but does not eliminate** US-legal-process exposure (CLOUD Act). **Document honestly in the PIA.** Because street/intersection renders typically contain **no personal information**, residual risk is **low and acceptable** for the core use case — argue this explicitly. Reserve sovereign/self-hosted for any workflow with PII/confidential input.
- **Cohere / North** (Canadian-owned, SAP/Bell sovereign cloud) is the strongest sovereignty answer and neutralizes CLOUD Act — **but text/agent/RAG only, no image gen.** Use as the sovereign **RAG/text-grounding layer**.
- **Canada's Sovereign AI Compute Strategy / SCIP** (~$890M from FY2026-27) — forward-looking hosting for self-hosted open image models on Canadian GPUs.

**Build the POPA PIA now** on the OIPC March 2026 template, with a jurisdictional/CLOUD-Act section per vendor, routed through the same governance process that cleared Copilot.

---

## 9. Sharing with Staff & Community + Governance

### 9.1 Use the stack Calgary already owns
- **Front door:** **Engage Calgary on Social Pinpoint** (~167,000 residents) — embed renders with map-pin feedback at the exact intersection.
- **Storytelling/before-after:** **Esri ArcGIS StoryMaps / Experience Builder** with native **Swipe**. **Residency caveat:** ArcGIS Online default offers only US/Europe/Asia-Pacific; Canadian residency needs Esri Canada Protected-B Managed Cloud or ArcGIS Enterprise on-prem.
- **Survey:** **MetroQuest** (within Social Pinpoint) — visual-preference/scenario-tradeoff screens fit rating safer street options.
- **Lightweight before/after:** **JuxtaposeJS**, **img-comparison-slider** (self-hostable, zero egress).
- **Co-design (scoped):** **Streetmix** (accurate-by-construction) and **Block by Block / Minecraft** — keep generative re-rendering *inside City Prompt*, not open public prompting, to prevent hallucinated geometry entering consultation.
- **Deliberation at scale:** **Pol.is** (open-source, self-hostable) or **Go Vocal Sensemaking** for genuine consensus.

### 9.2 Governance — the highest-stakes part (adopt all five)
1. **Hard disclosure/labeling:** every public render gets **"AI-generated concept — not a photograph"** + embedded **C2PA Content Credentials** (v2.3, Jan 2026) — cryptographic, tamper-evident provenance.
2. **APA generative-AI ethics:** disclose use AND limitations; human in the loop; attribute sources.
3. **EU AI Act Article 50** transparency (effective ~Aug 2, 2026 — checkable) — not binding on Calgary but a de-facto reference; adopt its posture (machine-readable mark + visible label).
4. **Human-in-the-loop sign-off:** a planner/traffic engineer verifies each render's geometry against the governing standard **before publication**, with the source cited next to the image.
5. **Aesthetic governance:** **photorealism for accuracy renders, artistic styles for labeled concept-mood only.** Demo learnings flag night/watercolor as anti-patterns that HIDE mask-seam/geometric error photorealistic exposes — disqualifying for faithful public renders.

**Accessibility (procurement gate):** WCAG 2.x AA — descriptive **alt text** + a **text/diagram description** so the safety message never depends on the image alone.

**Defensibility one-liner:** *Pair every photoreal render with a to-scale technical diagram, label it as AI-generated, cite the governing standard, and keep a human-validated source-of-truth attached.* The diagram is both the accuracy input AND the trust artifact.

---

## 10. Proposed Reference Architecture & Phased Roadmap

### 10.1 Accuracy-first reference architecture (the diagram is the source of truth)
```
[1] GROUNDING
    GIS/OSM context + design-PDF RAG (ColPali over Street Manual, TAC GDG,
    NACTO, Alberta Bike Guide page-images; self-hosted, Canadian infra)
        -> retrieves EXACT dimensions + citation
[2] PARAMETRIC INTERMEDIATE  (geometry authority)
    LLM/parametric step emits a labeled, to-scale SVG/diagram cross-section
    or plan (lanes, curbs, refuge islands, bike widths) - editable. THIS is
    the globe-path geometry source.
    Alt (STREET-VIEW only): clay model z-buffer (MeshDepthMaterial + edge +
    zone-color seg). NOTE: clay model exists in useStreetViewRender, NOT the
    globe pipeline - porting required to use it on globe.
[3] STRUCTURAL CONDITIONING  (geometry lock - NOT prompt text)
    Render diagram/depth/seg map as the input image:
      - cheapest/live, ON THE GLOBE PATH: diagram-as-input to Gemini/GPT
        Image 2 (validated breakthrough)
      - hardest lock (self-hosted): SD3.5 / FLUX-schnell ControlNet
        (depth + canny/MLSD + seg) - fix the DEPTH SOURCE first
    Text sets ONLY materials/lighting/entourage, phrased AFFIRMATIVELY.
[4] GENERATION  (route by intent + residency)
    Final/accuracy -> GPT Image 2 (Azure Canada, VERIFY; 6x slower, won't
      stylize) or self-hosted SD3.5/FLUX-schnell+ControlNet
    Draft -> Nano Banana 2;  Stylized/concept -> Nano Banana Pro
[5] VERIFICATION GATE  (hard-fail before publish; all self-hosted, no egress)
    Grounded-SAM / Grounding DINO segment the render ->
      IoU vs labeled diagram regions; lane-count match; bike-facility side;
      disqualifier detection (phantom buildings, wrong-way vehicles)
    + composite original roadway/road-network back (DEFENSE-IN-DEPTH)
[6] AUTO-CORRECT  (VLM-critique -> corrective regen, cap ~2-3 iterations)
[7] GOVERNANCE WRAP
    C2PA + "AI-generated concept" label + cited standard + engineer sign-off
    + PHOTOREAL-only for accuracy -> publish via Social Pinpoint / StoryMaps
[8] EVIDENCE PAIRING (optional, high-credibility)
    SUMO+SSAM conflict-reduction and/or AutoTURN/SIDRA compliance pass
```

### 10.2 Phased roadmap
**Near-term (weeks — built on what you have):**
- Generalize diagram-conditioning catalog-wide on the globe path; diagram = authoritative geometry, text = finish only.
- Street-view path: add the Three.js z-buffer control-map pass. Decide explicitly whether to fund porting clay geometry into the globe path or rely on diagrams there.
- Composite the original roadway back as defense-in-depth; don't rely on the edit mask being a hard lock.
- Add a self-hosted VLM + Grounding-DINO verification gate hard-failing on phantom buildings / wrong-way cars / lane-count mismatch; formalize the re-roll checklist.
- Fix prompt LANGUAGE: rewrite injected dimension clauses affirmatively; resolve the negatives-backfiring + temp audit in `render.py`.
- Re-ground the protected-intersection setback against a primary source; re-verify the Street Manual timeline; label Street-Manual renders "draft-aligned."

**Mid-term (1–2 quarters):**
- Build out rules-table coverage; reconcile against the Street Manual; ground with ColPali RAG (self-hosted, Canadian infra) for citations.
- Run the **3-engine accuracy bake-off** — ONLY after fixing the depth source: (A) soft reference baseline; (B) SD3.5 Large Depth+Canny fed a real volumetric depth source; (C) FLUX-schnell ControlNet stacked depth+seg — scored by **overlaying rendered lane edges on the input geometry**, not eyeballing. (Qwen only if PRC origin cleared.)
- Stand up procurement: POPA PIA on the OIPC template; verify Azure Canada GPT-image region availability; stand up the self-hosted SD3.5/FLUX-schnell + ControlNet fallback, all hops co-located on Canadian/on-prem GPU.
- Adopt StreetPlan-style Red/Yellow/Green compliance check on geometry inputs; expose a Veras-style fidelity slider + single-zone repaint.
- Add C2PA + labeling + engineer sign-off + photoreal-only rule to the publish path; wire renders into Social Pinpoint / StoryMaps.

**Longer-term (2+ quarters):**
- Build a GenEval/Blueprint-Bench-style spatial-fidelity regression suite over the archetype catalog so faithfulness is tracked, not vibed.
- Pair renders with quantified safety evidence (SUMO+SSAM) + geometry-compliance passes (AutoTURN/SIDRA) for high-stakes consultations.
- Interoperate with the City's Esri/CityEngine geometry; evaluate Cohere/North as the sovereign RAG layer; track Canada's SCIP sovereign compute.

---

## 11. Sources (representative; full set verified during research)

**Models & conditioning:** GPT Image 2 — https://en.wikipedia.org/wiki/GPT_Image · edit-mask forum report — https://community.openai.com/t/gpt-image-2-masking-issue/1379510 · Nano Banana Pro — https://blog.google/innovation-and-ai/products/nano-banana-pro/ · Nano Banana 2 — https://workspaceupdates.googleblog.com/2026/02/introducing-nano-banana-2-in-gemini-app.html · Ideogram 4.0 — https://ideogram.ai/news/ideogram-4.0/ · ControlNet — https://arxiv.org/abs/2302.05543 · SD3.5 Large ControlNets — https://huggingface.co/stabilityai/stable-diffusion-3.5-controlnets · FLUX.1 schnell (Apache 2.0) — https://huggingface.co/black-forest-labs/FLUX.1-schnell · FLUX.1-dev ControlNet (non-commercial) — https://huggingface.co/Shakker-Labs/FLUX.1-dev-ControlNet-Union-Pro-2.0 · Depth Anything 3 — https://github.com/ByteDance-Seed/Depth-Anything-3 · ColPali — https://arxiv.org/abs/2407.01449

**Design standards:** TAC GDG — https://www.tac-atc.ca/en/knowledge-centre/technical-resources-search/publications/ptm-geodes11-e/ · Alberta Bicycle Facilities Design Guide — https://www.calgary.ca/Transportation/TP/Pages/Cycling/Alberta-bicycle-facilities-design-guide.aspx · Calgary Street Manual — https://www.calgary.ca/planning/city-building-program/city-building-program/the-street-manual.html · Calgary Safer Mobility Plan — https://www.calgarypolice.ca/content/dam/police/documents/MobilityPlan2024_V3.pdf · FHWA Proven Safety Countermeasures — https://highways.dot.gov/safety/proven-safety-countermeasures · NACTO protected bike lanes — https://nacto.org/publication/urban-bikeway-design-guide/designing-bikeways-for-all-ages-and-abilities/protected-bike-lanes/designing-protected-bike-lanes/

**Competitors / adjacent:** 3DStreet — https://www.3dstreet.com/ · Streetmix — https://streetmix.net/ · StreetPlan.net — https://streetplan.net/ · Veras — https://www.evolvelab.io/veras · CityEngine 2025.1 — https://www.esri.com/arcgis-blog/products/city-engine/3d-gis/whats-new-in-arcgis-cityengine-2025-1 · UrbanistAI — https://site.urbanistai.com/

**Accuracy-adjacent:** CesiumJS draping — https://cesium.com/blog/2025/06/30/draping-imagery-over-3d-tiles-in-cesiumjs/ · FHWA SSAM — https://highways.dot.gov/research/publications/safety/surrogate-safety-assessment-model-ssam · SUMO — https://zenodo.org/records/18406080 · Miovision CSM — https://www.globenewswire.com/news-release/2025/07/14/3114581/0/en/From-Near-Miss-to-Vision-Zero-Miovision-Empowers-Cities-to-Act-Before-Crashes-Happen.html · TORUS 2025 / NCHRP 1043 — https://www.transoftsolutions.com/news/torus-2025-sets-a-new-standard-in-roundabout-design/

**Residency / procurement:** Alberta POPA — https://www.alberta.ca/about-the-protection-of-privacy-act · OIPC PIA template — https://www.dataguidance.com/news/alberta-oipc-launches-mandatory-pia-template-public · Calgary ChatGPT block / Copilot approval — https://livewirecalgary.com/2026/02/10/city-of-calgary-blocks-chatgpt-use-on-city-devices-and-networks/ · Vertex AI data residency — https://cloud.google.com/vertex-ai/generative-ai/docs/learn/data-residency · Azure OpenAI data privacy — https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy · SAP + Cohere sovereign AI (Canada) — https://news.sap.com/canada/2026/02/sap-and-cohere-expand-partnership-to-launch-sovereign-ai-solutions-globally-beginning-in-canada/

**Engagement / governance:** Engage Calgary — https://engage.calgary.ca/ · MetroQuest — https://metroquest.com/product/ · C2PA — https://contentauthenticity.org/ · APA AI ethics — https://www.planning.org/blog/9295637/planning-ethics-and-generative-ai/ · WCAG — https://www.w3.org/WAI/standards-guidelines/wcag/

---

## Items to verify before stating as fact in public-facing material
- **No commercial image API offers hard structural/depth/edge conditioning as of June 2026** (the roadmap's core assumption — re-verify at decision time).
- Whether **any** GPT/Gemini/Imagen/Bedrock image model has **Canadian in-region residency** today (none confirmed — re-check vendor region tables).
- **GPT Image 2 edit-mask "not a hard lock"** (single-forum — design roadway-composite-back so the action is independent of the answer).
- **Depth Anything 3 license** (repo = single Apache-2.0 file; per-variant NC split inferred from V2, not confirmed — check each model card).
- **Calgary Street Manual approval timeline** (Q4 2026 vs Winter 2027).
- **Protected-intersection setback envelope** (re-ground against TxDOT Ch. 18 / NACTO / CROW).
- FHWA "exactly 28 countermeasures," current **MUTCDC edition**, EU AI Act Art. 50 effective date.

## Refuted and stripped (do not resurface)
- "Sidewalk Labs Delve disabled May 2026" (unsourced).
- SIDRA 11 = Turbo Roundabouts / segments (those are v10).
- 3DStreet built-in AI = Veo/FLUX (over-attributed).
- Fabricated performance figures: "Reflect-DiT +30–40%" and "GLIGEN 6.8×".
