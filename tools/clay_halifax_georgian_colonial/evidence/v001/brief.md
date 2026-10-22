You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hfxgeo/v001
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, facade_close, architecture_close, porch_columns, glass_close, cornice_chimneys, west_front, roof_deck, rear_wings, interior, garden_fence)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a free-standing two-storey Georgian house of red brick with pale stone dressings on a garden lot in Halifax, the street to the south (the top view governs the plan): a nearly square main block seven bays across the south front and four along each side, two shallow rear wings at the back corners with a recessed court between them; a hipped blue-grey slate roof truncated in a flat lead deck, with four tall brick chimney stacks carrying clay pots at the corners of the deck, the rear wings hipped into the main roof; the centre three bays of the south front form a slightly projecting pavilion with four giant stone pilasters, an entablature and a brick pediment with an oval cartouche, its slate gable running back into the hip; a one-storey portico of four Tuscan columns with a low hipped standing-seam metal roof on a stone platform with steps before a panelled door with a fanlight; tall sashes three panes wide with shouldered stone lintels with a raised centre and stone sills, a stone plinth, a stone first-floor string course and a white modillioned eave cornice, dark downpipes; formal box-hedge parterres to the west and north, brick paths, lawns and low hedges before the front, a tall iron railing along the street and the west side, conical evergreens and a dark tree by the west front, street trees, and a grey stone Georgian house with a gabled slate roof and dormers to the east. The west, north and east fronts and the rear wings are not visible in the front view; the north front and wings show only in the top view; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (free-standing red-brick Georgian house with a pilastered, pedimented centre pavilion, a four-column portico, a hipped slate roof with a flat deck and four corner chimney stacks, white sashes and stone dressings, in formal box-hedge gardens behind an iron railing),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hfxgeo/v001/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, plan (main block, pavilion projection, rear wings and court, portico), brick coursing, window grid (seven bays south, four per side), sashes and glazing bars, lintels and sills, plinth, string course, eave cornice and modillions, pavilion (pilasters, capitals, entablature, pediment, cartouche, gable roof), portico (platform, steps, columns, entablature, hipped seamed roof), front door and fanlight, roof (hips, slate courses, deck, chimney stacks and pots, wing hips), downpipes, parterres, paths, lawns and hedges, iron railing, trees, stone neighbour, streets and sidewalks, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hfxgeo/v001/review/independent-review.md. Do not run the build.
