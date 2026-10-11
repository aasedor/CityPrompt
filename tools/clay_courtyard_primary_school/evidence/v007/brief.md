You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/school/v007
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, entrance_passage, courtyard, fins_close, canopy_contact, penthouse_terrace, interior, playground)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a mid-block corner primary school: a two-storey brick U around a south-facing playground, party walls to the west and north, a two-storey hall block at the north with a paved roof terrace, a corten-clad third storey over the north-west block, a south-east entrance block whose ground floor is an open concrete-framed passage, a corten canopy over the passage mouth and the east edge of the playground, strip windows with coloured fins, full-height classroom glazing to the court, gravel roofs with rails, a street fence with a gate. The catalogue label says Art Deco school; the locked pixels show this contemporary brick school and govern; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (brick U and playground, coloured fins, corten third storey, corner canopy and open passage, roof rails, fence and gate),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/school/v007/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, courtyard and wings, entrance passage and canopy, fins and glazing, corten storey, roofs and rails, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/school/v007/review/independent-review.md. Do not run the build.

This is version 7. The user lifted the three-version cap and asked for every building to be carried to a review with zero P0 and zero P1. The v006 independent review found 0 P0, 3 P1 and 7 P2: P1 the board-formed box was a short cube under the canopy's corner, set back from the street with pale forecourt paving and the fence running past it, where the sources show a narrow, long concrete wall from under the canopy corner to the street fence closing the east side of a dark fenced yard; P1 the south end face of the two-storey east wing carried a strip window with coloured fins, where both sources show blank brick above the canopy; P1 every roof was one pale grey close to the ground, where the source top shows warm tan gravel on the wings, the corten storey and the north-east terrace corner against a cool grey paved terrace. Verify each in the pixels of this version; do not take the builder's word. Report every remaining P0 and P1 precisely, and say for each v006 finding whether it is resolved in the pixels.
