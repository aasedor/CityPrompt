You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/condo/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, podium_retail, podium_setback, balcony_stack, roof_crown, corner_entry, interior, rear_lane)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a two-storey red-brick podium filling a corner lot with double-height storefronts between brick piers, a dark canopy band, ribbon windows with precast sills on the second storey, a precast cornice and a roof terrace behind a glass balustrade; an eleven-storey glass curtain-wall tower flush with the two street faces at the corner with continuous mullions, spandrel bands at every floor, two balcony stacks per face with glass balustrades and corner columns; a large pale metal mechanical penthouse with louvres on the tower roof behind a guard rail. Streets lie south and east; the north and west faces are only partly visible; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (brick podium with double-height storefronts and roof terrace, glass tower flush with the corner, balcony stacks, pale penthouse),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/condo/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, podium bays and storefronts, podium terrace and setback, tower curtain wall and spandrels, balcony stacks, penthouse, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/condo/v003/review/independent-review.md. Do not run the build.

This is version 3, the last permitted version. The v002 review found 1 P0 (the tower's two east corner columns carried down the podium's east brick face to grade, bisecting a second-storey window and a storefront bay) and 2 P1 (both east columns ending on dark inverted wedges at grade; front_corner taken from the south-west instead of the south-east street corner that the locked oblique shows). Verify each in the pixels of this version; do not take the builder's word. Record every remaining P0 and P1 precisely, since no further version will be built.
