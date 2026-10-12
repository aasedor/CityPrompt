# Independent holistic review: plaza v010 (RLASM v6.1 architectural clay)

Reviewer: independent. Evidence used: `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, all 18 `renders/*.png` at full resolution (with zoomed crops), and the 4 `boards/*.png`. I did not read any code, build report or builder note.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: both v009 P1s are fixed in the pixels. The exterior now matches the sources well. The interior view, though, shows open sky and rooftop units through a strip in the envelope. That is a closure defect, so the candidate cannot be approved yet.

Counts: P0 = 0, P1 = 1, P2 = 7

## 2. Findings table

| # | severity | view(s) with pixel regions | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | `interior.png` x 735-1045, y 395-430 (bright strip above the alcove ledge), plus the diagonal light shaft on the left wall at x 600-740, y 400-520 | A slanted band above the lower alcove ceiling and below the main ceiling is open to the outside. Its pixels are exactly the background sky colour (151,156,159, sampled at (900,412), (1000,408), (1030,407)). Two white rooftop-unit blocks are visible through it (x 935-975). Sunlight comes through the gap and falls as a raking shaft on the interior wall. The envelope is not closed where the lower roof (cafe/vestibule) meets the taller anchor volume. | When the tier behind the cafe was merged into the cafe parapet, the inner wall or ceiling that closed the band between the cafe roof and the anchor roof seems to have gone too. The exterior parapet reads solid, but nothing closes the band from inside (or the wall is single-sided). | Add a closed, double-sided wall or soffit that spans from the cafe roof slab up to the anchor ceiling along the shared line, or extend the anchor west wall down to the cafe ceiling. Re-render `interior` and confirm that no pixel in the alcove band matches the sky colour. |
| 2 | P2 | `left_side.png` x ~563, y 530-600; `front_corner.png` x ~320, y 535-585 | A dark vertical seam runs through the cafe west cornice and wall at mid-length. The single parapet reads as two butted segments. | Two parapet or cornice meshes abut with a gap or overlap instead of a single run. | Use one cornice/parapet run, or weld the joint. |
| 3 | P2 | `left_side.png` x ~716-719, y 530-560 | A thin pale vertical sliver at the south-east end of the cafe cornice drops below the cornice line. | A leftover face from the removed tier, or a cornice end cap overshooting. | Delete or trim the sliver. |
| 4 | P2 | `glass_close.png` x 955-1010, y 120-250 | The anchor canopy end runs past the green pier and overlaps the brick end pier. It reads as cutting into the pier. | Canopy length exceeds the clear span. | Stop the canopy at the green pier face, or notch it around the brick pier. |
| 5 | P2 | `endcap_corner.png` x 815-850, y 365-445 | A second tie rod is anchored on blank EIFS beyond the end of the canopy and supports nothing. | The rod array is longer than the canopy. | Trim the rods to the canopy length. |
| 6 | P2 | `top.png`, `aerial.png`, `front.png` | The lawn verges are reduced to one khaki strip along the south edge. The sources show grass verges on the west and south and around the lot edges, plus a planted court island. | Simplified landscape. | Add grass verges along the west and south lot edges and one planted island in the court. |
| 7 | P2 | `left_side.png`, `right_side.png`, `rear.png`, `rear_side.png`, `front.png` | The building fills under 10% of frame height, with large empty sky and ground. It is legible at full size but tiny on the phone boards (boards 03 and 04). | The orbit distance is fitted to the site plane, not the building. | Tighten the elevation and rear cameras to about 70-80% frame width. Keep the front margin that fixed v009. |
| 8 | P2 | `fc_cafe` region of `front_corner.png` x 300-520, y 515-545 | The cafe roof tone changes at the internal joint, consistent with #2. | The same split meshes as #2. | Fixed together with #2. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette | conforms. Long, low single storey; the anchor box and entrance tower rise above it; the end-cap turns south at the east. Matches front and oblique. | front, front_corner, aerial vs `front.png`, `oblique.jpg` |
| L-plan and wings | conforms. West anchor block with lower cafe on its west flank, inline wing along the north of the court, end-cap running south on the east. Court is open to the south. Proportions agree with `top.jpg`. | top, aerial vs `top.jpg` |
| Anchor tower | conforms. Projecting tower at the anchor's west end, beige EIFS with brick pilasters and a dark cornice, green wrap at its base, glazed entrance with a flat canopy. | anchor_entrance, front_corner, roof_units |
| Anchor sign band | conforms. Green band over a continuous glazed front, brick end pier at the east. Text omitted, as clay allows. | facade_close, architecture_close |
| Cafe wing / west flank | conforms. One cafe parapet with one cornice along the whole west flank; only the set-back anchor box rises behind it. The joint seam is P2 (#2, #3). | left_side, front_corner, front |
| Shop-front rhythm and canopy | conforms. Regular glazed bays between brick pilasters on a brick base under a continuous canopy with tie rods. The canopy turns the corner onto the end-cap. | inline_shops, parking_court, front |
| End-cap and drive-through | conforms. Glazed storefronts on the court face and south face. Pickup window with sill and bollards at the south-west of the end-cap. | endcap_corner, aerial, front |
| Parking court | conforms. Striped stalls, simple car massing, accessible-stall hatches. | parking_court, top |
| Roof units | conforms. Flat roofs with parapets and distributed rooftop units on every volume. | roof_units, top, architecture_close |
| Materials hierarchy | conforms. Beige EIFS over a brick base, brick pilasters, dark cornice bands, green accent only at the anchor. | facade_close, inline_shops, left_side |
| Pylon sign | conforms. Brick-framed pylon at the south-west of the lot near the road edge. | front_corner, aerial, top |
| Lawn verges | deviates (P2 #6) | top, aerial |
| Rear faces (no source) | coherent with the visible grammar: EIFS over a brick base, service doors, loading dock. | rear, rear_side, rear_service |

## 4. Camera validity

- No view clips the asset. `front.png` now has the end-cap's south-east corner at about x 1305 of 1440, a margin of about 135 px.
- No target is occluded.
- `interior.png` is a valid camera, but it shows the envelope breach in finding #1.
- `left_side`, `right_side`, `rear` and `rear_side` are legible but very small on the phone boards (P2 #7).

## 5. Status of v009 findings

| v009 finding | Status in v010 pixels |
|---|---|
| P1: the front render clipped the end-cap's south-east corner at the right frame edge | **Resolved.** `front.png` shows the whole end-cap with its south face and corner pilaster at x ~1290-1305, well inside the frame, and a tree beyond it. |
| P1: the west flank read as two parapet tiers (a higher tier behind the cafe, each with its own cornice) | **Resolved.** `left_side.png` and `front_corner.png` show one cafe parapet and one cornice along the whole west flank, with only the set-back full-height anchor box rising behind it. The merge left a mid-length seam and an end sliver (P2 #2, #3). The interior closure gap (P1 #1) looks like a regression from this merge. |
| v009 P2s (9) | Not itemised in the brief, so I cannot check them one by one. The current P2s are listed above. |
