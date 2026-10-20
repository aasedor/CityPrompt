# Independent holistic review: clay-inglewood-main-street v003 (RLASM v6.1)

Reviewer: an independent reviewer with no part in the build. I compared only the rendered pixels with the locked source pixels: sources/front.png, sources/oblique.jpg and sources/top.jpg. I opened all 18 renders/*.png at full resolution and all 4 boards/*.png. I made zoomed crops in a new folder, `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/ingle_v003_review_crops_8aecb5de/`. I also scanned every render for near-black pixels (max channel at or below 6) to find voids.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the v002 lane-wall P1 is resolved in the pixels and everything fixed earlier still holds. However, a new pure-black void slot is clearly visible at ground level between the end block's cream end pier and its east neighbour (right_side, and on the phone-03 board). It is the same class of defect as the v002 P1, so it blocks approval.

Counts: P0 = 0, P1 = 1, P2 = 8

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | right_side (px x≈1204–1214, y≈815–945); visible on boards/phone-03 right_side tile; a faint dark seam in aerial at the end-pier base | At the east end of the street wall, the cream end pier of the end block is full width in the upper storey and meets the neighbour wall. Below its small cap at about storefront-head height, the pier's ground stage is narrower. A slot about 6–8 px wide and about 130 px tall opens between the pier and the east neighbour. The pixels are pure black (RGB 0–1), the same kind of void through the envelope as v002's P1. It reads as a hole in the continuous street wall, not as a shadowed joint. | The ground stage (plinth or base) of the end pier is narrower than the upper shaft, and the end block's east party wall or return does not reach the neighbour context box. The camera therefore sees into an enclosed, unlit cavity (the block interior or a closed gap). | Make the end pier's ground stage the full width of the upper shaft, flush to the east line. Alternatively, close the end block's east party wall down to grade, or move the east context box so it abuts the end block with zero gap. Re-render right_side and confirm there are no near-black pixels in x 1190–1225, y 790–960. |
| 2 | P2 | rear | The lower bay's two lane openings (window at x≈1327 and door at x≈1417) are visible, but the foreground context roof cuts off the window's lower half and sill. | Camera height/target puts the lane-side context box in front of the ground band. | Raise or pull the rear camera back slightly, or aim lower so the lower-bay ground band clears the context roof. rear_lane and rear_side already prove the fix. |
| 3 | P2 | storefront_close | The frame crops the bulkheads and door bottoms, so the bulkhead panel mouldings and the door recess cannot be verified in this view. They can be in sidewalk_section and front. | Camera framed on transom and sign band. | Lower the target about 0.6 m, or widen the framing to include the bulkhead base. |
| 4 | P2 | sidewalk_section, street_furniture, front, angle_parking | Street-tree crowns are still heavy faceted blobs, wider than the slender young trees in the sources (top/oblique). | Crown radius and shape. | Narrow the crowns by about 20–25% and make them more upright and ovoid. |
| 5 | P2 | roof_parapets, front_corner vs oblique | The raised central parapet is a rectangular two-step block. Its name panel holds dark-green rectangles that read as a row of tiny windows. The oblique source shows a shouldered, curved-step gable with a plain panel. | Abstracted signage glyph blocks; orthogonal step profile. | Make the name-panel glyphs a lighter tone or fewer, flatter bars, and optionally round the step shoulders. |
| 6 | P2 | top vs top source | Plan subdivision: the lower bay runs full depth to the lane, whereas the source shows its rear stopping short at a recessed service yard. East of the middle block, the render has two narrow taupe roofs before the pale end roof (pale from about 90% of the frame). The source shows one gravel roof, then a brick wall and pale membrane from about 84%. The proportions are close, but not exact. | Block widths and depths set slightly off the top source. | Optionally pull the lower bay's rear wall back to form the service yard, and rebalance the bracketed and round-arched block widths against the top source. |
| 7 | P2 | corner_entrance, front_corner vs oblique | The corner block's ground-storey piers, including the corner pier, are cream stone. In the oblique source the corner and storefront piers read as brick with stone trim. | Shared storefront pilaster material. | Use brick for the corner block's piers, keeping the stone caps and base. |
| 8 | P2 | render set | The brief's listing names facade_close, architecture_close and glass_close, but no such renders exist. Exactly 18 renders are present, which matches the stated count. storefront_close, arched_windows and bracketed_cornice cover those roles. | The template listing does not match the delivered camera set. | Either render those three detail views or drop them from the brief template. |

(No P0 findings.)

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Section order, north to south: storefront wall, sidewalk, brick furnishing strip, 50° angled parking, travel lane, double yellow, travel lane, angled parking, strip, sidewalk, south row | conforms | top, right_side, angle_parking, aerial |
| Band widths (sidewalk ≈ parking ≈ lane, as in the top source) | conforms (sidewalk ≈100 px, parking ≈90, lane ≈75 vs source ≈95/70/70) | top vs top source |
| Mirror on the south side | conforms | right_side, aerial, front |
| Curb extensions and tapers (cross-street corner and mid-block, reverse-curve tapers) | conforms | top, crosswalk_bulbout, front_corner, right_side |
| Angled stall lines and edge line | conforms | angle_parking, top, aerial |
| Double yellow centre line | conforms | angle_parking, crosswalk_bulbout, right_side |
| Brick crossings with white edge lines over both streets | conforms | crosswalk_bulbout, left_side, top |
| Mid-block white ladder crossing (with brick band) | conforms | right_side, front, top, front_corner |
| Sidewalk scored joints | conforms | sidewalk_section, front, corner_entrance |
| Brick furnishing strip and tree pits | conforms | street_furniture (pit visible), angle_parking, top |
| Young street trees | deviates (P2 #4: crowns heavy) | sidewalk_section, street_furniture |
| Black lamps with red banners | conforms | crosswalk_bulbout, right_side, front |
| Bins | conforms | angle_parking, sidewalk_section, front |
| Bike hoops | conforms | street_furniture, sidewalk_section, corner_entrance |
| Benches (on brick pads at the bulbouts) | conforms | crosswalk_bulbout, corner_entrance, top |
| Corner block: 3 bays of paired upper sashes split by a pier; stone belt and white cornice turn the corner; side shopfronts near the corner | conforms; pier material deviates (P2 #7) | corner_entrance, front_corner, rear_side, left_side |
| Lower bay: one storey, membrane roof, two storefronts, sign band, stone cornice | conforms | front_corner, street_furniture, top |
| Middle block: cream pilasters, cream sign band, segmental windows with stone rings, modillion cornice, raised central parapet with name panel; exposed west wall with 4 framed windows | conforms; name-panel glyphs P2 #5 | roof_parapets, front_corner, aerial, rear_side |
| Bracketed-cornice block: dark bracketed metal cornice with end consoles over segmental windows, dark sign band | conforms | bracketed_cornice, front, aerial |
| Round-arched block: round-arched upper windows, brick voussoir rings, corbelled brick cornice (corbel table) | conforms | arched_windows, front, aerial |
| End block: tallest, cream stone fascia, cream end pier, tall flat-headed windows | conforms in form; end-pier ground stage defective (P1 #1) | right_side, front, aerial |
| Storefront glazing, transoms, panelled bulkheads, glazed recessed doors | conforms (bulkhead panels seen in sidewalk_section; storefront_close crops them, P2 #3) | storefront_close, sidewalk_section, front |
| Blade signs | conforms | front, corner_entrance, right_side, street_furniture |
| Roofs and parapets: flat roofs inside brick parapets with coping, rooftop units; east-end roof pale, others taupe | conforms | top, roof_parapets, rear, front_corner |
| Back lane: asphalt lane; rear walls coursed brick with framed, glazed, reveal-set openings on stone sills under stone lintels | conforms | rear_lane, rear, rear_side |
| South-side context, cross-street corners, low buildings beyond the lane | conforms (plain massing) | right_side, aerial, crosswalk_bulbout, rear_lane |
| Materials hierarchy: red brick, cream stone trim, green storefront frames, dark metal cornice, pale concrete, red brick pavers, asphalt | conforms | all |
| Plan proportions against the top source (block widths, lower-bay depth) | deviates slightly (P2 #6) | top |

## 4. Camera validity

- All 18 renders are valid: none has the target occluded, the asset clipped or the content illegible.
- rear: the foreground lane-side context roof hides the lower half of the lower bay's lane window. The view stays legible, and rear_lane and rear_side show the wall in full (P2 #2).
- storefront_close: the bottom edge crops the bulkheads and door bottoms (P2 #3).
- left_side: the camera has moved closer, as claimed. The corner block and the start of the street wall now fill the right half and are legible. The left half is still mostly road and sky (acceptable).
- aerial: the near south-side context roofs occlude the south sidewalk band, which is expected at this angle. The north street wall and the street are fully legible.
- bracketed_cornice and arched_windows are worm's-eye views, but legible and correctly targeted.
- facade_close, architecture_close and glass_close are named in the brief listing but not rendered (P2 #8).

## 5. Previous-version findings

**v002 P1 (lane wall of the lower bay, west end):** **Resolved in the pixels.**
- rear_lane: the service door sits at the west end, next to the corner block. The ground window sits about 3 m east of it. They are separate openings with solid brick between them. Each has its own stone lintel, and the sill belongs to the window alone and does not cross the door. Both are framed and glazed in reveals, and no black void shows.
- rear: the lower bay's lane wall shows exactly one window and one door, separate, each with its own lintel.
- rear_side: the same window-then-door pair shows on the lower bay, with the middle block's own ground window beyond the junction.
- The near-black scan finds 0 void pixels in rear and rear_side, and 4 isolated frame-shadow pixels in rear_lane.
- The two-storey rear walls look unchanged. No openings appear to be missing.

**Cheap P2s claimed for v003:**
- East-end (cafe) block roof is pale membrane, other two-storey roofs taupe: **confirmed** (top, aerial, right_side).
- left_side camera closer: **confirmed** (the target now fills the right half of the frame).

**v002 fixes, all still hold:**
- Corner block: 3 bays of paired sashes split by a narrow pier; belt and white cornice turn the corner: **holds** (corner_entrance, front_corner).
- Lower bay: one storey, membrane roof, two storefronts, sign band and stone cornice: **holds** (front_corner, street_furniture, top).
- Middle block's west wall: exposed coursed brick with 4 framed upper windows: **holds** (front_corner, rear_side).
- Middle block's segmental heads with stone rings: **holds** (roof_parapets).
- Round-arched block's brick voussoir rings: **holds** (arched_windows).
- End block tallest, with tall flat-headed upper windows: **holds** (right_side, front, aerial). Its end-pier base is the new P1.
- Curb extensions: pale scored concrete, brick band along the curb, small brick pads, reverse-curve tapers: **holds** (crosswalk_bulbout, top, front).
- Rear walls: coursed brick with framed, glazed openings in reveals, on stone sills under stone lintels: **holds** (rear_lane, rear_side).
- v002 P2s:
  - Bulkhead panel mouldings: **hold** (sidewalk_section).
  - Smaller tree crowns: still heavy, see P2 #4.
  - Brick band under the ladder crossing: **holds**.
  - Raised central parapet and name panel: **hold**.
  - Moved bracket console: **holds** (bracketed_cornice; the console clears the arch rings).
  - Opaque car cabins: **hold**.

**v001 strengths, all still hold:**
- Section order.
- 50° stalls with the edge line.
- Double yellow centre line.
- Brick crossings with white edge lines.
- Mid-block ladder crossing.
- Lamps with red banners, bins, bike hoops and benches.
- The middle block's cream pilasters, sign band and modillion cornice.
- The dark bracketed cornice.
- The corbel table.
- Storefront glazing with transoms and recessed doors.
