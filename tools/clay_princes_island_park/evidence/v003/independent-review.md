# Independent holistic review — clay-princes-island-park v003 (RLASM v6.1)

Reviewer: independent; judged only rendered pixels against `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`.
All 18 renders in `renders/` and all four phone boards were opened at full resolution. Zoomed crops (read-only derivatives) were written to
`/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indep-review-v003-crops-c2d1d09f/`.
Note: the brief's render list names `facade_close`, `architecture_close` and `glass_close`; none exist. The 18 renders present are aerial, bench_plaza, boardwalk, footbridge, front, front_corner, glazing_close, green_roof, left_side, pavilion_close, porch_northwest, promenade_beds, rear, rear_side, right_side, riprap_bank, top and west_path. `glazing_close` and `pavilion_close` cover the pavilion close-ups.

## 1. Verdict

**VISUAL_REWORK_REQUIRED** — The boardwalk deck is now clear of boulders, but the planting beds still read as primitives at eye level. The flower heads are faceted pointed cones, not rounded heads. The grasses are flat, stiff straw strips, and bare flat bed fill shows between the mounds. This is the third failed fix of the planting finding.

Counts: P0 = 0, P1 = 1, P2 = 7

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, promenade_beds, west_path, bench_plaza, glazing_close, porch_northwest (aerial and front_corner acceptable at distance) | At pedestrian range the beds still read as primitives, against the locked front and oblique, where the beds are dense layered mounds with feathery plume grasses and white panicles and no bare fill. (a) **Flowers:** each perennial "head" is a 4–6-facet pointed cone or pyramid, like a lavender, pink or white crystal or tooth. They are not rounded. In promenade_beds (left bed) and front (left bed) they lie in loose scattered groups across the mound flanks. In west_path (right bed) and bench_plaza they sit on the flat bed fill beside the mounds, not crowning a leafy mound. The builder's claim that the "cone heads are gone" is false in the pixels. (b) **Grasses:** each clump is about 8–12 flat, untapered, stiff ribbon blades in straw or khaki with a little olive (front right foreground, promenade_beds, bench_plaza). There is no arching fountain, and no "low dark leafy base" can be told apart from the shrub mounds. They read as paper strips. (c) **Bed fill:** inside the kerb is a flat green plane with troughs between the mounds (west_path crop, promenade_beds left bed, front left bed). The groundcover "berm" does not read as planted. (d) **Shrubs:** smoother than v002, but polygon edges are still visible on the silhouette in promenade_beds (left bed, behind the grasses). Kerb clearance now holds: no mound passes through a kerb. | Flower heads are built from low-segment cones or icospheres with no subdivision or smoothing, and drifts are placed by scatter rather than snapped to mound crowns. Grass blades are single flat quads with no taper, curvature or droop, in a mostly straw palette. The groundcover berm is too low and smooth to break up the fill plane. | Make flower heads smooth rounded domes or umbels (subdivided spheres of 8 or more segments, flattened, with smooth shading), packed tightly and raycast onto the mound crown so none rest on fill. Rebuild grass blades as tapered, curved strips (3 or more segments, arch and tip droop), with 60% green, a gold accent and a dark leafy base visible from the side. Raise the groundcover into a continuous hummock layer that covers at least 85% of the visible fill at eye level. Verify against front, promenade_beds, west_path and bench_plaza crops before submitting. |
| 2 | P2 | riprap_bank, right_side, rear_side | The rip-rap reads as pale, hard-faceted hexagonal polyhedra. Bank grass between the stones is reduced to scattered single tufts (top source shows substantial green clumps among the stones). A flat dark apron strip runs at the waterline. | Low-segment boulder mesh; bank grass count cut from 90 to 70. | Add one subdivision level and smooth shading to boulders, warm the grey-brown slightly, and cluster the remaining bank grass into fewer, larger clumps. |
| 3 | P2 | boardwalk, footbridge, right_side, rear_side | Railings are pale grey-white open pickets. The sources show dark or mid-grey steel railings with infill. They are open, with no solid panels, so the earlier fix holds. | Railing material colour. | Darken the railing material toward the source steel grey. |
| 4 | P2 | green_roof, front, pavilion_close | The sedum reads as a continuous olive, ochre and rust camouflage decal with sparse cube nubs. At eye level (front) no sedum mat shows above the fascia, whereas the locked front shows the green mat cresting the fascia. | Roof planting is a flat patch texture flush with the fascia. | Raise the sedum surface slightly above the fascia line and add fine low tufts. |
| 5 | P2 | bench_plaza, front_corner | Benches are timber on dark steel legs but have no end armrests, while the locked front bench has them. | Simplified bench assembly. | Add end armrest frames. |
| 6 | P2 | footbridge, west_path, rear_side, rear | Hard model edges are visible: the river ends at a straight cut into grey void (footbridge, rear_side), and the lawn plinth edge shows against grey void (west_path). | Finite site plinth and camera framing. | Tighten framing or extend the plinth and ground skirt beyond the frame. |
| 7 | P2 | rear, footbridge (far bank), all wide views | Trees are repetitive low-poly blob clusters. The far-bank trees are lollipop crowns on bare poles. In rear, foreground crowns cover about half the frame and the pavilion shows only as a roof patch. | Shared low-poly tree kit; rear camera behind the north grove. | Vary crown scale and density; raise or retarget the rear camera so the pavilion reads. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Plan vs top: pavilion position and rotation (~27° off river) | conforms | aerial, top vs top.jpg |
| Plan: promenade from south plaza past SW face to NW, paved band crossing west | conforms | aerial, front_corner |
| Plan: two N–S cycle paths (eastern joins boardwalk) | conforms | aerial, top, front_corner |
| Plan: lens-shaped kerbed beds between paths | conforms | aerial, front_corner |
| Plan: groves north of pavilion and along boardwalk | conforms | aerial, left_side, rear |
| Plan: boardwalk along rip-rap bank, river on east | conforms | aerial, top, right_side |
| Pavilion: green (sedum) roof | conforms (P2: decal, flush with fascia) | green_roof, front_corner |
| Pavilion: thin dark metal fascia | conforms | pavilion_close, porch_northwest |
| Pavilion: cedar board-and-batten | conforms | pavilion_close, porch_northwest |
| Pavilion: fully glazed SE face, dark mullions, depth, long table inside | conforms | glazing_close |
| Pavilion: SW door and corner glazing | conforms | front, pavilion_close |
| Pavilion: open NW porch with two doors | conforms | porch_northwest |
| Pavilion: NE clerestory windows | conforms (seen from inside and in riprap_bank) | glazing_close, riprap_bank |
| Pavilion: slim timber posts at roof corners | conforms | front, green_roof, porch_northwest |
| Pavilion: interior | conforms | glazing_close, pavilion_close |
| Promenade: pale slabs with joints | conforms | front, promenade_beds, bench_plaza |
| Promenade: flush dark granite sett borders and crossing sett bands | conforms (earlier fix holds) | front, promenade_beds, pavilion_close |
| South plaza: sett frame | conforms | front_corner, aerial |
| South plaza: two trees in kerbed pits | conforms | front_corner, aerial |
| Cycle paths: asphalt, yellow dashed centre line, flush concrete edges | conforms | west_path, bench_plaza, front_corner |
| Boardwalk: raised concrete deck and kerbs | conforms; deck and both kerbs clear | boardwalk, right_side, rear_side |
| Boardwalk: railings on both sides, open | conforms in form; deviates in colour (P2) | boardwalk, right_side |
| Boardwalk: ramps and landings | conforms | rear_side, right_side |
| Rip-rap: grey-brown rounded stones with grass between | deviates slightly (faceted, sparse grass; P2) | riprap_bank, right_side |
| River | conforms (clay flat water) | right_side, rear_side, footbridge |
| Planting beds: kerbs | conforms (no mound through kerb) | front, promenade_beds, west_path |
| Planting beds: grasses | **deviates (P1)** — flat stiff straw ribbons | front, promenade_beds, bench_plaza |
| Planting beds: shrubs | conforms at distance; faceting still visible at eye level (part of P1) | promenade_beds, front |
| Planting beds: pink, lavender and white flowers | **deviates (P1)** — faceted cones, some on bare fill | promenade_beds, west_path, bench_plaza |
| Planting beds: fill and density | **deviates (P1)** at eye level; acceptable from aerial | front, west_path vs front_corner |
| Trees: rounded deciduous groves | conforms (P2 repetition) | left_side, boardwalk, rear |
| Benches (timber on dark steel) and corten bins | conforms (P2 no armrests) | bench_plaza, front, promenade_beds |
| Footbridge: cambered deck, two piers | conforms | footbridge, rear_side |
| Footbridge: abutments, landings, open railings | conforms | footbridge, rear_side, top |
| Far bank: wooded | conforms (earlier fix holds) | footbridge, top, left_side |
| Materials hierarchy (pale slab > dark sett > asphalt > cedar > green) | conforms | front, front_corner |
| Aerial-scale finish vs park benchmark | conforms | aerial, front_corner, left_side |
| Pedestrian-scale finish vs park benchmark (conservatory) | **deviates (P1)** — beds primitive at eye level | front, promenade_beds, west_path, bench_plaza |

## 4. Camera validity

- No view is invalid: in every render the target is in frame, unclipped and legible.
- rear: foreground grove crowns fill about half the frame and the pavilion is reduced to a roof patch. This is legible as the north grove, but weak for the pavilion (P2, #7).
- footbridge, rear_side, west_path: the model edge or grey void is visible at the frame edge (P2, #6). The target is still legible.
- glazing_close: grass blades enter the lower foreground but do not occlude the glazing.

## 5. Previous-version (v002) findings — status in pixels

1. **P1 rip-rap boulder tips through the boardwalk deck: RESOLVED.** In the boardwalk crop of the deck edge and east kerb, in the right_side deck crop and in the rear_side deck crop, no boulder or bank grass breaks the deck or either kerb. Boulders remain massed seaward along the open bank, with a narrow grass strip between the bank and the boardwalk.
2. **P1 beds read as primitives at pedestrian range: NOT RESOLVED** (third attempt). The flat flower sheets are gone and kerb intrusion is fixed. But the new flower heads are faceted pointed cones, the opposite of the claimed rounded heads, and some lie on bare fill rather than on mound crowns. Grass clumps are still stiff flat straw ribbons with no arch or distinguishable dark base. Flat bare fill and troughs still show between the mounds. Shrub faceting is reduced but still visible. See finding #1.

Earlier fixes that must still hold:
- Flush dark granite sett borders, sett bands crossing the promenade, and the sett frame round the south plaza: hold.
- Sedum roof as a continuous olive, ochre and rust mat: holds (P2 #4).
- Open picket railings on the boardwalk and footbridge, with no solid panels: hold.
- Wooded far bank round the footbridge landing: holds.
- Grey-brown rounded rip-rap with grass between the stones: holds marginally. The stones are more faceted and the grass sparser after the cut from 90 to 70 clumps (P2 #2).
- Plan, pavilion position and rotation, cedar pavilion with glazed SE face, promenade, cycle paths with yellow dashes, lens-shaped kerbed beds, raised boardwalk, footbridge on two piers, benches and corten bins: all hold.
