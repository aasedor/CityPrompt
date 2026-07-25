# Overnight Batch — 25 Archetype Additions (2026-04-29)

This is the morning summary for the overnight Option B batch you greenlit before bed.

## Tonight's deliverables

**24 new archetypes added** + 1 piloted earlier (Beer Garden, retroactively patched with per-variant area metadata) = **25 archetypes touched**.

| Category | Existing | Added | New total |
|---|---:|---:|---:|
| Civic Plazas | 7 | 5 | 12 |
| Landscape Parks | 2 | 8 | 10 |
| Social / Event Spaces | 4 | 5 + 1 (Beer Garden) | 10 |
| Waterfront Spaces | 4 | 6 | 10 |
| **Total openspace catalog** | 104 | **+25** | **129** |

For each new archetype:

- **Rich JSON metadata** — 6-element evocative `landscapeCharacter` prose (~700 chars), per-variant differentiated descriptions naming real-world precedents, full `prompt.subject` + `prompt.details`, `renderPrompt.mapOverlay` + `roofView`.
- **Layer 1 polygon-scale defenses** — 4 variants spanning 5–20× scale, V3 sized at archetype max so the picker has a "biggest plausible variant" for borderline-overshoot polygons. Per-variant `minAreaSqm` / `maxAreaSqm` / `suggestedAreaSqm` populated on every variant.
- **Architecturally accurate references** — variants name specific real-world precedents (Tanglewood, Robson Square, Buttes-Chaumont, Plus-Pool, Granville Island, Sultan Ahmed, etc.) so Gemini and GPT image models hit the right typology priors.
- **Style 6 cards** — Gemini 3.1 Flash Image, temp 0.7, with `PEOPLE_CAMERA_SUFFIX` (Kodak Portra 400 / 35mm SLR / f/5.6) and per-archetype activity-people snippets (added to `PILOT_ACTIVITY_PEOPLE` in `scripts/_pilot_generate_one_archetype.py`).
- **60° steep-oblique aerial refs** — drone-altitude oblique drone photo, surrounding context.
- **90° true-nadir aerial refs** — orthographic top-down, fixed prompt (`_NADIR_TAIL` + dropped contradictory altitude in `FIDELITY_BLOCK_OPEN_SPACE`) so V3 rooftops and other context-rich archetypes now read correctly as flat satellite views.

**~300 images generated** (25 × 12) plus the JSON metadata.

## What's worth eyeballing first

Each row below has folder paths so you can browse with your file viewer. Names of tools / precedents in *italics* signal which real archetype each variant emulates.

### Civic Plazas (5 new)

| Archetype | Variants spanning |
|---|---|
| **City Hall / Government Plaza** | *Compact contemporary* → *Helsinki Senate* → *Toronto Nathan Phillips* → *Boston City Hall* (5.2× scale) |
| **Sunken Plaza** | *Intimate Eu courtyard* → *Rockefeller* → *Embarcadero* → *Asian transit-integrated* (6.9×) |
| **Cathedral / Religious Forecourt** | *Asian temple* → *French Gothic parvis* → *San Marco basilica* → *Sultan Ahmed mosque* (14.7×) |
| **Cultural Institution Forecourt** | *Tate Modern* → *NYPL Beaux-Arts* → *Lincoln Center* → *Wembley Way* (6.5×) |
| **Stepped / Terraced Plaza** | *Aegean village* → *Spanish Steps* → *Federation Square* → *Robson Square* (10.7×) |

Image dirs at `frontend/public/archetypes/openspaces/{city-hall-government-plaza, sunken-plaza, cathedral-religious-forecourt, cultural-institution-forecourt, stepped-terraced-plaza}/`.

### Landscape Parks (8 new)

| Archetype | Variants spanning |
|---|---|
| **Picturesque / Olmsted Park** | *Hampstead Heath* → *Mount Royal* → *Prospect Park* → *Central Park* (8.3×) |
| **Reclaimed Industrial Park** | *Domino Sugar Refinery* → *Gas Works Seattle* → *Zollverein* → *Landschaftspark Duisburg* (16.2×) |
| **Quarry / Sunken Garden Park** | *Vigeland bowl* → *Calgary Quarry* → *Limestone tier* → *Butchart* (6.4×) |
| **Hilltop Topographic Park** | *Mediterranean cypress hill* → *Telegraph Hill* → *Buttes-Chaumont* → *Pacific terraced viewpoint* (7.2×) |
| **Estate Picnic Grove** | *Pine-shaded creekside* → *Wide oak grove* → *Open meadow + pavilion* → *Regional picnic plain* (9.4×) |
| **Reservoir / Watershed Park** | *Concrete-edge utility* → *Stone-banked urban (CP reservoir)* → *Forested upland* → *Earthen-dam recreation* (20×) |
| **Greenbelt Buffer Park** | *Suburban wide-lawn* → *Forested rail-trail* → *Agricultural hedgerow* → *Active-recreation spine* (10×) |
| **Foothill Trail Park** | *California sage-scrub* → *Australian eucalyptus* → *UK heathland moor* → *Alpine larch ridge* (10×) |

### Social / Event Spaces (5 new)

| Archetype | Variants spanning |
|---|---|
| **Concert Pavilion Lawn** | *Forest Hills* → *Modern wave canopy* → *Tanglewood timber shed* → *Hollywood Bowl* (7.5×) |
| **Food-Truck Plaza** | *Industrial pop-up* → *Permanent food-truck park* → *Adaptive parking-lot* → *Night-market truck plaza* (6.5×) |
| **Outdoor Cinema Lawn** | *Pop-up festival* → *Park-lawn projection* → *Drive-in heritage* → *Rooftop cinema* (2.8×) |
| **Night Market** | *Asian hawker* → *European Christmas-market* → *Latin-American night plaza* → *Modern food hall* (7.1×) |
| **Parade Ground** | *Stadium-fronted civic* → *London Mall gravel allée* → *Champ-de-Mars* → *National Mall* (15×) |

### Waterfront Spaces (6 new)

| Archetype | Variants spanning |
|---|---|
| **Marina / Yacht Harbor** | *Inland-lake recreational* → *Working fishing-harbour* → *Pacific floating-dock* → *Mediterranean superyacht* (11×) |
| **Working Pier / Wharf Conversion** | *Granville Island* → *Pier 39* → *Industrial loading-pier adaptive* → *Brooklyn Bridge Park pier* (6×) |
| **Floating Park / Pool** | *Plus-Pool swim basin* → *Copenhagen Harbour Bath* → *Floating boardwalk meadow* → *Little Island* (7.5×) |
| **Lighthouse Point Park** | *Cape rocky-headland* → *Atlantic dune-point* → *Pacific cliff promontory* → *Mediterranean fortress lighthouse* (4.8×) |
| **Tidal Marsh Boardwalk** | *Cordgrass salt-marsh* → *Mangrove tidal-flat* → *Reedbed estuary* → *Bird-blind viewing circuit* (6.7×) |
| **Lake Edge Plaza** | *Como stone terrace* → *Geneva quayside* → *Modern timber lakefront* → *Chicago lakefront* (16×) |

## Pipeline notes

- **Generator scripts** (composers): `scripts/_compose_new_civic_plazas.py`, `_compose_new_landscape_parks.py`, `_compose_new_social_event.py`, `_compose_new_waterfront.py` — each emits a JSON-valid snippet that gets text-spliced into `frontend/src/data/openSpaceArchetypes.json` (no `json.dump` of the catalog per `feedback_json_dump.md`).
- **Pilot runner**: `scripts/_pilot_generate_one_archetype.py` — refactored to use Style 6 from `generate_card_images.py` after the V1 Beer Garden pilot showed the older `generate_park_street_variants.py` produced visibly worse output. Memory written: `feedback_style6_card_pipeline.md`.
- **Aerial generator**: `scripts/generate_corner_aerials.py` — fixed two prompt bugs at angle=90 tonight: (1) `FIDELITY_BLOCK_OPEN_SPACE` no longer hardcodes "80 meters"; (2) added `_NADIR_TAIL` block as final critical constraint per CLAUDE.md "critical constraints go at end". Both committed to fix the V3 Beer Garden rooftop oblique-drift problem and propagated through tonight's batch.
- **No hero.png** — per `feedback_no_hero_image.md`, all new archetypes' `arch.thumbnailUrl` points directly at `variant_0.png`. UI only has 4 variant slots.
- **Slug fixes**: Two title-vs-slug mismatches caught and fixed during the run — `parade-ground` (title "Parade / Procession Ground" → slugified to "parade-procession-ground" by the generator; renamed to match JSON), and `lighthouse-point-park` (same issue with "Lighthouse Point / Headland Park"). Worth a follow-up: align all `slug` parameters in the composer scripts with `_slugify(title)` to prevent repeats.

## Known issue — full buildings rendering inside 4 plaza archetypes (deferred)

User flagged during morning review that 4 of the new plaza archetypes render the *fronting institutional building* as the dominant foreground subject inside the plaza zone, when the user actually wants only the plaza itself (with the building as a separate building-zone if desired). Affected archetypes (16 variants total):

- **Cathedral / Religious Forecourt** — all 4 variants render cathedral / basilica / mosque / temple
- **Cultural Institution Forecourt** — all 4 variants render museum / library / concert hall / stadium
- **City Hall / Government Plaza** — all 4 variants render the city hall as foreground monument
- **Parade / Procession Ground** — all 4 variants render the monumental termination (capitol, palace, obelisk, arch)

**Fix plan** (deferred to a follow-up session):
1. Rewrite each variant's `description`, `landscapeCharacter`, `prompt.subject`, `prompt.details`, and `renderPrompt.mapOverlay` so the plaza/forecourt itself is the only subject. The institutional building should be referenced verbally as "fronts onto a [type] not visible in this frame" — implied, not rendered.
2. Re-render the 16 variant cards + 32 aerials (60° + 90°). Cost ~$2, ~10 min.
3. Validate: drawing a Cathedral Forecourt zone alone should produce just paved square + statue / fountain / arcade with the cathedral implied at one edge but not rendered as a foreground monument.

In the meantime, the 4 archetypes remain usable — users can either accept the bundled-building output, or draw a separate building zone alongside to override the plaza zone's render.

Memory: `feedback_archetype_building_bleed.md` written for the follow-up.

## Multi-ref tiling fix (deferred)

Per the conversation before bed: render-time multi-ref tiling fix (the third polygon-size mitigation layer) was scoped as a separate follow-up after generation, not bundled into tonight's run. Untouched. Still ~30 min of work in `useAIRender.ts` / `useGlobeAIRender.ts` when you're ready.

## Rooftop / sunken / floating placement awareness (deferred)

You raised this midway through the run. Currently SiteForge has **no rooftop-aware placement logic** — every drawn polygon is treated as a flat ground footprint regardless of what's underneath. Rooftop variants in the new batch (`beer_garden_v3` Rooftop, `outdoor_cinema_lawn_v3` Rooftop Cinema Terrace) and the inherently-elevated archetypes (`sunken_plaza` below-grade, `floating_park_pool` on water) only render correctly when the user happens to draw the polygon over a building rooftop / harbour edge AND mask context cooperates with Gemini.

**Recommended fix**: add a `placement: "ground" | "rooftop" | "sunken" | "floating"` field on variants, plus polygon-to-building hit-testing in the picker (Mapbox building extrusion data on 2D, Three.js raycaster against Google 3D Tiles on globe). Filter the picker so rooftop variants only show when the polygon is over a building, sunken when below grade, floating when over water; auto-inject placement context into the `mapOverlay` prompt. ~30 min of frontend + backend work once the building-context detection is wired.

Memory written: `project_rooftop_subsurface_placements.md`. Standalone follow-up — independent of the multi-ref tiling fix above. Doesn't block anything in the catalog tonight; the rooftop variants are correct by their own internal data, just not auto-routed by the picker.

## Costs

| Step | Calls | Approx cost |
|---|---:|---:|
| Variant cards (24 new × 4 + Beer Garden retake earlier) | ~100 | $4 |
| 60° aerials (24 × 4) | 96 | $4 |
| 90° aerials (24 × 4 + Beer Garden retakes) | 100 | $4 |
| **Total** | ~300 | **~$12** |

Within the $11–12 estimate I gave you.
