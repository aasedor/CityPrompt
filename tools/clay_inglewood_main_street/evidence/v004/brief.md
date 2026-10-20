You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ingle/v004
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, storefront_close, bracketed_cornice, arched_windows, corner_entrance, angle_parking, crosswalk_bulbout, street_furniture, sidewalk_section, roof_parapets, rear_lane)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a street option, not a building: a straight run of Calgary's Inglewood main street (9 Avenue SE), the top view governing the plan. The north side is a continuous street wall of early-1900s two-storey red-brick commercial blocks with flat gravel roofs inside parapets and a back lane behind: a corner block on the cross street with paired upper windows, a stone belt and a white cornice that turns the corner; a middle block with cream pilasters, a cream sign band, segmental-arched upper windows, a modillioned white cornice and a raised stepped central parapet with a name panel; a narrower block with a dark bracketed metal cornice over segmental windows and a dark sign band; a block with round-arched upper windows and a corbelled brick cornice; and a taller end block with a cream stone fascia, a cream end pier and tall flat-headed windows. Storefronts have large glazing with transoms, panelled bulkheads, glazed doors and blade signs. The section from the north building line: a wide pale concrete sidewalk with scored joints and a red brick-paver furnishing strip at the curb (tree pits with young trees, black lamp standards with red banners, bins, bike hoops); 50-degree angled parking with white stall lines and an edge line; one travel lane each way divided by a double yellow centre line; the same parking, strip and sidewalk on the south side. Curb extensions at the cross street (with benches and brick pads) and at a mid-block white ladder crossing; red brick-paver crossings with white edge lines over both streets at the intersection. The south-side row, the corners across the cross street and the low buildings beyond the lane are plainer context; the parked cars are simple clay placeholders. The pedestrians and dogs in the sources are not modelled. Awnings are not shown in the sources and are not modelled. Judge it as a street section: band order and widths, curb extensions, markings, surfaces, furniture, planting, the storefront street wall and pedestrian-scale finish, not storeys; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (historic two-storey red-brick storefront main street: wide sidewalks with brick furnishing strips, young trees and banner lamps, angled parking each side, curb extensions and brick crossings),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ingle/v004/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: section order and widths (storefronts, sidewalk, furnishing strip, angled parking, travel lanes, centre line, mirror), curb extensions and tapers, angled stall lines and edge lines, double yellow centre line, brick crossings and ladder crossing, sidewalk joints, brick strips and tree pits, young street trees, lamps with banners, bins, bike hoops, benches, corner block and its corner (pier, bands turning the corner, side shopfronts), middle block (pilasters, sign band, segmental windows, modillion cornice, raised parapet), bracketed-cornice block, round-arched block, end block (cream fascia and pier), storefront glazing, transoms, bulkheads and doors, blade signs, roofs and parapets, back lane, south-side context, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ingle/v004/review/independent-review.md. Do not run the build.
This is version 4. The v003 review found 0 P0 and 1 P1. At ground level on the east end of the street wall, between the end (cafe) block's cream end pier and the east neighbour, a slot about 6–8 px wide and about 130 px tall showed pure black in right_side (also on the phone-03 board and as a faint seam in aerial). The pier's ground stage looked narrower than its upper stage, and nothing closed the gap down to grade.

The builder claims it is fixed:
- **Cause:** the east neighbour context box started 0.10 m east of the end block, so a 9 cm gap ran from the sidewalk to the roof between the block's street wall and the neighbour; seen from the east, its inside rendered black.
- **Neighbour:** now bedded 2 cm into the end block's wall, so there is no gap at the party line. Its front sits 15 mm behind the block's street face, so the two fronts never share a plane.
- **End pier:** now one full-width cream pier from the sidewalk to its capital. It wraps 5 cm past the block end over the junction and is bedded 3 cm back into the neighbour's front; its capital widens to match.
- **Sweep:** this was the only block-to-neighbour junction on the north street wall. The blocks join each other with 1 cm overlaps at different setbacks, and the south-side context blocks overlap by 1 cm; no other gap runs to grade.

Cheap P2s the builder claims:
- **Corner block piers:** brick, with stone caps and plinths kept (P2 #7); the corner pier is brick too.
- **Name panel:** the raised parapet's name-panel lettering is a light stone tone instead of dark green blocks (P2 #5).
- **Street trees:** crowns about 20% narrower (P2 #4).
- **rear camera:** raised and pulled back so the lower bay's lane window and sill clear the context roof (P2 #2).

Verify in the pixels (right_side and aerial at the end block's east pier base; front_corner and corner_entrance for the brick corner piers; roof_parapets; rear); do not take the builder's word.

Everything fixed in v003 must still hold:
- **Lower bay lane wall:** the service door (x = -19.0) and the ground window (x = -15.8) apart, each with its own lintel, the window with its own sill, and no black void; no two rear-wall openings overlap on any block.
- **East-end (cafe) block roof:** the pale membrane.
- **left_side camera:** the closer framing down the cross street.

Everything fixed in v002 must still hold:
- **Corner block:** 3 bays with paired upper sashes split by a 0.3 m pier; the stone belt and white cornice turn the corner.
- **Lower bay:** the one-storey bay with a membrane roof, two storefronts, a sign band and a stone cornice.
- **Middle block's west wall:** the exposed coursed-brick wall above the lower bay, with four framed upper windows.
- **Middle block's windows:** segmental heads with stone rings.
- **Round-arched block:** brick voussoir rings.
- **End block:** the tallest, coping at 12.4 m, with tall 1.2 x 3.3 m upper windows.
- **Curb extensions:** pale scored concrete, a brick band following the curb, small brick pads and curved reverse-curve tapers.
- **Rear walls:** coursed brick with framed, glazed openings in reveals, on stone sills under stone lintels.
- **v002 P2s:** bulkhead panel mouldings, the brick band under the ladder crossing, the raised central parapet and name panel, the moved bracket console, opaque car cabins.

The things v001 got right must also still hold:
- the section order;
- 50-degree angled stalls with the edge line;
- the double yellow centre line;
- the brick crossings with white edge lines;
- the mid-block ladder crossing;
- the black lamps with red banners, bins, bike hoops and benches;
- the middle block's cream pilasters, sign band and modillion cornice;
- the dark bracketed cornice;
- the corbel table;
- the storefront glazing with transoms and recessed doors.
