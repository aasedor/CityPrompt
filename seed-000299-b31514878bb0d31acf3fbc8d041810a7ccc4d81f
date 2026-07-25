# City Prompt → Municipal Policy Engine
## Deep research: visualizing & reconciling a city's policies *spatially*
**Date:** 2026-06-25 · **Author:** Claude (research workflow: 25 agents, 11 web-sourced dimensions, adversarial verification, ~2M tokens, 263 unique sources) · **For:** Andrew (City of Calgary planner / City Prompt = SiteForge)

---

## 0. TL;DR

**The idea is real white space — but the moat is a *fusion*, not any single piece, and the hard part is the part you most want.**

The market splits into **four camps that never touch**:
1. **Rules-engines & zoning-as-data** (Esri CityEngine/ArcGIS Urban, Gridics/Zoneomics, Forma, TestFit, Symbium, Archistar, Boston/Singapore twins) — turn *numeric* zoning into **grey massing or pass/fail**. Accurate, never a believable picture, and they ingest pre-digitized parameters, not policy *prose*.
2. **Photoreal / AI-render tools** (3DStreet, ArchiVinci, mnml.ai, AIRIlab) — make the **believable image**, even on real map tiles — but are **policy-blind** and tell you to check code compliance by hand.
3. **Rules-as-Code & text-contradiction NLP** (NZ Better Rules, OpenFisca, Georgetown Policy2Code, LegalWiz, AI-Zoning, CLAUSE benchmark) — **read policy and even flag conflicts** — but are non-spatial, non-visual, and mostly tax/benefits/parcel-compliance scoped.
4. **Spatial conflict mapping** (McHarg overlay → LUCIS, marine-spatial-planning conflict scores, UK CReDo) — show clashes **on a map**, but as use-vs-use rasters or *physical-asset* cascades, **never read from the city's own written policy**.

**No surveyed tool does the three-way combination at the core of your idea:** treat a municipal *standard* as the authoritative source of geometry → render it **photo-realistically and to-scale on a specific real site** → **surface where two policies from different disciplines collide** on that same ground. Your June-17 **diagram-conditioning breakthrough is the literal mechanism every other camp lacks.**

**But three caveats kept the verifiers honest:**
- The "nobody does X" claims are **directionally true but consistently *overstated***. Archistar markets "photorealistic simulations" from a site address + zoning; Esri has a 2024 CityEngine→GenAI photoreal prototype and is shipping photoreal materials in 2026; 3DStreet added photoreal AI in Sept 2025; **UrbanLogiq** (Vancouver) already sells a *Canadian, data-resident* gov AI twin. The fusion is unoccupied; the components are maturing fast.
- The **SHOW** and **COMPARE** functions are near-term and within reach. The **SURFACE-contradictions** pillar is simultaneously the **sharpest white space and the least-validated, hardest capability** to deliver — and it carries political/legal risk (see §6).
- The whole thing is **supply-side**: the research proves nobody *builds* this; it does **not** prove anyone at the City is *funded to want* it. The documented planner pain is **circulations / resubmissions / interdepartmental delay**, which is *adjacent* to "see the contradiction," not identical. **Demand discovery is the missing step.**

**Recommended posture:** lead with **SHOW + COMPARE** (low-risk, demoable now, reuses existing pipeline); treat **SURFACE** as the visionary differentiator you prove on **one inherently-spatial, already-numeric conflict** — the **Street Manual cross-section vs. fire-apparatus clear width (CSPS033)** — before claiming the general "policy coherence engine."

---

## 1. The reframe: SHOW · COMPARE · SURFACE

Today City Prompt answers *"what would this archetype look like here?"* The municipal-policy version answers the three questions planners actually fight over:

| Pillar | Question | Maturity | Risk |
|---|---|---|---|
| **SHOW** | "What does this policy *mean* on the ground?" | **Near-term** — reuses diagram-conditioning today | Low |
| **COMPARE** | "How does the same policy play out *differently* across the city?" | **Near-term** — reuses compare/multi-preview | Low–med |
| **SURFACE** | "Where do two policies *collide* on the same ground?" | **Visionary** — unbuilt anywhere | High (technical + political) |

This sequencing matters: SHOW/COMPARE are *demos you can ship*; SURFACE is *the story that makes it a category*, but it's where hallucination, liability, and "contradiction is a feature not a bug" (§6) bite.

---

## 2. The customer's real terrain: Calgary's policy stack & where it self-contradicts

### 2.1 The three-tier stack (and why the middle tier is the sweet spot)

1. **Statutory apex — aspirational prose.** The **Municipal Development Plan (LUP009)** + **Calgary Transportation Plan (TP012)**: 60-year strategic plans, mostly principle/vision language (headline numeric target: 50% of 2009–2069 growth / ~650k people into established areas). **These two are being merged into a single plain-language statutory document, "The Calgary Plan"** — but adoption is **politically unsettled and delayed**: a June 16 2026 council decision pushed it to a "What We Heard" report in **Jan 2027** (13-2), and a councillor moved to *abandon* the replacement entirely (amendment failed). *Don't anchor a product on this timeline.*
2. **Regulatory ground truth — machine-readable.** **Land Use Bylaw 1P2007** is the only legally binding, parcel-by-parcel, fully numeric instrument (setbacks, heights, coverage, density, parking), and Calgary **publishes the district polygons as open shapefiles on data.calgary.ca** — a free grounding layer. **Live, fast-moving fact:** the 2024 citywide **blanket rezoning** to R-CG/R-G base districts (passed 9-6, May 2024, after the city's largest-ever public hearing) was **REPEALED 12-3 on April 8 2026, effective Aug 4 2026**, reverting to pre-2024 designations. Parking minimums were *removed for non-residential* and *reduced (not eliminated) for residential*.
3. **The middle layer — numerically-specific AND spatial (City Prompt's strongest fit).**
   - **Local Area Plans** (built on the *Guidebook for Great Communities*) encode policy as **two explicit GIS map layers**: an **Urban Form Map** (15 categories) and a **Building Scale Map** with **six numeric storey categories** — *Limited ≤3, Low-Modified ≤4, Low ≤6, Mid ≤12, High ≤26, Highest 27+*. This is **the most directly renderable, numerically-precise policy in the whole stack.**
   - **Street design** lives in **Complete Streets Policy (TP021, 2014)** and its successor the **Street Manual** (draft; final expected **Q4 2026**, bylaw amendments 2027), which translate ~9 street classes into **to-scale cross-sections** driven by land-use context + target speed — *exactly the to-scale diagram input City Prompt already renders from.*

The disciplinary/cross-cutting policies — TOD (LUP002, 600 m radii), Heritage (LUP007), Slope-Adaptive (LUP008), Bicycle (TP011), Pedestrian (TP010), Neighbourhood Streets (CP2022-03), Residential Street Design (TP018), Roundabout (TP016), **Integration of Emergency Services (CSPS033)**, Urban Forest, Biodiversity, Wetland, Source Water, Noise (TP003) — are exactly the silos that **collide on a single right-of-way.**

### 2.2 The Calgary contradiction catalog (citable, spatial, mostly geographic)

| Conflict | The two sides | Spatial manifestation | Status |
|---|---|---|---|
| **Fire access vs. walkable narrow streets** | Fire/EMS apparatus clear-width vs. Complete Streets / Neighbourhood Streets calming | A residential cross-section that can't host bulb-outs + trees AND a 6 m clear width | **CSPS033 exists *because* of this** — names emergency response as a co-equal stakeholder to balance against walkable design |
| **Cycle network vs. vehicle throughput** | Complete Streets / Bicycle Policy vs. auto LOS — escalated to **province vs. city** | 8 Ave SW cycle track; protected intersection vs. turn capacity | **Live (2025–26):** Alberta minister "actively reviewing" Calgary bike lanes; councillor moving to axe 8 Ave SW track |
| **Density vs. neighbourhood character** | MDP / Established-Area growth (R-CG) vs. character/parking/process-trust | Fourplex on a 50-ft inner-city lot vs. detached context | **Live:** blanket rezoning passed then **repealed**; LAPs now pitched as the "middle ground" |
| **Tree canopy vs. utilities** | Urban Forest Strategic Plan (canopy **8.25% → 16% by 2060**) vs. buried gas/streetlight/utility setbacks | Treed boulevard width vs. utility corridor on the same section | Documented in the Strategic Plan |
| **Environment vs. development** | Wetland/biodiversity ("no net loss") vs. growth | Logan Landing / Ricardo Ranch on intact Bow River wetland (**~90% of pre-settlement wetlands already lost**) | **Live, geographic** |
| **Skyway vs. street vitality** | Plus-15 Policy (CP2021-03) vs. Pedestrian Policy / ground-floor retail | Second-storey network draining sidewalk life; entangled with office-conversion strategy | Decades-old, well-documented |
| **TOD density vs. parking / heritage / slope** | TOD guidelines vs. Parking Policies, Heritage (inner-city clusters), Slope-Adaptive | Station-area density gradient hitting heritage blocks or slope limits | Structural |
| **Roundabouts vs. truck routes** | Roundabout Policy (TP016) vs. Truck / Dangerous-Goods / High-Load route networks | Long-vehicle turning envelope vs. compact roundabout geometry | Structural (visible in the policy index itself) |

### 2.3 Why these stay invisible until built

The policy-coherence literature (Scott & Gong on government "silos"; horizontal/vertical/internal coherence) explains the mechanism: government is organized into **self-governing subsystems that each optimize a local logic** and **encode their constraint as a quantitative filter** (fire clear-width, vehicle LOS grade, parking ratio, utility setback). Each scores *fine in its own silo's documents* while producing a hostile *aggregate* built outcome. **The contradiction is spatial and only legible when the standards are drawn/built on the same real cross-section** — which is precisely the gap a to-scale photoreal render closes by "building" the policy virtually first. Calgary itself implicitly admits the gap: its **City Building Program** is explicitly trying to make the new Zoning Bylaw and Street Manual "part of the same plan."

---

## 3. Is anyone doing this? The landscape

### 3.1 Capability matrix (state as of mid-2026; yes / partial / no)

| Tool | Camp | Ingests policy *text* | Machine-readable rules | Spatial/GIS | 3D/visual | **Photoreal** | **Contradiction detect** | Muni-deployed |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| Esri **CityEngine** | Procedural rules→3D | – | ✓ | ✓ | ✓ | ◐ | – | ✓ |
| Esri **ArcGIS Urban** | Municipal zoning scenarios | – | ✓ | ✓ | ✓ | – | ◐ | ✓ |
| **Symbium** (Complaw) | Computational law | – | ✓ | ◐ | ◐ | – | ◐ | ✓ |
| **Archistar** (+AI PreCheck) | Rules engine + gen design | ◐ | ✓ | ✓ | ✓ | – | ◐ | ✓ |
| **Gridics / Zoneomics** | Zoning-as-data | ◐ | ✓ | ✓ | ◐ | – | – | ✓ |
| **Autodesk Forma** | Massing optimizer | – | ✓ | ✓ | ✓ | – | – | ◐ |
| **TestFit** | Feasibility/massing | – | ✓ | ◐ | ✓ | – | – | – |
| **Boston BPDA twin** | Municipal twin (zoning-check) | – | ✓ | ✓ | ✓ | – | ◐ | ✓ |
| **Virtual Singapore** | National semantic twin | – | ◐ | ✓ | ✓ | – | – | ✓ |
| **MIT CityScope** | Tangible policy-sim table | – | ◐ | ◐ | ◐ | – | ◐ | ◐ |
| **UK NDT / CReDo** | Cross-sector infra twin | – | ◐ | ✓ | ◐ | – | **✓** | ◐ |
| **UrbanFootprint / UrbanSim** | PSS scenario forecast | – | ✓ | ✓ | – | – | – | ✓ |
| **AI-Zoning / zoning-gpt** | Academic zoning-LLM | **✓** | ✓ | – | – | – | – | – |
| **OpenFisca / NZ Better Rules** | Rules-as-Code (non-spatial) | ◐ | ✓ | – | – | – | – | ✓ |
| **McHarg overlay / LUCIS** | GIS suitability/conflict | – | ◐ | ✓ | – | – | ◐ | ✓ |
| **3DStreet (+StreetDesign.ai)** | Web street design + photoreal | – | – | ✓ | ✓ | **✓** | – | ◐ |
| **ArchiVinci / mnml.ai** | AI archviz | – | – | – | ◐ | **✓** | – | – |
| **LegalWiz / GPT-4 reg-NLP** | Text contradiction detect | **✓** | ◐ | – | – | – | **✓** | – |
| **AIRIlab** | Zoning-text→mockup (marketing) | ◐ | – | – | ◐ | ◐ | – | – |
| **OntoZoning** (Singapore) | Ontology binding rule→geometry | ◐ | ✓ | ✓ | – | – | – | ◐ |

**No row has ✓ in all of {text, photoreal, contradiction, muni}.** That empty intersection is the product.

### 3.2 The seven closest analogues — and the gap each leaves

1. **3DStreet (+StreetDesign.ai)** — *the single closest analogue.* Converts a Streetmix/StreetPlan cross-section to 3D, blends it onto **real-world 3D map tiles**, and since **Sept 2025 renders photoreal via frontier AI**. **Gap:** policy-*blind* and standard-*agnostic* — it renders whatever section a human hands it; it never tells you the geometry the *policy* requires, does no cross-site comparison, and has **zero contradiction detection**.
2. **AIRIlab** — *the only vendor whose stated pitch matches your thesis end-to-end* (zoning text → streetscape preview → strict/moderate/flexible scenario compare). **Gap:** marketing-stage and unverified — no confirmed photoreal, no confirmed real-named-site fidelity, no contradiction detection, no named municipal deployment.
3. **Esri ArcGIS Urban / Boston BPDA twin** — *the strongest real, in-production municipal "policy-check."* Boston checks projects against the **actual zoning code** (height/density/use) + shadow studies on ~129k buildings; ArcGIS Urban auto-converts zoning into 3D buildable envelopes. **Gap:** untextured **grey massing, never photoreal**; consumes numeric envelopes, not design *prose*; "conflict" logic is narrow zoning-vs-land-use validation, **not cross-disciplinary**. *(Watch-out: Esri has a 2024 CityEngine→GenAI photoreal prototype + 2026 photoreal-materials roadmap + Esri Canada data centres — this is the half an incumbent closes first.)*
4. **UK NDT / CReDo** — *the strongest real **contradiction/interdependency** analogue:* propagates how a climate shock cascades failures **across** energy/water/telecoms owners. **Gap:** operates on **physical assets**, not written policy; outputs failure graphs, not site renders; needs secure multi-utility data sharing.
5. **Symbium (Complaw)** — *the only documented case anywhere of a tool surfacing a code contradiction a city didn't know about* (turns an ADU design red on violation; instant permitting in 271+ jurisdictions). **Gap:** the contradiction-surfacing was an **accidental byproduct, in 2D**, project-compliance-centric; no photoreal, no cross-discipline reconciliation.
6. **LegalWiz / GPT-4 regulatory contradiction detection** — *proves the hardest half (text contradiction) is technically feasible* (multi-agent retrieval + entailment). **Gap:** entirely textual — no map, no geometry, no render; and the **CLAUSE benchmark shows frontier LLMs are still weak** at legal contradiction (F1 ranges from ~7% to ~63%), so reliability is unproven.
7. **McHarg overlay → LUCIS** — *the 60-year foundational technique* for making spatial conflict visible by overlaying weighted constraint layers. **Gap:** conflict is inferred from *suitability* layers, **not read from policy text**; raster heatmap, not a scene; captures use-vs-use competition, not policy-vs-policy on a cross-section.

### 3.3 Honest verdict on novelty

The white space for the **three-way fusion** is **real** (every dimension's verifier confirmed *the combination* is unoccupied). But each "no one does this" sub-claim was flagged **OVERSTATED** in isolation, because the components are individually maturing fast and a couple of vendors (Archistar, ArcGIS Urban roadmap, 3DStreet, UrbanLogiq) are adjacent. **The defensible moat = the fusion + the photoreal-on-real-site step + Alberta data-residency fit — not any one component.** Treat "nobody does this" as a *negative finding from broad search*, not proof of non-existence, and assume an 18-month window before an incumbent attempts the overlap.

---

## 4. Why City Prompt is uniquely positioned: the diagram-conditioning bridge

Every other camp is missing one specific mechanism: **a way to turn a *standard's drawing* into a *faithful, to-scale, photoreal render on a real site*.** That is exactly the June-17 breakthrough — feed an engineered, annotation-free, to-scale **technical diagram** (cross-section or intersection plan) as the model's reference image and the render reproduces *that exact geometry, building-free.* Validated in-app on the protected-intersection plan ("pretty great job with GPT") and the Collector cross-section.

This is the literal "policy-prose/drawing → photoreal place" bridge the Rules-as-Code world, the digital-twin world, and the archviz world each lack. Combined with what's already built — **zone drawing on 2D/globe/street views, the ~115-archetype catalog (incl. Calgary Street Manual cross-sections + Vision Zero treatments), OSM road-network awareness, the merged shapefile-import pipeline, and the side-by-side compare flow** — the SHOW and COMPARE pillars are *mostly assembly*, not new capability.

**Honest counter (from the critique):** diffusion models hallucinate geometry **even with conditioning**, and your *own* in-app FLUX-depth pilot was the **worst** result and was fully reverted. So "diagram-as-authoritative-geometry" is the **least-proven load-bearing claim**. Soft-conditioning works for *roadway* geometry (validated); it does **not** yet faithfully render *prose modifiers* (step-backs, massing) or guarantee dimensional accuracy good enough to be a *planning instrument* rather than an *illustration*. This gates how far SURFACE can go (see §6).

---

## 5. Eight product concepts (ranked by build-now value)

> Effort/risk are relative. "Fit" = how much reuses existing City Prompt capability.

### A. Policy-as-Standard Render — *effort: low* ⭐ start here
Pick a standard from a dropdown (a Street Manual cross-section, a Vision Zero treatment, an R-CG built form), trace it onto a **real** street/parcel, get a to-scale photoreal eye-level + 45° aerial of *exactly* what that standard produces — no hallucinated buildings, no manual prompt.
- **How:** re-skin the existing `technical-diagram` generationTag path as a *policy browser*; only new work is a policy-catalog index mapping a council-readable policy name → archetype + a one-paragraph "what this standard requires" caption from the source PDF.
- **Calgary:** "Complete Streets — Activity Street cross-section (Street Manual ch. 4)" traced onto a real block of 17 Ave SW → the to-scale lane/cycle-track/boulevard/tree allocation on the *real* street, not an artist's impression.
- **Risk:** validated only on street/intersection geometry; prose modifiers won't render faithfully yet; **must label "illustrative, not an approved design."**

### B. Same Policy, Two Places — *effort: medium*
Render the *identical* standard on two real Calgary sites side by side, so a planner SEES that "≤6 storeys" or "a protected intersection" lands very differently on a wide suburban arterial than on a tight inner-city street.
- **Calgary:** the LAP "Low (≤6)" category on a Marda Loop lot vs. an identical-width Bowness lot → contextual infill vs. out-of-scale wall — the exact "character" argument that drove the R-CG fight, **made visual for a public hearing.**
- **Risk:** soft-conditioned, so context differences may be under/over-dramatized — persuasive, *not* a measurement.

### C. Contradiction-on-a-Cross-Section — *effort: medium* ⭐ the differentiator
Take two standards from different departments that fight over the same finite right-of-way and render **both** faithfully on one real street so the collision is visible to planner, fire chief, and council at once.
- **Calgary:** a real traffic-calmed street in Mount Pleasant — render the Neighbourhood Streets narrow section, then the same street widened to the **6 m fire-access clear width CSPS033 forces**; the side-by-side shows the bulb-outs and trees that must be deleted. *The textbook fire-vs-walkability collision, shown instead of argued.*
- **Risk:** illustrates the geometric *trade-off*; does **not prove** the standard is unmeetable (compact apparatus / control vehicles can resolve some). Frame as "here's the trade-off to negotiate," not "this is illegal." Authoring honest conflicting pairs needs real engineering input.

### D. Policy Conflict Heatmap → Render-the-Hotspot — *effort: high*
Overlay Calgary's open GIS layers (land-use districts, truck/dangerous-goods routes, cycle network, TOD 600 m radii, heritage, slope) to flag where two layers spatially collide, then click any hotspot to render the clash photo-realistically.
- **How:** the **merged shapefile-import pipeline** proves the vector-drape works; compute geometric overlaps; each flagged segment becomes a pre-loaded drawable zone → hand off to the existing render. *Heatmap finds WHERE; render shows WHAT.*
- **Calgary:** where the High-Load/Dangerous-Goods truck network crosses the planned downtown cycle network near 8 Ave SW → render both the truck-turning envelope and the protected-intersection treatment on the real junction.
- **Risk:** **geometric overlap ≠ policy contradiction** — needs hand-tuned per-layer-pair rules or it cries wolf; depends on data.calgary.ca currency (R-CG repeal Aug 2026 must be reflected). Most net-new engineering.

### E. Before/After a Policy Change — *effort: low*
Same block, current rule vs. proposed rule, side by side — timed to Calgary's live transitions (R-CG repeal Aug 2026; Street Manual finalization Q4 2026).
- **Calgary:** on a 50-ft inner-city lot — pre-2024 detached form → 2024 R-CG fourplex → post-Aug-2026 reverted form: the literal visual history of the blanket-rezoning saga on one lot, for a council briefing on *what reverting actually means.*
- **Risk:** needs an archetype per policy version (some must be authored); shows *form* faithfully, not *market reality* — not a development forecast. **Don't over-anchor on the Calgary Plan timeline (politically unsettled).**

### F. LAP Building-Scale Painter — *effort: medium*
Load a Local Area Plan's Building Scale Map, "paint" its six storey categories onto the real blocks, render the eye-level + aerial streetscape that height policy actually produces. *The most directly renderable policy in the stack* — and the catalog already carries `minFloors`/`maxFloors` per archetype.
- **Calgary:** paint "Mid (≤12)" along a main street and "Limited (≤3)" on interior heritage blocks → see whether the ≤12 frontage overwhelms the ≤3 homes behind (inner-city heritage-vs-density made visible).
- **Risk:** heights are in *storeys* not metres, and step-back/massing modifiers are still prose — renders *approximate* the envelope. Document a storey→metre assumption; caveat that modifiers aren't honored.

### G. Cross-Section Width Budget — *effort: medium*
Lay every discipline's claim on one street's width — travel lanes, fire clear width, protected cycle track, sidewalk, utility setback, canopy boulevard — and render what the ROW looks like when each wins. Exposes the literal **zero-sum** nobody sees until it's built.
- **Calgary:** on a real collector, show the Urban Forest canopy target demanding a wide treed boulevard colliding with utility setbacks AND a cycle track AND fire clear width — render "trees win" vs. "utilities + fire win," so Parks, Roads, Fire, and Urban Forestry see the same picture in one room.
- **Risk:** requires *accurate* composite sections with real department minimums — get the numbers wrong and you lose the engineers you must convince.

### H. Standard-Faithful Public Hearing Pack — *effort: low*
One click → a small pack of photoreal renders (the standard on a representative site, the same in a second context, the key trade-off), each watermarked **"illustrative, not an approved design"** with C2PA provenance. Pure orchestration over the existing pipeline; adds the **municipal-deliverable layer no incumbent provides** and carries **no personal data** (sidesteps POPA's binding duties). Directly answers the PSS literature's "low communication value / analyst-vs-decision-maker divide" adoption killer.

**Sequencing:** A → B/F (SHOW + COMPARE wins) → H (packaging) → C (the differentiator, on the fire-vs-walkability wedge) → G → D (the moonshot).

---

## 6. The hard truths — the strongest objections (and how to answer)

A skeptical Calgary planning director will say:

1. **"Solution looking for a problem."** *(The single strongest objection.)* You've proven nobody *builds* it; you haven't shown anyone is *funded to want* "cross-policy contradiction surfacing." The documented pain is **circulations, coordination, approval timelines.** → **Answer:** reframe SURFACE as *"resolve a cross-department conflict in ONE meeting instead of three circulation cycles"* — a concrete ROI, not an abstract "see the contradiction." Then go validate it (§7).
2. **"Contradiction-flagging is a liability."** Plans are *deliberately discretionary* ("normally," "may," "will consider") so professional judgment can reconcile case-by-case; a tool that mechanically declares "Policy A contradicts Policy B" hands ammunition to appellants/NIMBYs/litigators under general-plan internal-consistency doctrine. → **Answer:** position as an internal *deliberation aid* (pre-decisional, FOIA-shielded where possible), never a public verdict; show *trade-offs to negotiate*, not *violations*.
3. **"Photoreal is exactly what we DON'T want in a hearing."** The 2024–26 literature documents photoreal renders triggering *emotional over analytical* responses and misleading non-experts ("visual greenwashing"); a real case saw >15% redesign costs because a render overstated building separation. → **Answer:** pair every photoreal image with the **to-scale diagram + numeric metrics it was conditioned on** + C2PA provenance + "illustrative" label. Turn the critique into a *designed safeguard* and a trust differentiator vs. ArchiVinci-class tools.
4. **"Hallucination is disqualifying for government."** Diffusion hallucinates geometry even with conditioning — and *your own* FLUX-depth pilot was the worst result and was reverted. → **Answer:** scope SURFACE to **inherently-spatial, already-numeric** conflicts where the geometry is the standard (fire width vs. cycle width), not prose; build a held-out **accuracy benchmark** (precision/recall on human-verified renders) before any post-pilot sale.
5. **"Incumbents close this in 18 months."** Esri has a CityEngine→GenAI photoreal prototype + 2026 photoreal roadmap + Canadian data centres + your procurement relationship; **UrbanLogiq** already sells a Canadian, data-resident gov AI twin. → **Answer:** move fast on the fusion; consider positioning as the **rendering+contradiction layer *on top of* an Esri/UrbanLogiq data twin** rather than head-to-head.
6. **"We can't procure or sustain it."** Municipalities rank privacy #1 and cite insufficient resources (50%) / complicated decisions (44%); govtech tools die when 1–2 people own the data ("one resignation away from collapse"); PSS has a 30-year implementation-gap track record. *Who maintains the versioned policy corpus through the Calgary Plan, the repealed rezoning, the new Street Manual?* → **Answer:** keep the corpus *thin and street-design-scoped* at first (Street Manual + Complete Streets + CSPS033), not "all 114 council policies"; price a small pilot; name an internal champion.
7. **"You're betting on a moving foundation."** The Calgary Plan (your before/after anchor) was just delayed with a councillor moving to abandon it; blanket rezoning was repealed; the Street Manual isn't final until Q4 2026. → **Answer:** anchor on the **stable, numeric, already-spatial** layers (1P2007 open data, Street Manual cross-sections, LAP scale maps), not the contested strategic plans.
8. **"Data residency isn't your moat."** No fully Canada-resident image API exists mid-2026; your governance argument is "no personal data + documented data-flow clears the gate like Copilot did." So residency is a *checklist item a competitor can also pass* — and UrbanLogiq already exceeds it. → **Answer:** don't *sell* residency as the moat; treat it as table stakes you've cleared (PIA template + pluggable model layer to swap to a Canadian image model when one ships). The moat is the fusion.

---

## 7. Recommended path

**Phase 0 — Demand discovery (the missing step; do this before building SURFACE).** 3–5 structured conversations: a Calgary planner, a transportation engineer, the **CSPS033 / fire-EMS reviewer**, a parks/urban-forester, and — critically — a **consultant who presents to councils** (consultants, not city staff, are often the real makers of development visualizations, and may be the faster first buyer). Test one question: *is "resolve a cross-department conflict in one meeting" something they're funded to want, and would they pay to remove a circulation cycle?*

**Phase 1 — Ship SHOW + COMPARE (low risk, demoable now).** Concepts A, B, F, H. These reuse the existing pipeline, carry no personal data, and produce council-ready deliverables. This is the wedge that gets you in the room regardless of whether SURFACE pans out.

**Phase 2 — Prove SURFACE on ONE wedge.** Concept C on the **Street Manual cross-section vs. fire-apparatus clear width (CSPS033)** — the sharpest, most-renderable, *least-discretionary* conflict in Calgary. Build the conflicting-diagram pair with real engineering input; benchmark accuracy; frame as deliberation aid. *Only* after this lands do you generalize toward Concept D.

**Phase 3 — Governance kit (parallel).** PIA template, C2PA provenance on every render, "illustrative, not an approved design" legal posture, pluggable model layer. No personal data = outside POPA's binding duties; the gate is an internal assessment (cleared for Copilot), not Canadian-soil residency.

---

## 8. Open questions / next research

- **Demand:** Calgary-specific circulation/review-cycle metrics — how many resubmissions, how long, what's the cost of a circulation? (This is the ROI denominator.)
- **Competitive deep-dive:** **UrbanLogiq** (Vancouver) and **Esri Canada** — what they can/can't do *today* on photoreal policy rendering + cross-discipline conflict; is City Prompt better as a **complement/partner** (the render layer on their twin) than a challenger?
- **Procurement vehicle:** sole-source innovation pilot vs. smart-city grant vs. RFPQ piggyback — which gets a $25–100k pilot past Calgary's multi-department risk assessment?
- **Accuracy eval:** build a held-out benchmark of human-verified policy renders / known contradictions so precision/recall is *measurable and reportable* — a hard buying criterion past pilot stage.
- **Defensibility architecture:** what makes an AI output FOIA-defensible for a Canadian municipality — the provenance chain *policy clause → diagram → render* + audit log.
- **Comparable-failure base rate:** apply the **Sidewalk Labs Toronto** cautionary tale (killed partly by data-governance + public-trust backlash) and the PSS implementation gap as *risks to City Prompt itself*, not just competitor weaknesses.

---

## 9. Key sources (curated; full 263-URL set in the workflow transcript)

**Calgary policy stack & conflicts**
- MDP (LUP009): https://www.calgary.ca/content/dam/www/ca/city-clerks/documents/council-policy-library/lup009-municipal-development-plan.pdf
- Land Use Bylaw 1P2007 + open data: https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html · https://data.calgary.ca/Base-Maps/Land-Use-Districts/mw9j-jik5
- Blanket rezoning repeal (Apr 8 2026): https://livewirecalgary.com/2026/04/08/calgary-city-council-repeal-citywide-blanket-rezoning/ · https://newsroom.calgary.ca/council-approves-repeal-of-blanket-rezoning-land-use-bylaw-1p2007-amendments-implementing-citywide-residential-rezoning/
- The Calgary Plan (delayed): https://www.calgary.ca/planning/city-building-program/city-building-program/the-calgary-plan.html · https://livewirecalgary.com/2025/02/12/the-calgary-plan-officially-postponed-until-sometime-in-2026/
- Street Manual: https://www.calgary.ca/planning/city-building-program/city-building-program/the-street-manual.html
- LAP Building Scale / Guidebook: https://www.calgary.ca/planning/local-area/resources.html
- CSPS033 Integration of Emergency Services: https://www.calgary.ca/content/dam/www/ca/city-clerks/documents/council-policy-library/csps033-integration-of-emergency-services.pdf
- Bike lanes province-vs-city: https://www.cbc.ca/news/canada/calgary/calgary-mayor-alberta-minister-to-discuss-bike-lanes-as-threats-of-removal-loom-1.7596308
- Urban Forest Strategic Plan (canopy 8.25→16%): https://www.calgary.ca/content/dam/www/programs-services/parks-recreation/parks/natural-parks-and-wetlands/urban-forestry-strategic-plan.pdf
- Wetland conservation: https://www.calgary.ca/content/dam/www/uep/water/documents/water-documents/wetland-conservation-plan.pdf
- Plus-15: https://en.wikipedia.org/wiki/Plus_15

**Rules as Code / contradiction NLP**
- NZ Better Rules: https://serviceinnovationlab.github.io/projects/legislation-as-code/ · OECD OPSI: https://oecd-opsi.org/publications/cracking-the-code/ · OpenFisca: https://openfisca.org/en/
- Georgetown Policy2Code: https://digitalgovernmenthub.org/publications/ai-powered-rules-as-code-experiments-with-public-benefits-policy/
- Singapore CORENET X (spatial rules-as-code, mandatory Oct 2026): https://info.corenet.gov.sg/overview/about-corenet-x/overview-of-corenet-x
- LegalWiz (contradiction detection): https://arxiv.org/pdf/2510.03418 · AI-Zoning (Milo/Gupta): https://github.com/dmilo75/ai-zoning
- Rules-as-Code for planning (Canada): https://wellurban.ca/2025/10/25/the-new-frontier-for-canadian-cities/

**Zoning-as-data / twins / generative**
- Esri ArcGIS Urban: https://www.esri.com/en-us/arcgis/products/arcgis-urban/overview · CityEngine: https://doc.arcgis.com/en/cityengine/latest/get-started/get-started-about-cityengine.htm
- Symbium (surfaced a contradiction): https://www.govtech.com/biz/symbium-opens-service-for-analyzing-zoning-building-codes.html
- Archistar (gov + AI PreCheck): https://www.archistar.ai/for-government-town-planners/
- Gridics: https://gridics.com/government-solutions/ · Zoneomics: https://www.zoneomics.com/product/api · TestFit: https://www.testfit.io/product/site-solver
- Autodesk Forma + Zoneomics: https://blogs.autodesk.com/forma/2024/08/19/autodesk-and-zoneomics-partner-to-bring-zoning-responsive-building-envelopes-to-forma/
- Boston BPDA twin: https://www.esri.com/about/newsroom/blog/3d-gis-boston-digital-twin · Virtual Singapore: https://en.wikipedia.org/wiki/Virtual_Singapore
- UK CReDo: https://cp.catapult.org.uk/project/climate-resilience-demonstrator-credo/ · MIT CityScope: https://www.media.mit.edu/projects/cityscope/overview/
- GIS-LLM planning (Esri EuclidHL): https://www.esri.com/about/newsroom/arcnews/gis-based-large-language-model-answers-city-planning-questions · MIT Senseable LLM-planning: https://senseable.mit.edu/papers/pdf/20250908_Zheng-etal_UrbanPlanningLLM_NatureComputatinoalScience.pdf
- 3DStreet (closest analogue): https://www.3dstreet.com/ · AIRIlab: https://airilab.com/blog/future-of-urban-planning-ai-zoning-visualizations
- Sidewalk Labs Delve (now in Google Earth): https://developers.google.com/maps/documentation/earth/generate-designs

**Conflict framing / PSS / governance**
- LUCIS: https://atlas.co/gis-use-cases/land-use-conflict-identification-lucis-model/ · MSP ADRIPLAN conflict score: https://maritime-spatial-planning.ec.europa.eu/practices/adriplan-conflict-score-tool
- General-plan internal-consistency doctrine: https://lci.ca.gov/docs/OPR_C9_final.pdf · Fire-vs-walkable streets: https://blog.qrfs.com/172-how-walkable-streets-are-changing-fire-code-and-safety/
- OntoZoning (Singapore): https://www.sciencedirect.com/science/article/pii/S2226585623000067
- PSS adoption gap: https://www.researchgate.net/publication/226421122_Improving_the_Adoption_and_Use_of_Planning_Support_Systems_in_Practice
- Alberta POPA + AI: https://www.alberta.ca/system/files/popa-fact-sheet-ai-automated-systems.pdf · Calgary blocks ChatGPT: https://livewirecalgary.com/2026/02/10/city-of-calgary-blocks-chatgpt-use-on-city-devices-and-networks/
- Implications of AI for Municipal Governance (2025): https://ccg.eco/wp-content/uploads/2025/10/Implications-of-AI-for-Municipal-Governance.pdf

---
*Method note: 11 research dimensions, each adversarially fact-checked (claims marked confirmed/overstated/uncertain/refuted). The recurring verdict was that "nobody does X" is directionally true for the **fusion** but **overstated** for each **component** — the components are maturing fast. Treat the white space as a fast-closing window, not a permanent vacancy.*
