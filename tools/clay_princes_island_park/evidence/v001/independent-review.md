# Independent holistic review: Prince's Island Park clay, v001

Reviewer: independent RLASM v6.1 holistic reviewer (not the builder). Evidence used: the locked sources `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`, all 18 renders in `renders/` at full resolution, and the four phone boards in `boards/`. Zoomed crops were written to a new folder only (`/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/pisland-v001-review-crops-2185dc62/`). Builder metadata, evidence JSON and scripts were not used as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the plan, topology and every identity element are present and correctly placed, so there is no P0. However, five clearly visible fidelity defects block production-quality approval:
- the promenade's granite sett borders are missing;
- the plants read as crystals, spikes and rocks;
- the sedum roof reads as flagstones;
- the boardwalk railings read as solid barrier walls;
- the far bank is a bare strip, not woodland.

Counts: P0 = 0, P1 = 5, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|----------|---------|--------------------------------|--------------|------------|
| 1 | P1 | front, promenade_beds, bench_plaza, aerial, front_corner | The promenade and south plaza are one uniform pale slab colour. Where the sources show wide, flush bands of dark grey granite setts (edging both sides of the promenade, crossing it, and framing the south plaza in all three sources), the render has only narrow pale concrete ribs. These ribs stand proud of the slab, read as a trip kerb across the walking surface (front, foreground), and show as thin grey lines at aerial scale. No sett material or colour is distinguishable anywhere. | The sett border was modelled as a thin raised strip in the slab material, not as a flush band with its own material. | Model the sett borders as flush bands about 0.6–1.0 m wide, coplanar with the slabs, in a darker warm-grey sett material with a small-module joint pattern (or many small blocks). Run them along both promenade edges, across the cross-band junctions and round the south plaza, following the top view. Remove the raised ribs. |
| 2 | P1 | front, glazing_close, promenade_beds, west_path, front_corner, right_side | Ornamental grasses are rigid smooth single-tone cones up to roughly shrub height. Perennials are floating-looking octahedral "gems" on hair-thin stems, and shrubs are large faceted boulders. At pedestrian height (front foreground, glazing_close foreground) the beds read as conifer spikes, crystals and green rocks, not as soft grass drifts with pink, lavender and white flowers. The flower colour mass that dominates the oblique and top sources (pink and lavender drifts, white umbels) is reduced to sparse specks. This is well below the conservatory benchmark's "dense planting with varied height, colour and texture". | A single primitive per plant type, with no clump or blade structure; flower heads too few and too small in area. | Replace the cone grasses with tufted clumps: 8–15 thin tapered blades or a fan of narrow planes per clump, arching, in two or three straw-and-green tones, at 0.4–0.9 m. Replace the gem flowers with clustered heads (several small spheres or discs per stem, grouped into drifts of 5–15) in source pink, lavender and white. Reduce shrub facet size and scale so shrubs read as rounded mounds. Raise the flower-drift area to match the source beds. |
| 3 | P1 | green_roof, front_corner, aerial, right_side | The sedum roof is a smooth lawn-green plane strewn with raised pale polygonal plates and tiny spikes. From above and at 45 degrees it reads as flagstones or lily pads lying on a lawn, not as a continuous fine-textured ochre-and-green sedum mat (oblique and top sources). | Coarse low-poly "clump" plates scattered with sparse density on a flat plane. | Make the sedum a fine, dense, low (under 0.1 m) bumpy mat: many small mounds or displaced micro-relief across the whole roof in two or three blended ochre and olive tones, with no isolated pale plates. Keep the planted surface just below the fascia lip, as in the front source. |
| 4 | P1 | boardwalk, right_side, riprap_bank, rear_side, footbridge, front_corner | The boardwalk (and bridge) railings are continuous opaque grey sheet panels between dark posts. At eye level (boardwalk) they read as solid sound-barrier walls that block the view to the river and beds. The oblique source shows an open, see-through steel picket or mesh railing through which the deck edge, the planting and the water remain visible. | Infill modelled as a solid panel in an opaque mid-grey material. | Replace the panel infill with vertical bars at about 100–120 mm centres, or with a dark mesh carrier that has real openness (transmissive or alpha mesh). Keep a dark steel top rail, bottom rail and posts. Apply the same treatment to the footbridge railing. |
| 5 | P1 | top, footbridge, bench_plaza, left_side, front_corner | The far bank is a bare flat green strip carrying one straight row of five identical, evenly spaced lollipop trees and a line of pebbles. The oblique source shows the footbridge landing into a dense wooded far bank, and the front source shows a vegetated far shore. The bridge therefore lands on an empty lawn edge, and the river edge across the whole scene reads as unfinished. | The far bank was treated as minimal context, with a single repeated tree instance. | Fill the far bank opposite the bridge landing with a grove: about 15–25 trees of varied size and spacing in two or three depth rows, with an understorey mound band and a rip-rap or rocky toe. Keep it as context, but make it read as woodland in the footbridge, top and front_corner views. |
| 6 | P2 | front, bench_plaza | Black pinholes appear at slab-joint intersections in the paving. | The slab corner chamfer or gap exposes the void below. | Close the corner gaps, or place a joint-coloured base plane under the paving. |
| 7 | P2 | front, pavilion_close, porch_northwest, promenade_beds | The roof edge is a heavy dark fascia (about 0.35–0.4 m). The front source shows a thin dark metal edge over a separate light timber beam band, a planted lip visible at the edge, and a slight mono-pitch rather than a dead-flat roof. | Single fascia box with no beam layer. | Thin the metal fascia to about 0.12–0.15 m, add a timber beam band below it, and optionally a slight fall. |
| 8 | P2 | pavilion_close, front | The south-west face carries only a door, one 2×2 window and corner glazing. The front source additionally shows a continuous clerestory band and a larger full-height glazed bay. The oblique source and the brief support the render's lighter reading, so the sources conflict and this is not a blocker. | Sources conflict. | Optionally add a slim clerestory band under the beam on the south-west face. |
| 9 | P2 | pavilion_close, glazing_close | The batten stubs over the window heads read as a dentil row. | Battens cut at the header without the board break being visible. | Add a header trim board, or run the battens behind a head flashing. |
| 10 | P2 | porch_northwest | A diagonal timber brace runs from the porch post to the wall. It appears in no source. | Extra structural member. | Remove it, or replace it with a horizontal beam tie. |
| 11 | P2 | footbridge | A black slit runs along the deck-to-edge-beam seam at the near landing. The near-end abutment wedge is crude. | Cambered deck and edge beam not coincident. | Weld or align the edge beam to the deck camber, and dress the abutment as a stepped wall. |
| 12 | P2 | riprap_bank, right_side, top | The rip-rap is near-white, uniform-sized faceted stones. The sources show grey-brown rounded boulders of mixed size with grass tufts between them. The rip-rap is currently brighter than the paving, which inverts the material hierarchy. | Single stone primitive and a light material. | Darken to grey-brown, vary size by 2–3×, round the stones, and seed grass clumps between them. |
| 13 | P2 | rear | The pavilion is mostly hidden behind the north grove. The park itself is legible. | The camera is low behind the grove. | Raise the camera or shift it slightly so the roof reads over the trees. |
| 14 | P2 | (provenance note) | The brief's detail list names facade_close, architecture_close and glass_close, which are not in renders/. The delivered set is 18 views, matching the brief's stated count, and pavilion_close and glazing_close cover the same faces. | Brief template names do not match the camera roster. | Align the brief or roster names in the next version. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|------|--------|--------------|
| Plan: pavilion position and rotation (about 27° off the river line) | conforms | aerial, top vs top source |
| Plan: promenade along the south-west face, south plaza to north-west, west cross-band | conforms | aerial, top |
| Plan: narrow slab paths to the porch and north to the footbridge landing | conforms | aerial, top, rear_side |
| Plan: two cycle paths, the eastern one rising onto the boardwalk | conforms | aerial, front_corner |
| Plan: lens beds between the paths | conforms (shape and placement) | aerial |
| Plan: groves north of the pavilion and along the boardwalk; south plaza trees | conforms | aerial, left_side, right_side |
| Plan: boardwalk, bank and river on the east | conforms | aerial, top |
| Pavilion: green roof | deviates (reads as flagstones, P1 #3) | green_roof, front_corner, aerial |
| Pavilion: thin dark metal fascia | deviates (heavy, no timber beam band, P2 #7) | pavilion_close, front |
| Pavilion: cedar board-and-batten cladding | conforms | pavilion_close, porch_northwest |
| Pavilion: glazed south-east face, dark mullions | conforms | glazing_close, front_corner |
| Pavilion: south-west door and corner glazing | conforms to the brief and oblique; lighter than front source (P2 #8) | pavilion_close, front |
| Pavilion: north-west porch with two doors | conforms | porch_northwest, promenade_beds |
| Pavilion: north-east clerestory | conforms | riprap_bank |
| Pavilion: corner posts | conforms (extra brace, P2 #10) | front, porch_northwest |
| Pavilion: interior long table | conforms | glazing_close, pavilion_close |
| Promenade: pale slabs and joints | conforms (pinholes, P2 #6) | front, bench_plaza |
| Promenade: granite sett borders | deviates (absent, raised ribs, P1 #1) | front, promenade_beds, aerial |
| South plaza and kerbed tree pits | conforms (pits); plaza sett framing missing | front_corner, aerial |
| Cycle paths: asphalt, yellow dashes, flush pale edges | conforms | west_path, bench_plaza, front_corner |
| Boardwalk: deck and ramp rise | conforms | boardwalk, right_side, front_corner |
| Boardwalk: kerbs | conforms | front_corner |
| Boardwalk: railings on both sides | present; deviates in material and openness (P1 #4) | boardwalk, right_side |
| Rip-rap and bank grasses | deviates mildly (colour, uniformity, sparse grasses, P2 #12) | riprap_bank, right_side |
| River | conforms (flat water, correct side) | top, right_side |
| Planting beds: kerbs | conforms (kerbs slightly proud) | promenade_beds, front |
| Planting beds: grasses, shrubs, flowers | deviates (primitive forms, low flower mass, P1 #2) | front, glazing_close, west_path |
| Trees: rounded deciduous | conforms (low-poly crowns, acceptable for clay) | left_side, boardwalk |
| Benches (timber on dark steel) and corten bins | conforms | bench_plaza, front, front_corner |
| Footbridge: cambered deck and two piers | conforms | footbridge, rear_side |
| Footbridge: abutments and landings | conforms; crude near abutment and seam (P2 #11) | footbridge, rear_side |
| Footbridge: railings | deviates (solid panels, P1 #4) | footbridge |
| Far bank | deviates (not wooded, P1 #5) | top, footbridge |
| Materials hierarchy | deviates (no sett material; rip-rap brighter than paving) | front, riprap_bank |
| Aerial finish against the park benchmark | partially conforms: the plan is legible and authored, and the pavilion is a clear focal point. The roof texture and missing sett bands weaken it. | aerial, front_corner |
| Pedestrian-scale finish against the park benchmark | deviates: planting, railing and paving detail do not hold up at eye level. | front, promenade_beds, boardwalk, glazing_close |

## 4. Camera validity

- All 18 views render a legible target, with no clipping of the asset and no camera inside geometry.
- In the rear view, the pavilion is largely occluded by the north grove (P2 #13). The view stays valid as a park envelope view because the lawn, paths, grove and cycle path are legible.
- The front view frames the pavilion more frontally than the source front, and it omits the bench, the cycle path and the boardwalk from the frame. Its role match is acceptable: the porch is on the left, the glazing on the right, and the railing and river at the right edge.
- The top and aerial views frame the whole board and the plan reads correctly.

## 5. Previous-version findings

This is the first version (v001). There are no previous-version findings to carry forward or close.
