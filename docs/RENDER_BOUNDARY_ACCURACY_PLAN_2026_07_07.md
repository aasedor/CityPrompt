# Plan-Render Boundary Accuracy — Implementation Plan (2026-07-07)

**Report:** isometric GPT render of a 4-tower single-block plan shows buildings/landscape
bleeding into roads and beyond the polygon boundary — worse than single-building renders.

Designed + adversarially reviewed; every claim verified in
`frontend/src/components/viewer/globe/useGlobeAIRender.ts` and checked against
`docs/CITY_PROMPT_DO_NOT_RETRY_LEDGER_2026_06_17.md`.

## Root causes (verified, in order of contribution)

1. **Silhouette-hull sweep.** The post-render clip mask is per-zone `zoneSilhouette` = convex
   hull of base + roof projected at building height (L375-393). A 28-storey (~90 m) tower's hull
   sweeps ~3× its footprint across streets behind it — anything the model paints inside that
   swath (podiums, landscaping, extra buildings) SURVIVES the clip. Single buildings look
   accurate because one small hull ≠ a plan's union of hulls + street/park zones tiling the site.
2. **Re-projecting styles make screen-space clipping meaningless.** The isometric prompt commands
   a camera re-projection ("parallel projection, zero perspective distortion") — output pixels no
   longer align with the input screenshot, so clipping is geometrically incoherent for it.
   `clay-maquette` also dictates a camera; `site-plan-photo` dictates near-nadir but isn't even in
   ARTISTIC_STYLES.
3. **Plan streets are white (editable) in BOTH masks** by design — nothing downstream can revert
   bleed painted on a plan street, and the diagram label never says streets are open corridors.
4. **Label leak (live bug, all styles):** the clip base is the LABELED screenshot (neon dashed
   borders + text burned in), not the raw capture — border halos/labels survive into every final
   composite today.
5. **GPT resize ghosting (live trap):** model output is stretched to canvas dims without checking
   (`drawImage(rendImg,0,0,w,h)`); ledger §4-B documents GPT reframes → ghosting, and GPT is now
   the default engine. Also: client attaches up to 48 refs while GPT caps at 16 — "Image N" prompt
   labels can reference images GPT never saw (breaks the slot-1 diagram contract).
6. Negative prompt sent for ALL styles includes 'cartoon, illustration, sketch' — directly
   contradicts artistic styles.

## P0 — hours, no render spend

1. **Clip against the RAW capture** (pass `rawBase64`, one line) — kills the label/border leak;
   prerequisite for every measurement below.
2. **Style contract split.** Classify styles by "does the prompt dictate a camera":
   `REPROJECTING_STYLES` = isometric, site-plan, site-plan-watercolor, blueprint, clay-maquette
   (+ decide site-plan-photo explicitly) → SKIP `clipRenderToZones`, return full-frame output,
   documented as "full-frame reinterpretation; boundary fidelity comes from the plan diagram".
   Camera-preserving artistic styles (watercolour, charcoal, pen-and-ink, marker, woodblock,
   collage, risograph, pixel-art) keep the clip.
3. **Style-aware negative prompt**: drop 'cartoon, illustration, sketch' for artistic (keep
   'text, watermark').
4. **Streets clause with a paid-for slot** (≤8 constraint budget, ledger): MERGE the redundant
   FOOTPRINT + FINAL CONSTRAINT clauses, ADD affirmative: "STREETS: the gray corridors in the
   PLAN DIAGRAM reference (Image 2) are streets — render them as open paved right-of-way,
   continuous and unobstructed curb to curb; buildings and landscaping meet the curb line and
   stop." Diagram label gains "streets remain open to the sky."
5. **Boundary parity without amputation**: clip the post-mask to (site boundary ∪ building
   hulls) — raw boundary clipping would amputate painted tower tops near the site edge.
6. **GPT hygiene**: assert/aspect-correct returned image dims before compositing; clamp refs to
   16 when model is GPT and renumber "Image N" labels.
7. **Instrumentation**: log clip-mask coverage % (confirms hull-union hypothesis on the exact
   scene, zero render cost) + check saved-artifact provenance (in-app composite vs raw archive)
   before attributing.

## P1 — a day

8. **Verification gate + one auto re-roll** (standing permission), photoreal/photomontage only:
   after clip, sample plan-street pixels OUTSIDE building hulls and score them RELATIVE to the
   same pixels in the original screenshot (absolute thresholds false-fail on tower shadows /
   golden-hour lighting); diff computed pre-color-grade. <70% street-similar → re-roll once,
   keep the better score.
9. **OSM road carve — honestly scoped as defense-in-depth**: carve buffered OSM road polygons
   from both masks where they fall outside every building hull (protects real roads crossing
   ground-zone masks). It does NOT fix in-hull bleed — only per-building compositing does.
10. **Two-pass artistic (camera-preserving styles) behind a "High fidelity" toggle**: pass 1
    full-frame restyle of the unlabeled screenshot; pass 2 zone inpaint onto the stylized base →
    hard clip composites with no style seam. 2× cost, hence opt-in.

## P2 — experiment (the only complete fix for in-hull bleed)

11. **Per-building z-order rendering revival** (renderPerZone, currently disabled via
    PERZONE_THRESHOLD=99): per-building hull clipping + z-order compositing. Prerequisites before
    any pilot: attach the plan diagram (it currently never does), use the raw capture as the
    cumulative base, apply the color grade ONCE at the end (currently compounds per composite),
    add a failure fallback (a failed building call currently leaves raw zone fill exposed), and
    cost honestly: a 37-zone plan ≈ 37 calls ≈ 30 min at ~50 s/call. Gate to plans with any
    building >10 floors; evaluate on the pilot scene before exposing in UI.

## Pilot protocol (≤8 calls, pre-registered)

- R1–R2: style-contract A/B **on Gemini** (ledger #34: never coerce GPT to stylize) — skip-clip
  isometric vs a camera-preserving isometric prompt rewrite; user picks the contract.
- R3–R4: photoreal with P0.4/5 + P1.9 — pass = <1% pixels changed outside the clip mask
  (measured pre-grade against the raw base) AND street-similarity ≥70%.
- R5–R8: EITHER 3-per-arm street-clause attribution (needs budget bump) OR accept the clause on
  prompting-guidance grounds and spend the reserve on gate-triggered re-roll validation.

## Do NOT (ledger)

No stacked negatives (every added clause displaces one) · no red-mask/zone-crop/auto-frame
retries · no prompt-only scale anchors · manual zoom stays the framing lever (passive hint only:
"zoom so the site fills ~half the frame") · plan diagram stays in GPT slot 1, total refs ≤16 ·
no in-app FLUX depth conditioning · artistic pilots run on Gemini.

## Pre-existing bugs found in passing (tickets)

`temperature: 0.0` and `guidance_scale: 15` on the globe render call (ledger items #25/§4-C —
Gemini 3 wants temp 1.0); duplicated console.log in renderPerZone; per-composite grade compounding.
