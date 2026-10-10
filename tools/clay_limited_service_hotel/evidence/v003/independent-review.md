# Independent RLASM v6.1 holistic review — clay-limited-service-hotel v003

Reviewer: independent (did not build the candidate). Judged only `renders/*.png` and `boards/*.png` against `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`. Every render, the three sources and the four phone boards were opened at full resolution before writing. Builder notes, counts and hashes were ignored.

## 1. Verdict

**VISUAL_REWORK_REQUIRED** — the v002 P0 (unjoined L legs) is genuinely fixed and the envelope, storey count, window grammar, tower, porte-cocheres and stone piers now conform, but three clearly visible P1 defects remain (guest-room windows and floor plates inside the glass tower, ribbon-not-storefront low wing, and a kerb-less site plane with a car parked across the rear door).

### Status of the v002 findings (verified in pixels, not from the builder)

| v002 finding | v003 status | Evidence |
|---|---|---|
| P0 — L legs not joined (through-sliver, parapet crossing roof at junction) | **Fixed** | `aerial.png`, `top.png`, `roof_plant.png`, `rear_side.png`: one continuous white membrane across both legs, parapet coping runs only around the outer outline, inner corner at roof_plant (x≈190,y≈290–460) is a clean re-entrant with the charcoal west face of the north leg below it; no sliver, no coping crossing the roof. |
| P1 — north wing colour and band | **Fixed** | `rear.png`, `rear_side.png`, `left_side.png`, `right_side.png`: north leg is charcoal with a green band; south leg beige with a navy band, matching the source front/oblique split. |
| P1 — ribbon glazing on the low wing | **Not fixed** (see finding 2) | `wing_contact.png`, `front.png`, `front_corner.png`. |
| P1 — stone piers | **Fixed** | `porte_cochere.png`, `interior.png`, `lobby_tower.png`: coursed, stone-coloured piers under both canopies. |
| P1 — guest floors running into the tower | **Not fixed** (see finding 1) | `architecture_close.png`, `glass_close.png`, `lobby_tower.png`. |
| P1 — parking stripes | **Fixed** | `top.png`, `rear_entry.png`, `front_corner.png`: stalls striped on the asphalt, grounded, regular. |
| P1 — road and kerbs | **Partly fixed** (road present, kerbs absent — see finding 3) | `top.png`, `aerial.png` show the east road as a lighter strip; no kerb upstand anywhere. |
| P1 — verges | **Partly fixed** (verges present as flat green bands, no kerb/sidewalk — see finding 3) | `top.png`, `rear_entry.png`. |

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | **P1** | architecture_close, glass_close, lobby_tower, parapet_corner | Through the tower glazing the beige block's **punched guest-room windows continue on the tower's inner walls at every level** (architecture_close: row of 3+4 white window rectangles at y≈470–520 at L4 level; glass_close: 2+3 at y≈520–580 at L2 level; lobby_tower: row of 8 at y≈595–640 at L2 level) and full **floor plates** cross the tower at each storey (architecture_close dark slab y≈650–700, glass_close pale slab y≈440–520). The "full-height glazed lobby tower" reads as a glass skin wrapped over the corner of the guest-room block, not a lobby volume; the source tower shows no interior punched walls. | Main block mesh (with window cutters) was not trimmed where the tower volume overlaps it; the tower is a separate glass shell laid over the block's SE corner. | Boolean-subtract the tower footprint from the main block through all four storeys (or stop the block's walls at the tower's inner faces), delete the window cutters inside that footprint, replace the inner faces with plain EIFS/lobby walls, and keep at most a landing/mezzanine slab rather than full floor plates. |
| 2 | **P1** | wing_contact, front, front_corner, left_side | Low wing is still a **strip/ribbon window**: in wing_contact the glazing is ≈215 px of a ≈505 px wall (≈43 %) with a ≈150 px beige fascia/spandrel above and a ≈140 px plinth below; in front.png glass is ≈35 of 75 px (≈47 %). Source front (y≈455–525) and oblique (y≈395–460) show near-full-height storefront glazing (≈60 %+) rising from a low stone base to a thin fascia, reading as a glass pavilion. | Wing modelled as a solid box with a cut ribbon opening; sill set too high and head too low. | Drop the sill to ≈0.3–0.5 m above grade (stone base only), raise the head to the underside of the fascia, keep the mullion bays; leave a thin beige fascia band under the coping. |
| 3 | **P1** | rear_entry, wing_contact, interior, lobby_tower, top | **No kerbs, sidewalks or pedestrian surfaces anywhere**: asphalt runs flush into the stone plinths (wing_contact y≈900, lobby_tower, interior y≈690–720) and flush into the flat green verges (rear_entry y≈600–1000). At the rear entry the parking stalls run straight to the north facade and the white car block (x≈500–790, y≈590–720) is parked across the rear door (x≈690–770); the entry canopy shelters a parking stall. Source shows concrete sidewalk along the facades, kerbed verges and islands, and a gravel apron. | Site is a single flat painted plane; stalls generated edge-to-edge with no setback from the building. | Add a ≈1.5 m raised sidewalk slab (light grey, ≈0.15 m upstand) along all facades and at the two entrances, a kerb upstand at every asphalt/verge edge, and set the north stall row back from the facade by the sidewalk width; move the car blocks off the entry axis. |
| 4 | P2 | architecture_close, wing_contact, roof_plant | Accent band is thick (≈ a third of a storey) and the top-floor windows butt directly against its underside; source has a thinner band with a beige margin above the top windows. | Band height / top-window head offset. | Reduce band height ~40 %, lower top-row head ≈0.4 m. |
| 5 | P2 | left_side vs source front (x≈150–190, y≈320–340) and oblique (x≈265–290) | West end of the south leg carries the navy band; source shows the end parapets as dark/green. | Band colour assigned per leg, not per face as in source. | Colour the west-end return of the band dark/green. |
| 6 | P2 | facade_close, porte_cochere vs source front (x≈190–390, y≈455–525) | Ground-floor stone base is a short plinth (≈1/3 of the ground storey); source stone veneer rises to roughly the L1 sill/head between the ground windows. | Plinth height. | Raise stone to the L1 head line between windows. |
| 7 | P2 | facade_close | Window pairs have a wide beige gap (≈½ window) and squarer proportions; source pairs are tall and nearly touching with a thin mullion. | Opening cutter dimensions. | Narrow the intra-pair gap and lengthen the windows. |
| 8 | P2 | front_corner, top | Low-wing rooflight is a flush flat grey patch; source top shows a glazed rooflight with visible frame/upstand. | Rooflight modelled as a decal-like plane. | Add a 0.3–0.5 m curb and a glazed lid. |
| 9 | P2 | top, aerial vs source top/oblique | Drive-loop islands under the porte-cocheres, gravel apron and the landscape finger in the west court are absent; pylon sign is at the SE corner, source places it mid-way along the east road. | Site simplification. | Add kerbed loop islands and move the sign north. |
| 10 | P2 | rear_entry | EIFS panel joints on the charcoal faces render as light tan hairlines, reading as a seam/leak rather than a reveal. | Joint colour not darkened for the charcoal field. | Use a darker-than-field joint colour. |
| 11 | P2 | rear vs left_side | South leg's north (inner-corner) face is charcoal with green band while its west end face is beige with navy band, so the colour field changes at an outside arris. No source shows this corner; coherence only. | Colour assignment by wall rather than by leg. | Make the south leg's north face beige/navy, or terminate the charcoal with a reveal. |
| 12 | P2 | front, rear, left_side, right_side | Whole-envelope elevations put the subject in ≈35 % of frame width; rhythm is legible but small. | Camera distance. | Tighten framing. |

P0: 0 · P1: 3 · P2: 9

## 3. Source conformance checklist

| Item | Result | View(s) used / what was compared |
|---|---|---|
| Silhouette (L-plan, 4-storey block, low SW wing, SE tower, two canopies) | **conforms** | `top.png` vs `sources/top.jpg`: north leg ≈265 px wide × 250 deep, south leg ≈410 × 260 with the north leg's west face ≈125 px inboard of the south leg's west end and a small east-face jog — same proportions as source; `aerial.png` vs `sources/oblique.jpg`. |
| Storey count (4 + 1-storey wing, tower rising slightly above parapet) | **conforms** | `front.png`, `right_side.png`, `rear.png`, `left_side.png`: four window rows everywhere; `wing_contact.png`: one-storey wing; `parapet_corner.png`: tower cap above parapet as in source front. |
| Window rhythm (paired punched windows with reveals) | **conforms** (proportion P2) | `facade_close.png`, `rear_entry.png`: pairs with dark frames and visible depth/returns; counts 4 pairs on south face, 4 beige + 5 charcoal on east face. Pair spacing wider than source (finding 7). |
| Lobby tower (full-height glazing, dark cap, beige returns) | **deviates** (P1) | `lobby_tower.png`, `architecture_close.png`, `glass_close.png`: exterior conforms — glazed both faces, dark cap, beige flanking returns, two entrance doors — but inner faces carry the block's punched windows and floor plates (finding 1). |
| Porte-cocheres (two, glass roofs, stone piers, E and S) | **conforms** | `porte_cochere.png`, `interior.png`, `aerial.png`, `top.png`: dark fascia, translucent glass roof with purlins, coursed stone piers; positions south of the tower and on the east face match source top. |
| Low wing (one-storey glazed breakfast/pool wing with rooflight) | **deviates** (P1 + P2) | `wing_contact.png`, `front_corner.png`, `top.png`: position, height and rooflight location conform; glazing is a ribbon not a storefront (finding 2); rooflight flush (finding 8). |
| Roof plant (white membrane, RTUs) | **conforms** (simplified) | `roof_plant.png`, `parapet_corner.png`, `top.png`: white membrane, dark coping, 4 grounded RTU blocks; source has more and smaller units — acceptable in clay. |
| Site elements (parking court, drive loop, pylon sign, road, verges) | **deviates** (P1 + P2) | `top.png`, `rear_entry.png`, `aerial.png`: parking court west, lane east, road east, sign, verges present; no kerbs/sidewalks, car across rear door (finding 3); loop islands and sign position (finding 9). |
| Materials hierarchy (beige/charcoal EIFS, navy/green bands, stone base and piers, dark frames, white roof) | **conforms** (band thickness P2) | `aerial.png`, `right_side.png`, `facade_close.png`, `porte_cochere.png`: colour split beige south / charcoal north, navy on beige, green on charcoal, stone plinth and piers, dark frames and coping. Band too thick (finding 4), west-end band colour (finding 5), stone base height (finding 6). |
| North and west faces (not shown in sources) | **not visible in source — coherent** except P2 11 | `rear.png`, `left_side.png`, `rear_entry.png`: same paired-window grammar, bands and plinth continue; rear entry with small canopy is coherent with a highway hotel. |

## 4. Camera validity

All 18 views are valid: no target is occluded, no asset is clipped in a way that hides the target, and every view is legible.

Notes (not failures):
- `interior.png` is shot from outside under the canopies; the lobby interior (stair, door, floor) is legible only through reflective glazing — weak as an "interior" view but the target is visible.
- `roof_plant.png` clips the south porte-cochere canopy at the right frame edge; the target (roof plant and parapets) is complete and legible.
- `front.png`, `rear.png`, `left_side.png`, `right_side.png` place the building in roughly a third of the frame width with a large empty ground plane; rhythm and bands remain readable at full resolution (P2 12).
