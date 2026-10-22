You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/steps/v004
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, central_stair, seating_terraces, parapet_pots, side_stair, chapel_top, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is an open space, not a building: a Cycladic hillside stair-plaza, a long strip climbing north between rows of white cubic houses (the top view governs the plan): a narrow central stair with two metal handrails and a landing at every terrace level; broad terraces on each side with white-rendered risers, a seating step and stone-paved platforms; a white parapet with terracotta pots of red geraniums along the east terraces and a narrow side stair beyond it; a low white parapet on the lowest west terrace; white houses with blue doors and blue-framed windows stepping up both sides, one draped in magenta bougainvillea; a blue-domed chapel at the top on the west and a white belfry with a blue cupola at the foot on the east; a paved lower plaza. The hillside below the terraces is represented as solids on a level base. Judge it as an open space: plan legibility, routes, terraces, edges, planting and pedestrian-scale finish, not storeys; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (white Cycladic stair-plaza: central handrailed stair between terraced seating platforms, parapet with geranium pots, side stair, blue-trimmed white houses, bougainvillea, chapel dome and belfry),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/steps/v004/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions, central stair (steps, landings, handrails), terraces (risers, seats, paving), east parapet and pots, side stair, west parapet, flanking houses (doors, windows, heights stepping), bougainvillea, chapel and dome, belfry and cupola, lower plaza, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/steps/v004/review/independent-review.md. Do not run the build.

## Context for this review (v004, a second pass reopened by the user)

v004 is v003 with its bougainvillea and pot planting replaced by the shared planting kit (kit v003.1,
`tools/clay_planting_kit_showcase`, whose own review judged it able to close this family's bougainvillea finding), plus
targeted fixes for v003's two plan P1s. Score it against the candidate v003 (P0 = 0, P1 = 3,
`evidence/v003/independent-review.md`). Judge from the pixels.

- **v003 P1 #1, bougainvillea balloons with no drape:** both plants are now kit `wall_drape` climbers built from
  instanced leafy and flowering sprays (three-bract clusters), trailing canes and a woody frame over a hidden dark carrier;
  there are no balloon or ovoid primitives. West: trained from a terracotta pot on the second west terrace at the house's
  south-east corner (clear of the door jamb), up the corner and over the roof edge across the head of the east facade
  (door and windows cut clear) and round onto the south wall; look at architecture_close, front, front_corner, aerial,
  top. East: a cascade down the inner face of the east parapet over four terraces (yk(0) + 1.4 m to yk(4) - 1 m), over
  the coping and a little down its outer face; look at front, front_corner, side_stair, top.
- **v003 P1 #2, the foot of the strip did not splay west:** the two lowest west terraces now run west of the house line
  to a slanting low parapet (3.6 m west at the foot, 5.0 m at the bougainvillea house: top view, it slants south-east
  down to the plaza), with geranium pots on its coping. A 2.4 m diagonal stair runs outside the parapet from the lower
  plaza up to a landing beside the bougainvillea house, and the south-west corner house is moved west beyond the stair
  (face 8 m west of the house line). Look at top, front_corner, aerial.
- **v003 P1 #3, pergola in the seating terraces:** the pergola now stands on the roof terrace of east house 1, east of the
  side stair, its beams running into the wall of the taller house to the north; the side stair and the east terraces
  are clear. The y-beams now end inside the front beam and the posts rise into the beams (the v003 black void at the post
  head is closed). Look at front, side_stair, front_corner, top.
- **P2 #5:** the geranium pots are kit pots (0.19 m radius, 0.30 m tall) with clustered corymb flower heads; the two pots
  on the plaza floor are gone.
- Unchanged from v003: the stair, terraces, houses, chapel, belfry and cameras. The front camera does not reach the new
  west parapet (it is about 3.6 m further west than before); the plan reads in top, front_corner and aerial.
- Dark pixels inside the climber canopies are leaf-gap shadow; please separate them from any slit in the geometry.
