# Independent holistic review: clay-brick-parkade v003 (RLASM v6.1 architectural clay)

Reviewer: independent, adversarial. Evidence: rendered pixels only. I opened all 18 renders at full resolution, the three locked sources (front.png, oblique.jpg, top.jpg) and the four phone boards. I made zoomed crops into a new scratch folder (`indrev-parkade-v003-crops-q7`). I did not open any metadata, logs or builder notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The candidate fixes the east face and removes the extra south-face piers, but the south-face open-deck zone is still built as three stacked punched openings in brick. Brick bands sit between the decks and the pale upstands project in front of the brick. The source shows one wide, deep, brick-framed void lined with concrete across decks 2 to 4. This is a residual of v002 P1 #2.

Counts: P0 = 0, P1 = 1, P2 = 10

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | facade_close, front_corner, aerial, front | **South open-deck zone (decks 2 to 4):** each deck reads as its own punched opening in the brick wall. A brick band about half the upstand's height runs under every pale upstand, between it and the opening above (facade_close y≈120–160, 385–420, 645–740). Each deck opening has its own brick jambs. The pale upstands sit **proud** of the brick: they cast a shadow down onto the brick band and their ends run past the jamb onto the brick. At the top of the zone a pale upstand sits directly under the roof coping, with no brick header. From a distance the zone reads as stacked pale ribbons on a brick wall, the same grammar as the east and north faces. In the source (front and oblique), one deep opening spans decks 2 to 4 under a thick brick header, with brick returns at its edges. Inside it are recessed pale concrete upstands, slab edges and columns, and no brick between decks. | The "one wide opening per deck" was built as three per-deck cuts through the brick carrier. The upstands were placed on the outer facade plane instead of inside the void. | Cut one aperture through the brick carrier spanning decks 2 to 4 (deck-2 sill to the underside of a brick header about 0.6 to 0.8 m below the parapet coping), with brick returns at least 0.3 m deep. Place the pale upstands and slab-edge bands **inside** the aperture, recessed 0.3 to 0.5 m behind the brick face. Colour the slab edges between upstand and next opening pale concrete, not brick. Keep the deck-1 punched opening below the brick band as it is now. |
| 2 | P2 | tower_crown, front_corner, right_side, rear_side | Patina is a light blue-cyan, still pale beside the source's darker mottled green patina. The crown's east patina panel is hung as a separate plate proud of the bronze frame. It overlaps the louvre strip and one post, and its thickness edge shows. | The panel is placed outboard of the frame plane. The patina value is too high. | Set the patina panel inside the crown frame bay, flush with the louvre plane. Darken it and shift it toward green (about 60–75% of current value). |
| 3 | P2 | architecture_close (corner), front_corner | The SE tower corner is still two separate bronze posts with a bright pale sliver between them along the full height. | Each face's frame terminates separately at the corner. | Replace the two posts with one corner post, or close the gap with a bronze infill. |
| 4 | P2 | front_corner, front, rear | The west stair head is still a thin grey cap slab on top of the glass shaft, plus a brick box behind it. The source shows a solid dark precast or charcoal head about one storey tall above the parapet. | Head massing not rebuilt. | Replace the cap with a solid dark head volume about one storey tall over the glazed shaft, and remove the brick wedge. |
| 5 | P2 | front, front_corner | The south-face west brick bay has a pale precast panel above its top ribbon, where the source has a brick header. The deck-1 open bay has a pale upstand, where the source has brick with a thin ledge. | Spandrel module repeated to the top and bottom. | Change the top panel and the deck-1 upstand to brick, with a thin concrete ledge at the deck-1 sill. |
| 6 | P2 | architecture_close, right_side, vehicle_entry | East-face bays 1 and 2 now read dark and mullioned, but the screens have a mid-height horizontal rail, so they read as a square grille rather than single-tier mullioned ribbon glazing. The precast spandrels stand proud of the brick piers. In the source they sit flush or recessed within the frame. | Grid module with transom; spandrels on the outer plane. | Remove the mid rail, or keep it only very thin. Set the spandrels flush or slightly recessed between the piers. |
| 7 | P2 | facade_close, north_lane, retail_base | Brick has a slight pink or salmon cast beside the source's deeper red-brown. | Base colour value and saturation. | Shift the brick hue slightly toward red-brown and lower its value about 10%. |
| 8 | P2 | interior | Cars are blocky stacked boxes that overlap in depth, and it is unclear whether they touch or interpenetrate. The far-wall openings have thin glowing white outlines. | Car proxy spacing; edge or emission artefact on openings. | Space the car proxies on a stall grid with a clear gap. Remove the outline artefact. |
| 9 | P2 | retail_base, facade_close, stair_penthouse | A tree trunk covers the centre of retail_base. A tree crown covers the deck-1 and retail corner of facade_close. A light pole fills the left foreground of stair_penthouse. The targets are still legible. | Camera placed behind entourage. | Offset these cameras, or hide entourage in detail cameras. |
| 10 | P2 | front | The front camera is a frontal elevation of the south face with the building at about 45% of frame width. The locked front is a street-level three-quarter view, so the role match is weak; front_corner carries that comparison. | Camera role choice. | Add, or reframe to, a street-level SE three-quarter view matching the source front, with the building at 70% or more of the frame. |
| 11 | P2 | stair_penthouse, top | The stair well reads better than in v002 (dark grey interior, a column, a pale flight), but the stair flights are hard to read and the well still looks mostly empty. The top view shows black with two pale bars. | Low interior light; sparse flights. | Add two clear stair runs with a landing and some fill light in the well. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette (rectangular block, corner towers rising above the parapet, west stair, roof plant) | conforms | front_corner vs oblique; top vs top; aerial |
| Footprint proportion | conforms (roof about 1.35:1 in render against about 1.33:1 in source top) | top vs source top |
| Level count (retail ground + 4 decks + roof) | conforms | front, front_corner, left_side, right_side |
| Bay rhythm and piers | south: deviates (#1, stacked brick bands inside the open zone); east: conforms (3 bays, two southern bays glazed or screened, north bay open); west and north: coherent | front, facade_close, right_side, rear, left_side |
| Spandrels, brick south | partly conforms (no extra piers; upstands pale; but brick bands between decks and upstands proud, #1) | facade_close, front_corner |
| Spandrels, precast east | conforms (pale precast; proud of piers, P2 #6) | architecture_close, right_side |
| Dark guard screens in deck openings | conforms (dark mullioned screens on east bays 1–2; guard rails in open bays) | architecture_close, vehicle_entry, facade_close |
| Glazed retail base | conforms (bronze-mullioned glazing between brick piers on a pale base) | retail_base, front, right_side |
| SE corner tower: strips (precast / glass / louvre) | conforms | architecture_close, front_corner, front |
| SE corner tower: bronze band at first deck | conforms | front_corner, architecture_close |
| SE corner tower: louvred crown | conforms | tower_crown |
| SE corner tower: patinated coping | conforms in form; patina value pale (P2 #2) | tower_crown, front_corner |
| North-east tower (larger, same grammar) | conforms (larger footprint than SE, as in source top) | top, rear_side, right_side, roof_deck |
| West narrow glazed stair at the west end of the south face | conforms in body; head deviates (P2 #4) | front, front_corner, left_side |
| Roof deck: stall stripes | conforms | top, roof_deck |
| Roof deck: light poles | conforms | roof_deck, aerial |
| Roof deck: dark ribbed lift overrun + rooftop units | conforms | roof_deck, top |
| Roof deck: open stair well with guard rail | conforms (legibility P2 #11) | stair_penthouse, aerial |
| Vehicle entry/exit on the east street | conforms (two deep dark openings with columns and ramp in the north bays, under a dark lintel band as in the source) | vehicle_entry, right_side |
| Curtain wall at the SE end of the south face starting at deck 2, punched deck-1 window below | conforms | front, front_corner |
| Materials hierarchy (brick frame > precast > dark bronze > glass > patina) | conforms overall; bronze now dark; brick slightly pink (P2 #7); patina pale (P2 #2) | all whole-envelope views |
| Openings have depth and returns | conforms everywhere except the south open zone, where per-deck returns replace one deep framed void (#1) | facade_close, vehicle_entry, north_lane |
| Contact / floating / intersection | no floating envelope parts found. The patina panel is proud but in contact (P2 #2). Car proxies are ambiguous (P2 #8). | tower_crown, interior |

## 4. Camera validity

- No view is invalid. In every whole-envelope view (front, front_corner, aerial, top, left_side, right_side, rear, rear_side) the asset is whole, unclipped and legible.
- front: legible, but the building is small (about 45% of frame width) and the camera is frontal while the source is a three-quarter view (P2 #10).
- retail_base: a tree trunk covers about 8% of the frame at centre; the glazing, piers and base are still legible (P2 #9).
- facade_close: a tree crown covers part of deck 1 and the retail; the open-zone decks are fully legible (P2 #9).
- stair_penthouse: a light pole sits in the left foreground; the stair well and guard rail are legible (P2 #9).
- interior: dark but legible (columns, slab, car rows, perimeter openings).
- tower_crown, glass_close, architecture_close, roof_deck, vehicle_entry, north_lane: clear.

## 5. Previous-version (v002) findings: resolved in pixels?

| v002 finding | v003 status | Pixel evidence |
|---|---|---|
| P1: the two southern east-face deck bays read pale and open where the source shows dark mullioned ribbons | **Resolved.** Residual P2 #6 (mid rail makes a grille). | architecture_close, right_side, vehicle_entry: dark bronze close-mullion screens fill both southern bays on every deck; only the north bay is open with rails, as in the source. |
| P1: south open-deck zone split by two extra brick piers into three bays | **Partly resolved. Carried forward as P1 #1.** | Piers gone: front, facade_close and front_corner show continuous openings with pale recessed columns at the old bay lines behind the rails. But the decks are still separated by brick bands with per-deck jambs, the upstands are proud of the brick, and there is no brick header, so it is not the source's single brick-framed void. |
| P1 sub-item: brick (not precast) between the ribbons in the west bay | **Resolved.** | front and front_corner: pale precast panels between the three ribbons over a brick deck-1 band. The top panel should be brick (P2 #5). |
| P1 sub-item: curtain wall running through deck 1 instead of a punched window | **Resolved.** | front and front_corner: the curtain wall covers decks 2 to 4, with a punched deck-1 window below it in brick. |
| P2: pale patina | Not resolved (still light blue-cyan) | tower_crown |
| P2: bronze slightly light | Resolved (dark bronze) | architecture_close, glass_close, tower_crown |
| P2: split SE corner posts | Not resolved | architecture_close (pale sliver between two posts) |
| P2: black stair well | Partly resolved (now has a grey interior, column and flight, but still hard to read) | stair_penthouse, top |
| P2: light lift overrun | Resolved (dark ribbed bronze-brown) | roof_deck, front_corner |
| P2: deck-1 lintel bands | Kept. The dark lintel over the east vehicle openings matches a dark band in the source, so it is not a defect. The south deck-1 sill should be brick (P2 #5). | vehicle_entry; source front east ground |
| P2: interpenetrating cars | Unclear (blocky, overlapping in depth) | interior (P2 #8) |
| P2: thin west-stair head | Not resolved | front_corner, front, rear (P2 #4) |
| P2: tree-occluded close-ups | Not resolved | retail_base, facade_close (P2 #9) |
