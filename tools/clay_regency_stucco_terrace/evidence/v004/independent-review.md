# Independent holistic review: clay-regency-stucco-terrace v004 (RLASM v6.1)

Reviewer: independent; did not build this candidate. Evidence used: the three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`), all 18 renders in `renders/` opened at full resolution, the four phone boards, and zoomed crops made from those same pixels (written only to the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/regency-v004-indrev-crops-b21e95f5/`). Metadata, the build report and the builder's notes were not used as proof.

Orientation as the pixels show it, consistent with the oblique and top sources: the end with the pediment faces the south street junction; the two long porch fronts face west and east; the brick terrace closes the north side.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: all four v003 P1s are fixed in the pixels, but one new P1 remains. In the matched top, aerial and front_corner roles, the roof round the light court is a blank slate hopper. The locked top and oblique sources show a working inner mansard there, with four large dormer boxes, rooflights and a ribbed lead band.

Counts: P0 = 0, P1 = 1, P2 = 12

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top, aerial, front_corner, rear_side, mansard_dormers, rear_north (vs sources top + oblique) | Inside the flat lead ring, each of the four inner roof faces is a single plain slate plane that falls into the court like a funnel. It has no dormers, rooflights or articulation, and it is the largest surface in the top and aerial frames. The locked top source shows the inner slopes carrying four large dormer boxes (one pair on the west inner slope, one pair on the east), two rooflights on the north inner slope and two lantern-rooflights plus a skylight on the south inner slope. The oblique source shows the same inner dormers standing above the court walls. The render therefore reads as an empty hopper, not the source's inhabited inner mansard. | The inner court slope was built as one lofted ring surface. The dormer generator was run on the outer street faces only. | Run the existing dormer assembly on the inner slopes as well. Place two large dormer boxes on each of the west and east inner slopes at about 0.3 and 0.6 of the court length, sized as in the top source (about 1.5x the outer dormers). Add two flush rooflights on the north inner slope, and two raised lantern-rooflights plus one small skylight on the south inner slope. Rerender top, aerial and front_corner. |
| 2 | P2 | giant_order (crops), architecture_close | The capitals now have a closed bell that reaches the abacus, with no dark gap. However, the leaves are flat angular plates whose tips bend outward rather than curl, and the corner "volutes" are flat diagonal blades with no scroll. At close range they read as a faceted crown rather than acanthus. They read correctly as Corinthian at the front and east_side distances. | Low-poly leaf blades with a single fold, and volutes modelled as planar wedges. | Give each corner blade a two-segment inward curl at the tip so it reads as a volute, and pull the outer leaf tips 20-30% closer to the bell. |
| 3 | P2 | porch_balcony (crop) | Small pure-black slits sit under the porch balcony slab where its returned end meets the wall entablature (about 40x6 px each). Thin black vertical slits also show between the two abacus blocks of each paired Tuscan column. | Unlit voids from a small offset between the slab or abacus blocks and the adjacent mass. | Extend the slab returns and abaci by about 2 cm into the wall and the neighbouring abacus, or merge each pair into a single abacus block. |
| 4 | P2 | aerial, front_corner (crops) | A black hairline runs round the top rim of the court wall where the inner slope meets it. | A gap or coincident edge between the court wall top and the slope's lower edge. | Add a coping strip or close the edge loop. |
| 5 | P2 | front, architecture_close, east_side, end_pediment, rear_north | The lead curb roll at the mansard break renders as a pure black line, with black blobs at the corners. It reads as an outline or cable, not as grey lead. | The curb roll was given the black ironwork material. | Assign a mid-grey lead material to the curb roll. |
| 6 | P2 | top, aerial, mansard_dormers | The flat upper "lead" ring is smooth. The source shows closely spaced standing-seam lead rolls on this band. | No seam ribs were modelled. | Add a rib array of thin raised rolls at about 0.6 m spacing on the upper band. |
| 7 | P2 | front, front_corner, architecture_close | The party-wall fins are thin white ribs. In the oblique source they are broad white wedge cheeks that stand well proud of the slate. | The fin cross-section is too narrow and too shallow. | Double the fin width and give it a deeper, wedge-shaped projection at the parapet end. |
| 8 | P2 | facade_close, porch_balcony | The rustication channels are short dashes that stop well short of the window architraves and porch columns, so the ground storey reads as dashed rather than banded. The black squares are gone. | Channel strips are clipped too far back from the openings. | Run each channel up to the architrave or column edge, still stopping at the voussoir fans. |
| 9 | P2 | facade_close, end_pediment | The pediment tympanum holds plain blocks, and a faint dark hairline shows between the left raking cornice and the tympanum. | The raking cornice is offset from the tympanum face. Sculpture is simplified, which is acceptable in clay. | Seat the raking cornice onto the tympanum plane. Optionally add a single relief block. |
| 10 | P2 | rear, rear_side, left_side, right_side, rear_north | The north "terrace" is one undifferentiated brick box under a single hip roof, with grouped windows and no doors, house divisions or chimney party parapets. It reads as one warehouse, not a row of houses. | Context massing was built as a single block. | Split it into five house volumes with chimney party-wall parapets, as in the top source, and give each house a door. |
| 11 | P2 | left_side, right_side, rear | In the whole-envelope elevations the building fills only about 38-45% of the frame width, with large empty ground and sky. Legible, but small. | The orthographic or long-lens framing is too loose. | Tighten the framing so the asset fills about 75% of the width. |
| 12 | P2 | front | The south end's far corner and its lamp sit about 30 px from the right edge of the frame. The view is valid, but the margin is tight. | Framing. | Pan about 2 degrees left or widen the field of view slightly. |

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette | conforms: rectangular palatial block, a balustraded parapet line, a steep slate mansard and stacks on fins. Compare with oblique and front. | front, front_corner, aerial |
| Storey count | conforms: channelled ground storey, tall first floor, shorter second floor, mansard attic. Basement shown as area slots. | east_side, facade_close, left_side |
| Plan and light court | conforms in outline: near-square block, streets on the west, south and east, terrace on the north, central court. The court floor is squarer than the source's north-south rectangle (polish only). The inner court roof deviates (finding 1). | top, aerial |
| Rustication | conforms: banded ground storey with voussoir fans over the windows and no black squares. Channel stubs short (finding 8). | facade_close, porch_balcony |
| Giant order (columns, capitals, rhythm) | conforms: engaged fluted columns through the first and second floors, one between every window bay, with matching rhythm on all three street faces. Capitals stylised (finding 2). | east_side, giant_order, end_pediment |
| Entablature and cornice | conforms: architrave, frieze and block-modillion cornice run continuously and turn the corners. | architecture_close, giant_order |
| Balustrade and pedestals | conforms: balustrade with pedestals over each column, stopping either side of the pediment. | east_side, mansard_dormers, facade_close |
| Porches and balconies | conforms: three porches of paired Tuscan columns per long front, each carrying a balustraded balcony whose pedestals sit on the slab. Minor black slits (finding 3). | east_side, front, porch_balcony, facade_close |
| End pediments | conforms: central pediment over the giant order on the south end, matching the oblique source. The north end abuts the terrace, so no second pediment is visible, which is coherent with the top source. | facade_close, end_pediment, front |
| Windows (sizes per floor, balconettes, heads) | conforms: tall first-floor windows with iron balconettes and cornice heads; shorter second-floor windows; glazing bars; visible reveals and sills. Openings show depth from inside and outside. | facade_close, glass_close, interior |
| Mansard (dormers, fins, stacks, flat top) | outer faces conform: a steep slate band rises from behind the balustrade to the curb, with short dormers standing high on it, six on the south (three each side of the pediment), and fins ending in stacks just inside the break. Inner court slopes deviate (finding 1). Curb roll black, no lead seams, fins slender (findings 5-7). | front, architecture_close, mansard_dormers, top |
| Areas and railings | conforms: iron railings along the pavement with dark area slots behind them; porch steps bridge the area. | front, front_corner, east_side |
| Streets and trees | conforms: roads and pavements on the west, south and east; lamps; two trees on the west pavement and one on the east pavement near the north end. No tree now covers the south bays. | top, front_corner, aerial |
| Terrace houses north | partly deviates: a brick context mass is present against the north side, but it is one undivided box (finding 10). | rear, rear_side, top |
| Materials hierarchy | conforms: cream stucco throughout, grey slate mansard, lighter lead top, black ironwork, brick context, terracotta pots. The curb roll uses the wrong material (finding 5). | front, aerial, architecture_close |

## 4. Camera validity

No view is invalid. In each of the 18 renders the target is legible, unclipped and unoccluded.
- front: valid. The camera is further back to the south-west. The whole west porch front and the south end with its pediment are in frame, with the slate mansard, dormers and white fins clearly above the balustrade. Sky above the roof is about 15% of the frame. The right margin is tight (finding 12).
- front_corner, aerial, top, rear, rear_side, left_side, right_side: valid. The elevations are framed loosely (finding 11).
- facade_close, architecture_close, glass_close, porch_balcony, giant_order, end_pediment, mansard_dormers, east_side, rear_north: each frames its named target with no occluder.
- interior: valid. It shows the window reveals, glazing bars and balconettes from inside.

## 5. Previous-version findings (v003) checked in the pixels

| v003 finding | status in v004 pixels | evidence |
|---|---|---|
| The front render hid the mansard, dormers and fins behind the balustrade; the camera was low and close, with about 35% sky and the south face running off the right edge. | **Resolved.** The camera is further back and higher in the south-west. The mansard band, eleven or more dormers, three white fins with stacks, the whole west porch front and the south end with its pediment are all in frame. The south end now finishes inside the frame (tight margin, P2 finding 12). | front |
| The lower mansard at about 30-40 degrees read as a low hipped roof with long tunnel dormers. | **Resolved.** The lower mansard is now a near-vertical slate band from behind the balustrade up to the curb roll at the break, with a shallow, lighter upper slope beyond. Dormers are short boxes standing high on the band. The fins are short ribs up the band, ending in stacks just inside the break. | front, architecture_close, mansard_dormers, east_side, left_side |
| Solid black squares appeared at every crossing of a voussoir strip and the rustication channel over the ground-floor windows. | **Resolved.** The channels stop at the edge of each voussoir fan, and no black squares remain over any ground-floor window. | facade_close, porch_balcony, east_side |
| Corinthian capitals had a dark gap between bell and abacus, and splayed stick leaves. | **Resolved to P2.** The bell is closed and reaches the abacus with no dark gap. There are two tiers of wider tapered leaves and diagonal corner blades under the abacus horns. The residual faceted, outward-bent finish at close range is polish (finding 2). | giant_order (3x crops), architecture_close |

Other builder claims checked:
- Six south dormers, three each side of the pediment: confirmed in top and front_corner.
- The south-east street tree moved to the east pavement near the north end: confirmed in top, front_corner and aerial.
- Balcony pedestals and plinths seated into the slabs: confirmed in the facade_close crop.

Finding 1 is a pre-existing omission that the earlier reviews did not list. It is raised now because it is clearly visible against the locked top and oblique sources.
