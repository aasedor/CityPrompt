You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ingle/v002
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ingle/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: section order and widths (storefronts, sidewalk, furnishing strip, angled parking, travel lanes, centre line, mirror), curb extensions and tapers, angled stall lines and edge lines, double yellow centre line, brick crossings and ladder crossing, sidewalk joints, brick strips and tree pits, young street trees, lamps with banners, bins, bike hoops, benches, corner block and its corner (pier, bands turning the corner, side shopfronts), middle block (pilasters, sign band, segmental windows, modillion cornice, raised parapet), bracketed-cornice block, round-arched block, end block (cream fascia and pier), storefront glazing, transoms, bulkheads and doors, blade signs, roofs and parapets, back lane, south-side context, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ingle/v002/review/independent-review.md. Do not run the build.
This is version 2. The v001 review found 0 P0 and 5 P1.
1. The corner block was stretched across two source lots: one full-height box carried about 9 evenly spaced single upper windows, where the top and oblique views show a 3-bay corner block with paired windows, then a separate bay with a lower membrane roof, and above that lower roof the middle block's exposed brick side wall with punched windows.
2. The middle block's upper windows had full semicircular heads, the same as the round-arched block, so the street wall lost its block-by-block window differences. The source has near-flat segmental heads under stone there.
3. The end block was the same height as its neighbour, with the same upper-window proportions, where the source front shows it clearly the tallest, with much taller upper windows.
4. The curb extensions were almost entirely red brick and tapered back to the parking lane with straight 45-degree chamfers, where the source has pale scored concrete, a narrow brick band following the curved curb, small brick pads and curved tapers.
5. The rear windows were flat dark rectangles painted flush on the wall, with no reveal, frame or glazing, and the rear walls had no brick coursing.

The builder claims each is fixed:
1. The corner block now ends at x = -20.4 (about 9.4 m of frontage, per the top view). It is 3 bays wide, with a tight pair of upper sashes over each bay, split by a 0.3 m brick pier; the stone belt and white cornice still turn the corner. A one-storey "lower bay" (6.6 m to the coping, pale membrane roof with plant) runs from there to the middle block, with two green storefronts, a sign band and a plain brick parapet under a stone cornice. Above its roof, the middle block's west wall is now a coursed-brick carrier with four punched, framed and glazed upper windows on stone sills under stone lintels, and a stone coping.
2. The middle block's upper windows now have shallow segmental heads (rise 0.13 m on a 1.0 m opening) with stone rings. The bracketed block keeps its deeper segmental cream hoods, and the round-arched block keeps semicircular heads, now as brick voussoir rings with no stone keystones.
3. The end block's coping is now 12.4 m (about 2.4 m above its neighbour), with upper windows of 1.2 x 3.3 m starting at 5.7 m under flat stone lintels; the cream fascia, end pier and stone cornice follow the new height.
4. Each curb extension is pale concrete with scored joints. A brick band follows the curb all the way round: 1.3 m wide (0.3 to 1.6 m in from the curb face) on the main run, narrowing to 0.7 m round the extensions and the corner return. Small brick pads sit under the benches. The tapers are lengthened (west 3.5 m, east 3.5 m) and rounded at both ends with 2 m fillets, so they are smooth reverse curves, not chamfers. The south side mirrors the north.
5. Every block's rear wall is now a coursed-brick carrier with cut openings: a framed service door and framed, glazed two-light upper sashes in about 130 mm reveals, on stone sills under stone lintels (the one-storey lower bay has ground windows instead).

Cheap P2s the builder claims:
- raised panel mouldings on the storefront bulkheads;
- young street trees with crowns about a third smaller;
- a brick band under the mid-block ladder crossing;
- the middle block's central parapet raised by about 0.8 m with a larger name panel;
- the bracketed cornice's middle console moved between two windows, clear of the window heads;
- opaque cabins on the clay cars.

Verify each in the pixels (top, front_corner, left_side, corner_entrance, roof_parapets, aerial, right_side, front, crosswalk_bulbout, angle_parking, rear, rear_lane, rear_side, arched_windows, bracketed_cornice, storefront_close); do not take the builder's word. The things v001 got right must still hold: the section order and 50-degree angled stalls with the edge line; the double yellow centre line; the brick crossings with white edge lines at the intersection and the mid-block ladder crossing; the black lamps with red banners, bins, bike hoops and benches; the corner pier, stone belt and white cornice turning the corner; the middle block's cream pilasters, sign band and modillion cornice; the dark bracketed cornice; the round-arched block's corbel table; the storefront glazing with transoms and recessed doors.
