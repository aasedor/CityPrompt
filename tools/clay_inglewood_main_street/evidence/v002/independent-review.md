# Independent holistic review: clay-inglewood-main-street, v002 (RLASM v6.1 architectural clay)

Reviewer: independent; judged only rendered pixels against the locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders at full resolution, the four phone boards and the three sources. I made zoomed crops (written only to a new folder, `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/ingle-v002-review-crops-112651e4/`). I did not use metadata, counts, hashes or builder notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: all five v001 P1s are fixed in the pixels, but the new rear-wall opening system has a visible window/door collision on the one-storey lower bay's lane wall. A ground window and a service door share one position, a sill crosses the door, two lintels overlap, and a black void shows through. This one P1 blocks approval.

Counts: P0 = 0, P1 = 1, P2 = 10

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | rear (right end, x≈1385-1430, y≈790-850), rear_lane (x≈905-960, y≈555-815), rear_side (x≈520-545, y≈705-765) | On the lane wall of the one-storey lower bay, at its west end next to the corner block, a framed service door and a framed ground window are cut at the same position. The window's stone sill runs across the door leaf. The door's lintel and the window's lintel are two offset stone blocks that overlap, and between them a black see-through void is open in the wall. The door frame continues below the sill to the ground. The same collision shows in all three rear views. | The generic "service door + upper sash per block" rear recipe still emits a door for the lower bay, and the lower-bay-specific "ground windows instead" pass then adds a window at the same bay. The two boolean cuts and their sill/lintel parts overlap, and the overlapping cutters leave a hole through the carrier. | Give the lower bay's lane wall exactly one opening per bay. Either drop the service door there or move it to a clear bay at least 0.6 m from any window jamb. Then remove the duplicate lintel and sill and re-cut, so the carrier has no void that reads through. Add an assertion that no two opening rectangles on one carrier face overlap, including their sill/lintel extents. Re-render rear, rear_lane and rear_side. |
| 2 | P2 | front (x≈900-1030, y≈690-740), sidewalk_section (x≈900-1000, y≈800-830) | Where the 1.3 m brick furnishing strip narrows to the 0.7 m band round the extension, the inner edge steps with a small hook/notch instead of a smooth taper. | Two band profiles joined with an abrupt width change at the taper start. | Blend the inner edge over the length of the taper fillet. |
| 3 | P2 | top, aerial, front_corner | Every two-storey roof is the same smooth taupe. The top source shows gravel ballast on the corner, middle and next block and a white membrane on the east-end block. In the render the east-end block's roof is taupe. | One roof material is used for all gravel roofs, and the east-end block gets no membrane material. | Give the east-end roof the pale membrane tone. Optionally use a slightly warmer, mottled tone for the gravel roofs. |
| 4 | P2 | front, sidewalk_section, street_furniture, angle_parking | Street-tree crowns are still heavy faceted icosahedra on thin trunks. The source's young trees have small, open, leafy crowns. | Low-poly crown primitive. | Use a lighter crown of two or three smaller lobes, or reduce the crown further. |
| 5 | P2 | top | The north corner curb extension runs about 30% further east than in the top source. The source ends the extension sooner and leaves a small white-lined no-parking triangle before the first stall. | The extension length absorbs the source's hatched no-parking triangle. | Shorten the extension by about one stall width and paint the no-parking triangle with its edge lines. |
| 6 | P2 | top | Scaled to the building frontage, the sidewalk is about 15% wider and the travel lanes about 10% narrower than in the top source. The band order is correct. | Small cross-section dimension drift. | Move about 0.5 m from the sidewalk into the lanes. |
| 7 | P2 | front (end block, x≈1280-1440, y≈700-755) | The end block's storefront bulkhead is a flat dark slab with no panel moulding, while the other blocks show panelled green bulkheads. | The bulkhead panel recipe is not applied to the end block's dark storefront. | Apply the panel moulding there too. |
| 8 | P2 | right_side (right foreground), left_side, crosswalk_bulbout, rear_lane (left) | Context blocks (north-east beyond the crossing, the south-west corner, the buildings across the lane) have flush painted window rectangles and are prominent in some frames. The brief allows plainer context, so this is noted only. | The context is intentionally plain. | Optionally inset the context windows by 0.1 m, or tone them down. |
| 9 | P2 | (set coverage) | The brief lists facade_close, architecture_close and glass_close, but the candidate has 18 renders without them. storefront_close, roof_parapets, arched_windows and bracketed_cornice cover the same ground, so nothing is unjudgeable. | The view list was trimmed to 18. | Add the three roles, or remove them from the brief template. |
| 10 | P2 | storefront_close, street_furniture, sidewalk_section | Several storefront panes show a bright blurred horizontal smear, an interior light reflected in the glass, that reads as a stain on clay glass. | The interior emitter is reflected by the glazing material. | Lower the glass specularity or move the interior light. |
| 11 | P2 | left_side | The street wall fills only the right third of the frame at small scale. It is legible, but has little detail value. | Camera distance. | Move the camera about 30% closer. |

(P2 rows: #2 to #11 = 10. P1 rows: #1 = 1. P0 rows: none.)

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Section order (storefronts / sidewalk / brick furnishing strip / 50° angled parking / travel lane / double yellow / travel lane / parking / strip / sidewalk, mirrored) | conforms (widths within about 15%, P2 #6) | top, right_side, aerial, angle_parking |
| Curb extensions and tapers | conforms. Pale scored concrete, brick band following the curved curb, smooth reverse-curve tapers at both ends; the corner extension is slightly long (P2 #5) | top, front, crosswalk_bulbout, front_corner, right_side |
| Angled stall lines and edge line | conforms. Same "\" orientation as the source, about 50°, white edge line | top, angle_parking |
| Double yellow centre line | conforms | angle_parking, crosswalk_bulbout, right_side |
| Brick crossings with white edge lines at the intersection (both streets) | conforms | crosswalk_bulbout, left_side, top |
| Mid-block white ladder crossing | conforms (now with a brick band between the bars, which matches the top source) | front, right_side, aerial, top |
| Sidewalk scored joints | conforms | front, sidewalk_section, street_furniture |
| Brick furnishing strip and tree pits | conforms (small step at the band transition, P2 #2) | angle_parking, sidewalk_section, street_furniture, top |
| Young street trees | conforms (crowns still heavy, P2 #4) | front, sidewalk_section, top |
| Black lamps with red banners | conforms | crosswalk_bulbout, right_side, front |
| Bins | conforms | angle_parking, sidewalk_section, front |
| Bike hoops | conforms | street_furniture, sidewalk_section |
| Benches (on brick pads at the extensions) | conforms | crosswalk_bulbout, front_corner, top |
| Corner block: 3 bays, paired upper windows, corner pier, stone belt and white cornice turning the corner, side shopfronts on the cross street | conforms | front_corner, corner_entrance, street_furniture, rear_side |
| Lower bay (one storey, membrane roof, green storefronts, sign band, parapet with stone cornice) and the middle block's exposed west wall with 4 punched windows above it | conforms (matches source oblique) | front_corner (crop), street_furniture, top, rear_side |
| Middle block: cream pilasters, cream sign band, shallow segmental upper windows with stone rings, modillioned white cornice, raised stepped parapet with name panel | conforms | roof_parapets, front_corner, aerial |
| Bracketed-cornice block: dark bracketed metal cornice, deeper segmental cream hoods, dark sign band, central console clear of the window heads | conforms | bracketed_cornice, front, right_side |
| Round-arched block: semicircular heads in brick voussoir rings, corbelled brick cornice | conforms | arched_windows, right_side, aerial |
| End block: tallest, cream stone fascia, cream end pier, tall flat-headed upper windows | conforms | right_side, front_corner, front, aerial |
| Storefront glazing, transoms, bulkheads, glazed doors | conforms (end block bulkhead unpanelled, P2 #7; glass smear, P2 #10) | storefront_close, front, sidewalk_section, corner_entrance |
| Blade signs | conforms | front, corner_entrance, street_furniture |
| Roofs and parapets | conforms in form (flat roofs inside brick parapets, coping, rooftop units); tone simplified (P2 #3) | roof_parapets, top, aerial, rear |
| Back lane and rear walls | **deviates**: coursed brick, framed glazed sashes with reveals, sills and lintels are present, but there is an opening collision with a void on the lower bay's rear (P1 #1) | rear, rear_lane, rear_side |
| South-side context row | conforms (plainer, as allowed) | right_side, front, aerial |
| Materials hierarchy (red brick body, cream stone/pilasters/cornices, dark metal cornice, green frames and bulkheads, pale concrete, red brick pavers, dark asphalt, white/yellow paint) | conforms | all |

## 4. Camera validity

All 18 renders are valid. No target is occluded or clipped, and every view is legible.
- left_side: the target is small, in the right third of the frame, but legible (P2 #11).
- rear_lane: the near right wall is a long blank stretch, but the lane, the rear openings and the defect in P1 #1 are legible.
- storefront_close is tightly framed on one bay, and bracketed_cornice and arched_windows are steep upward views; all are legible and show depth (reveals, sill returns, console projection).
- The three detail roles named in the brief but not rendered (facade_close, architecture_close, glass_close) are logged as P2 #9. Their content is visible in other views.

## 5. Previous-version (v001) findings: are they resolved in the pixels?

1. **Corner block stretched across two lots: RESOLVED.** front_corner, corner_entrance and street_furniture show a 3-bay corner block with tight pairs of upper sashes. Then a separate one-storey lower bay with a pale membrane roof, green storefronts, a sign band and a parapet under a stone cornice. Above that roof is the middle block's coursed-brick west wall with 4 punched, framed windows on sills under lintels, matching the source oblique. The top view shows corner block, lower bay and middle block widths in about the source's 1 : 1 : 2.3 proportion.
2. **Middle block windows were semicircular: RESOLVED.** roof_parapets (zoomed) and front_corner show shallow segmental heads with stone rings. They are clearly different from the bracketed block's taller cream hoods and the round-arched block's semicircular brick rings. From the low street-level front view at distance the stone rings still read faintly arched, which is acceptable.
3. **End block not taller: RESOLVED.** right_side, front_corner and aerial show the end block clearly above its neighbour, with an exposed side wall above the neighbouring roof, much taller flat-headed upper windows under stone lintels, a cream fascia and a cream end pier.
4. **Curb extensions all brick with 45° chamfers: RESOLVED.** crosswalk_bulbout, front, top and right_side show pale scored concrete extensions with a narrow brick band following the curved curb, small brick pads under the benches, and smooth reverse-curve tapers at both ends. The south side mirrors the north. Only a small step remains where the strip narrows (P2 #2).
5. **Rear windows flat painted rectangles, no coursing: RESOLVED, but the new opening system introduced P1 #1.** rear and rear_lane show coursed-brick rear walls with framed, glazed two-light sashes in visible reveals, on stone sills under stone lintels, plus framed service doors. However, on the lower bay's lane wall a door and a window collide, leaving a black void.

The builder's cheap P2 claims, checked in the pixels:
- Bulkhead panel mouldings: present on the green bulkheads (front, sidewalk_section). Absent on the end block's dark bulkhead (P2 #7).
- Smaller tree crowns: the crowns read somewhat lighter but are still heavy faceted forms (P2 #4).
- Brick band under the ladder crossing: present (front, right_side, aerial).
- Taller central parapet with a larger name panel: present (roof_parapets, front_corner).
- Bracketed-cornice middle console between two windows, clear of the heads: present (bracketed_cornice).
- Opaque car cabins: present (angle_parking, front).

What v001 got right still holds:
- section order, 50° stalls and the edge line
- the double yellow centre line
- brick crossings with white edge lines and the ladder crossing
- black lamps with red banners, bins, bike hoops and benches
- the corner pier, stone belt and white cornice turning the corner
- the middle block's cream pilasters, sign band and modillion cornice
- the dark bracketed cornice
- the round-arched block's corbel table
- storefront glazing with transoms and doors set back from the brick pier faces
