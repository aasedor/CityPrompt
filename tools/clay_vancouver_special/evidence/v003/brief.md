You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/vspec/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, glass_close, balcony_rail, entry_stair, brick_base, east_side, side_entry, roof_ridge, interior)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a boxy two-storey Vancouver Special on a street corner, the street south and a side street east (the top view governs the plan): one wide, low-pitched front-gable roof of brown-grey asphalt shingles with the ridge running front to back over the middle, deep overhangs, brown fascias and gutters, open rakes with brown outrigger blocks under the front gable; red-orange brick veneer on the ground storey of the street front, white stucco on the upper storey and on every other wall, an exposed concrete foundation on the sides and rear; a long cantilevered balcony across the east two thirds of the upper front with a thick white slab fascia and a grey aluminium picket railing, a three-panel sliding door and a smaller window behind it, a wide three-light window on the upper left; under the balcony a white panelled front door with a glazed sidelight, a white casing, two coach lamps and a mailbox, opening off a raised concrete landing whose stair runs down eastwards along the front, with aluminium railings; wide three-light bronze aluminium windows with brick rowlock sills either side; small upright windows on the east side, the ground-floor suite door with its own concrete landing and a flight running down towards the street, brown downpipes at the corners; a lawn, shrubs, a front walk, sidewalks, boulevards and curbs on both streets, a board fence with a lattice top round the back yard and a row of cedars at the rear corner. The west and north faces (a small upper rear deck and a back stoop) are not visible in the front or oblique; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (boxy two-storey Vancouver Special: low wide front gable with deep overhangs, red brick ground storey under white stucco, long front balcony with aluminium picket railing, raised front landing and side-suite stair),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/vspec/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette and storey count, roof (pitch, front-gable ridge, overhangs, shingle courses, fascias, gutters, outriggers), brick ground storey (joints, rowlock sills) and stucco upper storey, balcony (slab, fascia, railing, extent), windows (bronze sliders, light count, sizes per floor, curtains), front door, sidelight, casing, lamps and mailbox, landing, front stair and railings, east side windows, side door, landing and flight, downpipes, concrete foundation, lawn, beds and shrubs, walks, sidewalks, boulevards and curbs, fence and lattice, cedars, street trees, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/vspec/v003/review/independent-review.md. Do not run the build.

This is version 3. The v002 review found 0 P0 and 3 P1. First, a pure-black slot 2-3 px wide ran the full length of both front rakes, between the brown rake fascia and the white rake soffit. Second, every brick mortar T-junction showed a near-black pit on a regular grid in brick_base and entry_stair. Third, the front camera did not match the locked front: the east (side-street) wall read at about 0.10 of the street-front width, against about 0.53 in the source, so the suite door, its stair and the east openings were slivers. The builder claims all three are fixed. The rake fascia is now deeper (0.30 m) and set lower, so its underside drops below the soffit lining. The soffit lining now runs into both rake fascias, so its end is buried in the board, and the corner return blocks were enlarged to stay proud of the deeper board. The head joints of the brick now span only between bed joints, on their own plane, so no head and bed joint pieces overlap at the Ts. The front camera now stands across the side street to the south-east at eye height (35 mm-equivalent framing), so the east wall reads at about half the street-front width, with the suite door, landing, flight and both east openings legible. Also claimed (P2): the north-east boulevard tree moved behind the rear_side camera, out of its frame. Verify each in the pixels: zoom along both front rakes in architecture_close, front and facade_close, look for black pits across the brick in brick_base and entry_stair, and measure the east-wall to street-front width ratio in front against the locked front. Do not take the builder's word.

The v002 fixes must still hold, so check each in the pixels:
- the trim has no black faces: gable apex fascias front and rear, rake ends, every downpipe elbow, offset and outlet, both top corners of the white front-door casing, and the stair-head post caps;
- each rake-to-eave corner is one closed brown return at one height, with no slot or step;
- the east wall keeps its front ~45% blank, with one ground window and the full-lite suite door mid-wall, an upright upper window stacked over each, and the side landing and flight at the door.

The v001 strengths must also still hold:
- a low wide front gable with outriggers;
- a brick ground storey under a stucco upper storey;
- the long front balcony with its picket railing;
- the raised front landing, with its stair running along the front;
- the oblique camera framing matched to the locked view.
