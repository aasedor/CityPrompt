You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/stepg/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, stepped_gable, entrance_stoop, wall_anchors, east_side, roof_chimney, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a narrow, deep Amsterdam canal house of dark red-brown brick with its crow-stepped gable facing the brick-paved street south and a side alley east (the top view governs the plan): a raised ground floor up a short stone stoop with iron rails to a panelled door with a transom in a white surround, two ground windows, three bays of white-framed small-paned sashes on each of three upper floors with stone sills, iron wall anchors at the floor lines, a stepped gable above the eaves with stone copings on each step and a single gable window, a steep dark tiled roof running back from the street between the front and rear gables, a brick chimney on the east slope; plain brick side walls with a few small windows; a tree and a black lamp standard on the street. The north face is not visible in the front or oblique; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (narrow dark-brick canal house with a crow-stepped street gable (copings, gable window), three bays of white small-paned sashes, iron anchors, stone stoop to the door),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/stepg/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count and proportions, brick and joints, stepped gable (step count, copings, gable window, pinnacle), sashes and sills, door, transom and surround, stoop and rails, anchors, side walls and windows, roof and chimney, street, tree and lamp, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/stepg/v003/review/independent-review.md. Do not run the build.

This is version 3. The v002 review found 0 P0 and 8 P1 (v001: 2 P0, 12 P1): brick still reading as siding (bed joints only, no head joints); the roof lighter than the brick; a second crow-stepped rear gable the sources do not have, with the chimney alone on the east slope; the two small east windows in the front third instead of over the rear tall window; a north face without white frames, sills, anchors or joints; front_corner and aerial framed far too wide; glass_close cropping the sash; a short umbrella-crowned street tree. The builder claims every one is fixed (pale bed and staggered head joints, a near-black roof, a plain raked coped rear gable with a two-pot chimney at its apex, the small east windows stacked over the first tall rear window, the north face given white six-over-six sashes, sills, anchors and joints, close high framings for the oblique and aerial, glass_close centred on a first-floor sash, a tall oval-crowned tree to the eaves). Verify each in the pixels; do not take the builder's word.
