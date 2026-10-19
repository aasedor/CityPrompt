You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/georg/v004
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, doorcase_balconette, mansard_dormers, chimney_stacks, east_side, roof_lead, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is the five-bay end house of a London Georgian terrace on the street (south) beside a paved side passage (east), a lower stuccoed terrace to the west beyond a garden wall and gate (the top view governs the plan): three storeys of yellow-brown stock brick with six-over-six white sashes under gauged brick flat arches and stone sills, the first-floor windows tallest and the centre one a French window with an iron balconette on the stone doorcase below; a black panelled door with a rectangular fanlight between stone pilasters under a frieze; a stone string course and a brick plinth; a short parapet with a stone coping, then a steep grey slate mansard with five dormers and a flat lead roof behind it with a skylight; the side walls rising as coped parapets carrying long chimney stacks with rows of clay pots; a small hipped rear wing; a black lamp standard and a plane tree. The north face is not visible in the front or oblique; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (five-bay yellow stock-brick Georgian house, white sashes under flat arches, stone doorcase with balconette, slate mansard with five dormers, side parapets with potted chimney stacks),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/georg/v004/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count and bay rhythm, brick and joints, sashes (sizes per floor, bars, sills, flat arches), doorcase (pilasters, frieze, fanlight, door), French window and balconette, string course and plinth, parapet and coping, mansard (pitch, slate, dormers), lead flat and skylight, side parapets and chimney stacks with pots, side wall windows, passage, garden walls and gate, lamp, tree, neighbour terrace, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/georg/v004/review/independent-review.md. Do not run the build.
This is version 4. The v003 review found 0 P0 and 1 P1 (v002: 2 P1, v001: 10): the rear range not matching the locked top view: the east rear extension's flat roof brick-coloured with no rooflight, reading as an open yard, where the source shows a grey roof inside a stone rim with a long hipped glazed lantern; the hipped rear wing with overhanging eaves where the source encloses its roof in a coped parapet. The builder claims both are fixed (a grey lead roof inside a stone rim on the extension carrying a long hipped glazed lantern on a pale upstand with glazing bars; a coped brick parapet round the wing's north and side edges with its hipped slate roof set inside it). Verify each in the pixels; do not take the builder's word.
