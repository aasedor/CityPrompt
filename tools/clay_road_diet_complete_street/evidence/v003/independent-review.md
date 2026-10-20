# Independent holistic review: road diet complete street, v003

Reviewer: independent RLASM v6.1 holistic reviewer. I did not build this candidate.
Evidence used: the three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`), all 18 PNGs in `renders/`, and the four phone boards. I opened every render at full resolution. I also made zoomed crops of the front lamps, the front island, the west bands in front, the north and south legs in top, the far lamp in verge_trees, the sign back in turn_lane, the island sign in refuge_island, the east trees in aerial, the corner in front_corner, the lamp in rear, and the source west-verge lamps. The crops were written only to the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/rv003-crops-06cf2e7d/`. I treated builder claims as hypotheses and checked them only against pixels.

## 1. Verdict

**PASS_ZERO_P0_P1**: the road-diet section, markings, crossings, islands, separators, furniture, planting and street wall all match the locked sources. The v002 lamp P1 is now resolved in the pixels: arms and cobra heads read from street level in front and verge_trees. What remains is polish only.

Counts: P0 = 0, P1 = 0, P2 = 6

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | front, verge_trees, rear, bike_lane_separator | The west-verge trees now have a clear, straight, untapered trunk for about half their height, and the crowns start above the lamp heads. In the sources (front, oblique) the elms fork low, at about one third of their height, into several stems, and the canopy reaches down toward lamp-head level. The tall cobra-head poles rise into the canopy. The trees still read as dense, overlapping, multi-lobe mature crowns (not lollipops), but their proportion and the lamp-to-canopy relationship drift from the source. | The v003 fix raised every crown lobe 2.6 m and cut the lamps to 6.2 m so the heads clear the crowns. | Optional: lower the crowns by about 1 m and lift the lamps to about 7.5 m, keeping the sightline gap. Or add a low primary fork and a slight trunk taper so the clear stem reads less columnar. |
| 2 | P2 | verge_trees | The pole of the farther lamp hides exactly behind the third tree trunk, so its arm and head seem to grow out of the trunk. | A chance alignment between the camera and the lamp/tree positions. | Shift the verge_trees camera about 0.5 m sideways, or yaw it 1 to 2°, so that pole clears the trunk. |
| 3 | P2 | front | The near (south) end of the north refuge island falls outside the right edge of the frame, and with it the keep-right sign face. Only the far-end sign back (plain dark plate) and the yellow object-marker posts show. In the source front, the sign and marker are a focal element. The sign face reads correctly in refuge_island and crosswalk_zebra. | The camera framing follows the top-view plan, which puts the island right next to the crosswalk. | Yaw the front camera about 5° right or pull it back about 2 m so the island's near end and sign are in frame. |
| 4 | P2 | left_side, right_side | A nearby cross-street tree crown fills about a quarter of the frame on the right and hides the right sidewalk and street wall. The street itself stays fully legible. | Camera placed close to the sidewalk tree line. | Move the cameras toward the cross-street centreline or raise them about 1 m. |
| 5 | P2 | refuge_island, crosswalk_zebra | The keep-right sign glyph is a straight diagonal stroke with a hooked head between top and bottom bars. The source sign shows a bent arrow. It reads as a keep-right sign at clay level. | Simplified glyph. | Optional: redraw the glyph as the bent R4-7 arrow. |
| 6 | P2 | (deliverable) | The brief's detail list names facade_close, architecture_close and glass_close, but the folder holds 18 views without them. The brief's count of 18 matches. storefronts and corner_signal cover the facade and glazing close-up role, with visible frame reveals and sills. | Street-option view profile. | None needed for this verdict. Keep the profile and the brief's list consistent. |

No P0 or P1 findings.

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Section order and widths, west to east: lawn, sidewalk, grass verge, curb, green bike lane, raised separator, travel lane, centre TWLTL, travel lane, separator, green bike lane, east sidewalk, storefronts | conforms | top (zoomed north and south legs), verge_trees, bike_lane_separator, rear, turn_lane |
| Green paint extent (full main-street and cross-street lanes, continuing under the crosswalk bars) | conforms | top, crosswalk_zebra, corner_signal, bike_symbol |
| Raised concrete separators with white delineator posts | conforms | bike_lane_separator, rubber_curb, top, left_side |
| Rubber curb stops at the crosswalks (black, yellow chevrons, three posts) | conforms: two chevrons sit between the posts and no post base stands on a chevron | rubber_curb, front_corner (zoomed), top, bike_symbol |
| Centre-lane yellow lines (solid outer, dashed inner on both sides) and opposing white left-turn arrows | conforms | turn_lane, top, rear |
| Refuge islands: curb, planting, keep-right sign, object marker | conforms: raised curb, dense straw tussocks on mounds, white keep-right sign, yellow-and-black marker; far-end back plate plain dark grey, no arrow ghost | refuge_island, crosswalk_zebra, turn_lane (zoomed), front (zoomed), top |
| Continental zebra crosswalks on all four legs, spanning the bike lanes | conforms | top, aerial, crosswalk_zebra, front |
| Stop bars (on the approach side of each crosswalk, in the approach lane) | conforms | top, crosswalk_zebra, refuge_island |
| Cross-street dashed yellow centre line | conforms | cross_street_lane, left_side, right_side, top |
| Cross-street hatched painted buffer with posts and curb-side green lanes | conforms | cross_street_lane, left_side, right_side |
| Bicycle symbols on every green lane, clean strokes, no black triangles | conforms | bike_symbol, top (all 12 lane segments) |
| Signal poles with mast arms and three-lamp heads at all four corners | conforms | corner_signal, top, aerial, left_side |
| Lamps (black cobra-heads) | conforms: west arms and heads visible from street level and from above; lower and shorter relative to the canopy than in the source (P2 #1) | front (zoomed), verge_trees (zoomed), rear (zoomed), aerial |
| Mature verge trees (rounded, multi-lobe, two greens, overlapping) | conforms: crowns raised (P2 #1) | front, verge_trees, front_corner, aerial, rear |
| East young trees in pits, crowns clear of the facades | conforms | top, aerial (zoomed), storefronts, crosswalk_zebra |
| Bins and bike racks | conforms | storefronts, crosswalk_zebra, corner_signal, top |
| Storefront row: large glazing with transoms, doors, dark sign band, cream upper storey, brick pilasters, sash windows, coping | conforms: glazing set in frames with visible reveals and sills | storefronts, corner_signal, front_corner, refuge_island |
| Four-storey brick apartment block with balconies (north-east) | conforms | front_corner, bike_lane_separator, front, refuge_island |
| South-east beige stucco two-storey block | conforms | right_side, aerial, rear_side |
| West blocks (two-storey brick office and one-storey block behind lawns) | conforms | aerial, front, verge_trees |
| Context massing (plain blocks) and clay car placeholders (opaque cabins, wheels tucked under the sill) | conforms | aerial, rear_side, rubber_curb, cross_street_lane, turn_lane |
| Materials hierarchy (asphalt dark, green paint, pale concrete, brick, cream, stucco, black metal, straw grass) | conforms | all |

## 4. Camera validity

- No view has an occluded target, a clipped asset that removes legibility, or nothing legible. All 18 views are valid.
- front: the near end of the north refuge island is cut off by the right frame edge (P2 #3). The section, separator, rubber curb, crosswalk, lamps and street wall are all legible.
- left_side and right_side: a nearby crown fills about 25% of the frame on the right (P2 #4). The cross street, buffers, green lanes, centre line, crosswalks and signals are legible.
- verge_trees: the farther lamp pole is hidden behind a trunk (P2 #2). The nearer lamp, the verge, the sidewalk and the lawn are legible.
- top: a valid nadir view, with the intersection centred, the main street north-south and the cross street east-west.

## 5. Previous-version findings: resolved in the pixels?

| previous finding | status in v003 pixels |
|---|---|
| v002 P1 (and v001): from the low front and verge_trees cameras, the west-verge cobra-head lamps read as bare poles whose arm and head were hidden by the nearer crown | **Resolved.** front: all three visible west lamps show the pole, the horizontal arm and a cobra head with a pale lens, reading against the farther canopy or the sky (zoomed crop). verge_trees: the near lamp's arm and head read fully against the sky; the far lamp's arm and head are visible, though its pole hides behind a trunk (P2 #2). From above (rear, aerial) the arm and head still read. The crowns remain dense, rounded, overlapping and multi-lobe, not lollipops, at the cost of a higher clear trunk (P2 #1). |
| P2 claim: the chevrons on each rubber curb stop sit between the posts | Confirmed in rubber_curb (two chevrons between three posts) and in the zoomed front_corner. |
| P2 claim: the keep-right sign has a plain back plate | Confirmed: turn_lane (zoomed) and front show a plain dark-grey back with no arrow ghost. |
| P2 claim: the car wheels are tucked under the body sill | Confirmed in rubber_curb, cross_street_lane, turn_lane and front. |
| v002 fixes: rounded multi-lobe crowns in two greens; east pit and corner crowns clear of the facades; dense straw tussocks on the islands; opaque cabins; no black triangles in the bike symbols or turn arrows | All still hold (aerial, front_corner, top, refuge_island, front island crop, bike_symbol, turn_lane). |
| v001 successes: lane order and widths and the east mirror; zebras on all four legs; planted islands with signs and markers; cross-street centre line, buffer and green lanes; signal mast arms; brick-and-cream storefront row, four-storey apartment block, set-back west blocks | All still hold (see the checklist). |
