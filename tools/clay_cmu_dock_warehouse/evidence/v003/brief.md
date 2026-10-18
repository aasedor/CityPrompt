You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/wh/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, dock_doors, entry_canopy, roof_units, east_windows, parapet_corner, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a single-storey mid-century distribution warehouse on a corner with the street south and a parking lane east (the top view governs the plan): a block of painted beige concrete masonry units with horizontal coursing, about 1.3 times as wide as deep, on a dock-height floor; four raised loading bays along the west half of the south face, each an overhead sectional door with a row of small lites inside a dark steel surround, black dock bumpers and yellow guide posts; east of them a glazed aluminium entry door and sidelight under a flat concrete canopy hung on two rods, a wide aluminium window beside it and a long cast-concrete landing with steps at its west end; punched windows on the east face (one low near the south corner, two high clerestories); a flat parapet with a thin pale metal coping round a grey membrane roof with two rooftop units, small vent domes and pipe vents. The north and west faces are not visible in the front or oblique; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (beige CMU box with coursing, four raised loading bays in dark surrounds with bumpers and guides, rod-hung entry canopy over the concrete landing, flat parapet roof with rooftop units),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/wh/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, height and proportions, CMU coursing, dock bays (doors, lites, surrounds, bumpers, guides, dock height), entry (door, sidelight, canopy, rods, window), landing and steps, east windows, parapet and coping, roof (membrane, units, domes, vents), apron and site, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/wh/v003/review/independent-review.md. Do not run the build.

This is version 3. The v002 independent review found: P1 dock doors and shelters still too tall for the wall (shelter tops about 68% of wall height against about 55% in the source, door tops about 60% against about 43%); P1 the front camera looking almost straight at the south face with the east face a sliver and empty ground below; P1 the grey cast-concrete dock base and steel lip under each door missing. The builder claims: 1.9 x 3.0 m doors on a 1.0 m dock floor (door tops at about 45% of the wall); a closer, lower three-quarter front camera from the south-east; a cast-concrete dock base along the bays and steel leveller lips. Verify each in the pixels and record for each v002 finding whether it is resolved; also confirm the six v001 findings resolved in v002 have not regressed.
