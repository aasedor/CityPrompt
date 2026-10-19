# Independent holistic review: clay-calgary-riverwalk v003 (RLASM v6.1 architectural clay)

Reviewer: independent; judged from rendered pixels against the three locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg) only. All 18 renders were opened at full resolution, along with the four phone boards. Zoomed crops were written only to the new folder /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/crops-rv3-1840413757/.

## 1. Verdict

**PASS_ZERO_P0_P1**: the full river-to-blocks section reads in the right order in every whole-envelope view. Both v002 P1s are gone in the pixels: right_side now frames the section from over the river, and the window crossings are clean. Every v001 fix still holds. What remains is polish only.

Counts: P0 = 0, P1 = 0, P2 = 6

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | glass_close, architecture_close, front, planters_benches | Balcony glass guards run only along the outer edge of each slab. In the oblique close views the slab's side end has no glass above it (glass_close: the left balcony's guard stops at x≈230 while the slab runs on to x≈385; front: the guard covers about half of the visible slab length). Balcony floors also sit about 0.5 m below the sills of the windows behind them, so no door serves them. | Guard panel modelled as a single front plane with no side returns; balconies placed on the window grid rather than on door openings | Add side-return glass panels flush with each slab end, and either drop the sill of the window behind each balcony to floor level as a door or shift the balconies onto door bays |
| 2 | P2 | peace_bridge, top, aerial | The far bank is a flat olive slab with about six isolated trees and a few loose pebbles at the water line. The source top and oblique show a densely wooded far bank with its own rip-rap edge and a path. | Far bank kept as minimal context | Add a continuous rip-rap toe on the far bank and two or three canopy clusters (8 to 12 more trees) near the bridge landing |
| 3 | P2 | planters_benches, architecture_close, front | The gabion walls read as smooth pale-grey blocks with a brown grid, the same hue family as the bronze rails and timber benches. They look more like tiled blocks with a timber trellis than wire cages filled with stone. | Gabion wire assigned the rail/timber material | Give the gabion grid a neutral grey steel tone, and optionally facet the fill into coarse stone blocks |
| 4 | P2 | front_corner | The large cottonwood canopies along the riparian strip cover most of the promenade and the river rail in the oblique-matched view. The promenade only shows in a strip at the lower right (benches and lamps visible). In the source oblique the promenade reads as a continuous pale band. | Camera azimuth and height versus canopy diameter | Raise or rotate the front_corner camera slightly toward the land side, or trim the near two canopies by 15 to 20% |
| 5 | P2 | riprap_bank, left_side, right_side | A continuous near-black band runs along the waterline under the boulders and widens to the right in riprap_bank. It reads as a seam or plinth rather than rock entering water. | Vertical face of the bank or toe slab shaded dark above the water plane | Sink the toe below the water plane or tint it to the boulder grey, and let the lowest course of boulders cut into the water |
| 6 | P2 | rear, rear_north | The lower 25 to 30% of each frame is empty grey ground in front of the section cut. The section itself is fully legible. | Camera target set at the section base | Lower the camera pitch slightly or crop the ground plane (raise the target about 1 m) |

No P0 or P1 findings.

## 3. Source conformance checklist

| Item | Status | View(s) used | Note |
|---|---|---|---|
| Section order (river, rip-rap, planting, rail, promenade, edge, blocks) | conforms | top, aerial, right_side, rear_north | The order matches source top from water to blocks |
| Band widths | conforms | top, aerial | The rip-rap, riparian, promenade and edge bands are roughly equal and close to the source proportions. Source riparian is slightly wider than its rip-rap, which is acceptable at concept scale |
| River | conforms | top, right_side, peace_bridge | Blue-green flat water, wide channel |
| Rip-rap | conforms | riprap_bank, left_side, aerial_section | Packed, faceted grey boulders on a slope; dark toe band noted (P2 #5) |
| Riparian grasses | conforms | river_railing, rear_north | Continuous cover of pale and green grass cones over a straw ground |
| Shrubs | conforms | riprap_bank, promenade_section | Continuous low-poly shrub masses |
| Cottonwoods | conforms | front, aerial_section, right_side | A tall-trunked line of riparian trees between the rip-rap and the rail |
| Handrail | conforms | river_railing, front | Slender two-rail bronze handrail on low posts with base plates along the promenade edge. It is darker bronze than the benches. It opens at the bridge landing (top) |
| Promenade surface and joints | conforms | promenade_section, facade_close, architecture_close | Wide pale concrete with scored joints and no base slot |
| Planters | conforms | planters_benches, architecture_close | Stone-faced raised planters (block coursing) with soil, shrubs and bronze top rails |
| Gabions | deviates (minor) | planters_benches | Present and in the right place; brown grid and smooth fill (P2 #3) |
| Benches | conforms | planters_benches, front | Timber benches with backs, legs on the paving, set against the planters |
| Edge trees | conforms | facade_close, planters_benches | Small round-canopy trees in planters on the building edge |
| Lamps | conforms | facade_close, aerial | Regular pedestrian lamps on plinths along the building edge |
| Blocks and patios | conforms (minor deviation) | left_side, rear_side, front_corner, rear | Pale mid-rise blocks with window reveals, clean mullions, glass-guard balconies, and fenced ground-floor patio strips. End and rear faces are present. Balcony guard returns and access are noted (P2 #1) |
| Peace Bridge: truss | conforms | peace_bridge, rear_side | Red diagonal helical lattice tube with a white canopy and deck |
| Peace Bridge: deck | conforms | peace_bridge, rear | Continuous white deck through the tube, with a low arch |
| Peace Bridge: landing | conforms | top, rear, rear_north | Lands at promenade level on a paved landing that cuts through the riparian strip, with an opening in the river rail; the far end lands on a pad on the far bank |
| Far bank | deviates (minor) | peace_bridge, top | Present but sparse; not the wooded bank in the sources (P2 #2) |
| Materials hierarchy | conforms | all | Teal water, grey rock, straw and green planting, bronze rails darker than tan timber, pale concrete, cream blocks, red bridge. The only clash is the gabion grid (P2 #3) |

## 4. Camera validity

- front, facade_close, river_railing, promenade_section, architecture_close, planters_benches: valid. The promenade, rail, planters and benches are legible, and the bridge reads in the background.
- front_corner: valid but the promenade is partly occluded by canopies (P2 #4). The river, rip-rap, riparian strip, bridge, blocks and edge furniture are legible.
- aerial, aerial_section, top: valid, with the whole section and the bridge legible.
- left_side: valid, with the section framed from the river. The bridge is out of frame, which is acceptable for an elevation.
- right_side: valid. It is a raised three-quarter view from over the river looking up the section, and the river, rip-rap, riparian strip, rail, promenade, planters, benches, blocks and Peace Bridge all read. There is no large empty area.
- rear, rear_north: valid, with the section cut and bridge landing legible. The lower foreground is empty (P2 #6).
- rear_side: valid.
- glass_close, riprap_bank, peace_bridge: valid close views of their targets.
- No view has its target occluded, the asset clipped in a way that hides the target, or nothing legible.

## 5. Previous-version findings: resolved in the pixels?

| Previous finding | Status in v003 pixels | Evidence |
|---|---|---|
| v002 P1: right_side looked from the land side, blocks hid the section, about 60% empty frame | **Resolved** | right_side now looks from over the river toward the north-east. The river, rip-rap, riparian strip, rail, promenade, planters, benches, blocks and Peace Bridge all read, and the frame is filled. |
| v002 P1: opaque black square at every mullion/transom crossing | **Resolved** | 6x crops of glass_close crossings (crops-rv3-1840413757/g1.png, g2.png) show continuous light-grey bars with no dark square. architecture_close, planters_benches, facade_close and front crops show the same. |
| v002 P2: handrails same tone as benches | **Resolved** | river_railing, planters_benches and front show dark bronze rails that are clearly darker than the tan timber benches. |
| v001: bridge lands on an abutment at promenade level with an opening in the river rail | **Still fixed** | top crop (t1.png) shows the deck ending on a paved landing through the riparian strip with the rail stopping on both sides. rear and rear_north confirm it. |
| v001: lattice-tube bridge | **Still fixed** | peace_bridge, rear_side |
| v001: 6 m bands | **Still fixed** | top, aerial |
| v001: packed dark rip-rap | **Still fixed** | riprap_bank, left_side, aerial_section |
| v001: continuous riparian cover | **Still fixed** | promenade_section, river_railing, aerial |
| v001: planters with rails | **Still fixed** | planters_benches, architecture_close |
| v001: rear and end facades | **Still fixed** | rear_side, front_corner, right_side (end faces with windows) |
| v001: no slot at the promenade base | **Still fixed** | river_railing, promenade_section, rear_north section cut |
| v001: rear, left_side and rear_side framed on the section | **Still fixed** | rear, left_side, rear_side |
