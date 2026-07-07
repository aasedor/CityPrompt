# Plan-Diagram Conditioning Pilot — 2026-07-07

**Question answered:** does a nadir flat-color plan diagram reliably control an
oblique aerial render? This was the #1 untested experiment flagged by
`docs/DIAGRAM_CONDITIONING_RESEARCH_2026_06_17.md`. Answer: **yes, on both
engines**, when combined with the existing mask/FOOTPRINT machinery and
deduplicated archetype refs.

## Setup

- Site: Beltline test site (project "Custom Style E2E"), Climate First scenario,
  37 drawn plan zones (16 building bars / 8 blocks / park / street grid).
- View: oblique aerial (~40° camera elevation), Photo Realistic style.
- Diagram: client-built 1024px flat-color nadir PNG of the plan zones
  (gray streets / green parks / dark-red building footprints, white ground,
  no text, no scale bar) attached as the FIRST reference image with the label
  "PLAN DIAGRAM — authoritative nadir layout … preserve street network
  topology, block arrangement, park locations and building footprints exactly
  as drawn". Slot 1 matters: GPT Image 2 caps at 16 input images.
- Matrix (6 render calls total this session, all archived in Project Renders):
  1. Baseline pre-dedupe: 48 duplicate archetype refs, no diagram
  2. Baseline dedupe: 9 unique archetype refs, no diagram
  3. Dedupe + diagram: 10 refs (diagram first)
  each × {Gemini 3.1 Flash, GPT Image 2}.

## Results (pre-registered gates: street topology / park location / footprints)

| Engine | No diagram (dedupe) | With diagram |
|---|---|---|
| Gemini 3.1 Flash | Buildings on the main street only; internal grid mostly lost; park good | **Internal cross-street grid reproduced; discrete bars per block incl. L/U courtyard configurations; parks on the drawn blocks** |
| GPT Image 2 | Good block grain, park distributed loosely | **Rigorous orthogonal grid; two central green blocks match the drawn parks; finest footprint adherence of any render to date** |

Both "with diagram" outputs pass all three gates; neither baseline fully does.
Site containment and surrounding-context preservation unaffected.

## Two failure modes found and fixed along the way

1. **Duplicate archetype refs steer composition.** 16 bars × 1 archetype
   attached 48 copies of the same card; Gemini rendered "the card's hero
   scene" (3 mega-buildings) instead of the 38 drawn zones. Fix: refs dedupe
   by (archetype, variant, zone color) — loss-free because zone colors are
   assigned per archetype. 48 → 9 refs restored drawn structure.
2. **The recurring "hallucinated pond+amphitheatre" was not a hallucination.**
   A leftover custom-style test zone ("Custom Park": *"naturalized stormwater
   pond … wooden amphitheatre facing the water"*) sits NE in the site; every
   engine/style rendered it faithfully. Lesson for accuracy debugging: check
   ALL zone inputs (including custom-style zones) before blaming the model.

## Product state after the pilot

- Diagram conditioning is **ON by default** for globe renders when the view
  contains ≥4 AI-planner plan zones (`buildPlanConditioningDiagram` in
  `useGlobeAIRender.ts`); opt out with `localStorage.cc_plan_diagram_conditioning='0'`.
- Server-side equivalent for exports: `GET /api/v1/urban-dna/scenarios/{id}/plan-diagram`
  (`backend/app/services/plan_geometry/plan_diagram.py`) — same palette,
  used by the hearing pack.

## Not yet tested (honest limits)

- Single site, single style family, one run per cell — no seed-variance study.
- Hand-drawn (non-planner) zone diagrams — the builder only fires on plan zones.
- Near-nadir output angles (should be even easier; untested).
- Whether the diagram alone (without archetype refs) suffices.
