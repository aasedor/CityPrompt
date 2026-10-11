You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/fire/v007
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, apparatus_bays, soffit_corner, tower_clock, loggia_close, apron_contact, interior, rear_door)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a two-storey oxblood panel fire station whose upper storey cantilevers over a glazed apparatus hall with four glazed bays on the south apron under a lit soffit edge; a deep glazed loggia in the south-west of the upper storey; a white membrane roof; a slender glass clock tower at the south-east corner standing proud of the front; flagpole, memorial wall, benches and a small flat shelter on the forecourt. The north face is not visible in any source; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (cantilevered red box over the glazed hall, four bays, lit soffit, south-west loggia, glass clock tower with sign band, appliances visible through the bays),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/fire/v007/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, bay count and rhythm, cantilever and soffit, loggia, tower and clock, forecourt elements, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/fire/v007/review/independent-review.md. Do not run the build.

This is version 7. The user lifted the three-version cap and asked for every building to be carried to a review with zero P0 and zero P1. The v006 independent review found 0 P0, 4 P1 and 7 P2: P1 the south-west corner of the upper box was still a separate red block, proud of the west sill band with a seam and a lower bottom; P1 the lit line on the west face was broken (missing the north-west vertical, the south-west vertical, the notch risers and the sill band bottom, with the top line at the loggia head instead of the parapet); P1 the clocks and sign bands faced south and east, where the sources show them on the south and west faces; P1 the south ground storey read as a continuous storefront with sidelights and no piers, with the bays bunched east, where the sources show four bays between broad grey piers from about 17 to 79 percent of the face. Verify each in the pixels of this version; do not take the builder's word. Report every remaining P0 and P1 precisely, and say for each v006 finding whether it is resolved in the pixels.
