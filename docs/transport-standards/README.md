# Transport Standards — side project charter
**Branch:** `side/transport-standards` · **Started:** 2026-06-25 · **Status:** kickoff

> A focused offshoot of City Prompt. Where main City Prompt is a general site-planning/render tool, this is a **transportation-standards visualizer for planners and engineers**: turn the design standards they already use into faithful, to-scale, photoreal renders on real streets — and show where two standards collide.

This is deliberately **separate** from the main City Prompt roadmap (buildings, land-use, parks, the broad archetype catalog). It reuses the *render core* (diagram-conditioning, street/globe/aerial views, OSM road-network awareness) but stays scoped to **the right-of-way**.

Grounded in the research at [`docs/MUNICIPAL_POLICY_SPATIAL_AI_RESEARCH_2026_06_25.md`](../MUNICIPAL_POLICY_SPATIAL_AI_RESEARCH_2026_06_25.md).

---

## Why transportation first
It's the sharpest fit for what the tool does *today*:
- The standards **are to-scale technical drawings** (cross-sections, intersection plans) — exactly the diagram-conditioning input that renders faithfully and **building-free**.
- The catalog **already holds the geometry**: 13 Calgary Street Manual cross-sections, ~24 Vision Zero / traffic-calming treatments, 8 Alberta Bike facilities, ~11 diagram-conditioned archetypes — all on `beeman/main`.
- The audience (transportation engineers + planners) has a **real, live debate** — TAC vs NACTO vs Calgary, fire-access vs walkability — that nobody can currently *see*.

## The standards corpus (what we incorporate)
**Calgary / Alberta**
- Calgary **Street Manual** (Draft 4.0a/4.0b) — cross-sections + Ch9 Intersections + Ch10 Traffic Calming
- **Complete Streets Policy & Guide (TP021)**; **Calgary Transportation Plan (TP012)** road classification
- **Neighbourhood Streets (CP2022-03)**, **Residential Street Design (TP018)**, **Roundabout (TP016)**, **Bicycle (TP011)**, **Pedestrian (TP010)**
- **CSPS033 — Integration of Emergency Services** (fire/EMS access widths)
- **Alberta Bicycle Facilities Design Guide (ABFDG)**

**National / best-practice (the engineer's reference shelf)**
- **TAC** Geometric Design Guide for Canadian Roads (GDGCR); TAC MUTCDC (signs/markings); TAC Canadian Roundabout Design Guide
- **NACTO** Urban Street / Urban Bikeway / "Don't Give Up at the Intersection"
- **AASHTO** Green Book; **FHWA** references where cited

## The three pillars, scoped to the right-of-way
- **SHOW** — pick a standard (a Street Manual class, a TAC cross-section, a NACTO bikeway) → faithful to-scale photoreal render on a *real* Calgary street. *(near-term — reuses the diagram-conditioning path)*
- **COMPARE** — the engineer's killer view: the **same street class under different standards** side by side (Calgary vs TAC vs NACTO), or the same standard on two different real streets. *(near-term — reuses the compare flow)*
- **SURFACE** — render two standards that fight over one finite right-of-way so the trade-off is visible to planner, engineer, and fire chief at once. *(the differentiator — the hard, validate-carefully pillar)*

## First build (Phase 1 pilot — recommended)
**"Standards Browser → render the standard on a real street."** Re-skin the existing `technical-diagram` archetype path as a standards picker:
1. Pick a standard (start with the 13 Street Manual cross-sections already built).
2. Trace it onto a real corridor (OSM-snapped).
3. Get the to-scale photoreal eye-level + 45° aerial.

Then the **SURFACE wedge**: author the **Street Manual narrow residential section vs. the CSPS033 6 m fire-access clear width** as a conflicting-diagram pair, rendered on one real Mount Pleasant street.

## Governance (non-negotiable from day one)
- Every render carries an **"illustrative — not an approved design"** label + C2PA provenance.
- Pair each photoreal image with the **to-scale diagram + numeric dimensions** it was conditioned on (the anti-"misleading render" safeguard).
- No personal data → outside POPA's binding duties.

## Out of scope (keep it separate)
Building massing/land-use renders, parks/plazas, the general archetype catalog expansion, the main City Prompt globe/site-planning roadmap. If a feature isn't about the right-of-way, it belongs on the main branch.

## Open questions
- Which corpus to wire first beyond the Street Manual (TAC GDGCR is the most engineer-credible; NACTO the most demoable).
- Whether the buyer is the City (planners/engineers) or the **consultants who present to councils** (possibly faster — see research §7).
- Accuracy benchmark before any SURFACE claim leaves a demo.
