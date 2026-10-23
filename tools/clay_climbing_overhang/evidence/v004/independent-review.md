# Independent holistic review — The Overhang, v004 (RLASM v6.1 architectural clay)

Reviewer: independent; I did not build this candidate. I judged rendered pixels only, against `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. I opened all 18 renders and the 4 phone boards at full resolution, and made zoomed crops of the shell foot, the shell/parapet fold, the white-hold band, the wall under the east overhang and the SE corner of the top view. I did not use builder notes, counts or hashes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the building, roof program and landscape now conform closely, but the climbing shell, which carries the building's identity, meets the plaza on a knife-edge spike. The source shows a broad, planted base. There is also a stray spandrel plate and a stepped parapet stub on the white wall under the overhang.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | **P0** | front, front_corner, aerial, entrance, wall_base_contact, right_side, phone-01 | **Envelope and contact of the shell foot.** In front and front_corner the shell's west and south faces taper to a single sharp point on the plaza, about 2 m in front of the entrance doors. The shell reads as an inverted crystal balanced on its tip. right_side and entrance show that its only ground line is a short wedge edge running from that point north-east to the facade. In both locked sources (front, and oblique at matched roles) the shell stands on a **broad base**. Its bottom edge runs east along the facade line, roughly from the east jamb of the entrance doors to under the east overhang, which is about 1.5x the width of the frame box. The lit west face is wide at the plaza ("flares out at the foot") and the fold between the west and south faces lands mid-base. Side by side on phone-01, the lower third of the shell is a different silhouette, a spike instead of a planted, leaning prism. | Shell section/loft collapses the lower ring to a vertex (or to a very short N–S edge) instead of a base polygon aligned with the south facade. This is probably driven by the "south face is a triangle widening from its foot" reading, which the source pixels do not support. | Re-author the shell's lowest section as a base polygon on the plaza. The long side should run E–W, parallel to and just in front of the south facade, from the east door jamb to roughly under the rim's east end. The west face must widen to the plaza and the west/south fold must land partway along that base. Keep the rim position, the level, the lean and the cantilever unchanged. Re-render front and front_corner and overlay them on the source silhouettes. Re-check wall_base_contact for full-length plaza contact. |
| 2 | **P1** | right_side, climbing_face, (aerial) | **Stray plate and stepped parapet on the white wall under the east overhang.** There is a free-standing white rectangular plate, a leftover spandrel or band piece, at about third-storey level on the otherwise plain wall. Its west end runs behind or into the shell's east face. Above it, where the wall meets the shell, the parapet steps: a higher, more projecting block sits beside the lower east-block parapet. Both read as orphan geometry, not as part of the facade grammar. | The band module was removed from the under-overhang bay but one segment and its parapet cap stayed. The parapet segment there is at a different height or offset. | Delete the orphan plate. Make the parapet cap over the under-overhang wall continuous with the east-block parapet (same height and projection), or end it cleanly against the shell. Re-render right_side and climbing_face. |
| 3 | P2 | front, front_corner, climbing_face | The white holds along the west/south fold are small and sparse (about 15 tiny holds that fade out in the lower half). The source shows a full-height stream of larger white holds down to the foot. | Hold scale and count in the fold band are too low. | Enlarge the band holds about 1.5x and extend the band to the foot. |
| 4 | P2 | front, wall_base_contact, entrance | There is no contact or occlusion darkening where the shell meets the plaza, so the foot looks pasted on. | No AO or contact shadow at the base (overcast clay lighting). | Add a soft AO or contact-shadow strip along the base, after fix #1. |
| 5 | P2 | front, front_corner (zoom) | A hairline dark slit runs between the shell's west face and the pool-block parapet and frame-box return at the fold. | Shell face is tangent to the parapet and not exactly coincident. | Close the gap or add a small timber or flashing return at the fold. |
| 6 | P2 | all shell views | The CLT reads as a flat, saturated mustard and is warmer and yellower than the source's honey timber. | Palette value. | Shift slightly toward a less saturated honey-tan. Keep the fascia lighter. |
| 7 | P2 | front, aerial vs source front/oblique | The plaza is flush with the sidewalk. The source has steps down at the south edge and beside the west entrance approach. | Not modelled. | Add 2–3 shallow steps along the south edge. |
| 8 | P2 | top, rim_interior | The crash mat still reads as a near-black void in top and cannot be seen in rim_interior. The source top also shows a dark rectangle, so this is acceptable. | Lighting in a deep shaft. | Optional: lift the mat value slightly. |
| 9 | P2 | pool_deck | The water is a flat slab, and the glass weir edge is barely legible at the west trough. | Clay water material; thin weir. | Optional: add a slightly lighter weir lip line. |

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette: three-storey pool block (glazed ground + 2 upper + deep parapet) | conforms | left_side, front, front_corner vs source front/oblique |
| Silhouette: one-storey penthouse on mid-roof | conforms | front, front_corner, rear, top |
| Silhouette: four-storey east block | conforms (north and east fronts are authored and coherent) | right_side, rear, aerial |
| Plan (top view): about 39 m south × 36 m deep, pool block W, penthouse middle, east block E, shell over SE/S | conforms | top vs source top |
| Climbing shell: foot on the plaza | **deviates (P0 #1)**: knife-edge point vs broad planted base | front, front_corner, wall_base_contact, right_side, entrance |
| Shell: lean east and cantilever over the plaza and the white facade | conforms | front, front_corner, top, right_side |
| Shell: folded faces | conforms in the upper two-thirds; the lower faces deviate per #1 | front, climbing_face, rim_interior |
| Shell: level open rim with light timber fascia | conforms | front, rim_interior, top |
| Shell: contact with the plaza | deviates (P0 #1; P2 #4) | wall_base_contact, entrance |
| Shell: contact or fold with the pool-block parapet | conforms (hairline P2 #5) | front, front_corner, rim_interior |
| Holds: dark holds densest on the south face | conforms | climbing_face, front, rim_interior |
| Holds: white band along the fold | conforms in placement; undersized and sparse (P2 #3) | front, climbing_face |
| Three climbers on the south face | conforms | climbing_face, front, rim_interior |
| Open top and inner walls with white holds | conforms | rim_interior, top |
| Crash mat at the bottom | conforms to source (dark rectangle); hard to read (P2 #8) | top |
| West front rhythm: fins, spandrels, recessed two-pane windows with returns | conforms | facade_close, left_side, architecture_close |
| West glazed ground floor behind white columns | conforms | left_side, front |
| South projecting white frame box with two storeys of glass ribbons (5 panes) | conforms | architecture_close, front, glass_close |
| Entrance: two pairs of doors in recessed ground-floor glazing | conforms | entrance, interior |
| Deep white parapet band | conforms | left_side, architecture_close |
| Pool deck: long N–S infinity pool on the west edge | conforms | top, pool_deck, front |
| Pool deck: weir and overflow trough at the west parapet | conforms (weak legibility, P2 #9) | pool_deck, top |
| Pool deck: glass balustrades on the parapet | conforms | left_side, pool_deck, architecture_close |
| Pool deck: row of white loungers | conforms (east-edge row and north row) | top, pool_deck, front |
| Roof garden: raised planters, grasses, small yellow-green trees at the north end | conforms | top, rear_side, pool_deck |
| Penthouse: glazed to the pool deck at the south, solid with a door at the north | conforms | front, pool_deck |
| Penthouse: AHU with fan on the roof | conforms | top, front_corner |
| East block: membrane roof, two skylights, small plant | conforms | top, aerial |
| White facade under the overhang | conforms as plain white with glazing beyond; **stray plate and stepped parapet (P1 #2)** | right_side, climbing_face, aerial |
| Plaza: two-tone granite bands | conforms | front, aerial, wall_base_contact |
| Plaza: two raised planters of tall straw-coloured grasses (SW rectangle, SE L-shape) | conforms | plaza_planters, rim_interior, front |
| Plaza: low planted strip on the east edge | conforms | front, right_side, top |
| Plaza: bollards and lamp posts | conforms | aerial, right_side, front |
| Plaza: steps at the south edge | deviates (P2 #7) | front vs source front |
| West concrete sidewalk | conforms | left_side, front |
| Street trees in pits (8) | conforms | left_side, front, top |
| West and east streets with crossings | conforms | top, aerial |
| Parked cars on the east street | conforms (simple massing) | front, right_side, top |
| Neighbours: brick mid-rise and residential blocks | conforms (clay massing) | aerial, front, top |
| Materials hierarchy: white precast > glass > honey CLT feature > grey granite | conforms (CLT saturation P2 #6) | all whole-envelope views |

## 4. Camera validity

All 18 views are valid. None has its target occluded or clipped, and all are legible.
- rear is dim but legible.
- interior gives about 35% of the frame to a blank side wall, but the doors and the plaza beyond are legible.
- pool_deck is mostly water, but the loungers, balustrade, trough, penthouse glazing and roof garden are all legible.
- facade_close sits clear of the tree crowns.
- wall_base_contact and entrance both frame the shell foot correctly; they are the views that expose finding #1.
