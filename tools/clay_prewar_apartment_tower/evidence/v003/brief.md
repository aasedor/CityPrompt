You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/prewar/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, entrance_marquee, limestone_base, fire_balconies, cornice_balustrade, tank_house, interior, rear_court)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a twelve-storey New York pre-war apartment tower on a corner with streets south and east: a two-storey limestone base with rusticated joints and tall windows, the entrance on the south face under a dark metal marquee on tie rods; ten storeys of red-brown brick above a limestone belt course, limestone quoin strips at every corner, a stacked limestone-framed bay over the entrance, flat stone lintels and sills on dark double-hung windows, stacked iron balconies on both street faces, a band under the top storey, a deep limestone modillion cornice under a balustraded parapet with pedestals and corner urns; on the dark roof a brick water-tank house with stone quoins under a copper pyramid, a steel grating catwalk round it, plant units and three brick chimneys with clay pots; an iron areaway railing along the east sidewalk. The north and west faces are not visible in the front or oblique; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (red-brown brick on a rusticated limestone base, quoins, stacked iron balconies, deep cornice and balustrade, copper-roofed water-tank house, entrance marquee),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/prewar/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, base and rustication, entrance and marquee, window rhythm, lintels and sills, quoins, stone bay, iron balconies, cornice and balustrade, tank house, catwalk and chimneys, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/prewar/v003/review/independent-review.md. Do not run the build.
This is version 3. The previous independent review (v002) found: P1 a full-height stone pier over a window column, halving it on every brick storey; P1 the entrance group mid-face where the sources put it hard by the south-east corner with a wide stone-framed bay at the corner of the east face; P1 a black slit and stepped coronas where the cornice meets the corner pedestal; P1 the rooftop catwalk a near-black ring at deck level where the source has light galvanized grating raised on posts with a stair; P1 the entrance_marquee camera clipping the marquee and door. The builder claims: the separate pier is removed; the entrance, marquee and balcony stack moved to the second bay from the south-east corner with the wide projecting stone bay in the corner bay, and a matching stone bay at the south end of the east face; a stone corner block enclosing the cornice junction at every corner under the pedestals; the catwalk as light grating with bearing bars, raised 0.9 m on posts, with light rails and a short stair; the entrance_marquee camera re-aimed with a wider lens to frame the marquee and door whole. Verify each in the pixels and record for each v002 finding whether it is resolved.
