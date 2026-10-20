You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/rink/v005
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, christmas_tree, market_chalets, dasher_boards, ice_surface, square_aerial, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is an open space, not a building: a cobbled city square with a rounded-rectangle ice rink, its long axis north-south (the top view governs the plan), ringed by low white dasher boards with clear glass panels; a dark timber deck round the boards; a tall decorated Christmas tree in a circular planter with a glass ring just north of the rink centre; a ring of dark timber market chalets with snow-laden pitched roofs, garlands and counters facing the ice, four on each short side and six on each long side; benches by the ice; old town fronts round the square as simplified context. Judge it as an open space: plan legibility, the rink, boards, tree island, chalets and pedestrian-scale finish, not storeys; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (rounded ice rink with glass-topped dasher boards round a decorated tree island, timber deck, snowy market chalets with garlands on four sides, cobbled square),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/rink/v005/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions, ice, dasher boards (board, glass, posts, rail), deck, tree island (ring wall, glass ring, tree, ornaments, star), chalets (count and arrangement, walls, counters, awnings, snowy roofs, garlands), benches and skating aid, setts, lamps, town fronts, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/rink/v005/review/independent-review.md. Do not run the build.
This is version 5. The v004 review found 0 P0 and 3 P1: in the front view the tree ran off the top of the frame, the spire tip touching the edge and the gold star cut off, where the locked front shows the whole tree with the star and sky above; the gold star floated about 4-6 px above the spire tip with sky between, and as a flat plate it read from the east and west as a thin floating gold sliver; the handrail garland was built of straight segments round the rounded rink corners and every joint left a pure-black wedge gap, two showing as large black slashes in the market_chalets foreground. The builder claims every one is fixed (the front camera tilted up about 5 degrees with a slightly wider lens so the whole tree, the star and sky sit inside the frame while the garlanded boards and the east chalet row stay the right-hand foreground; the star seated on the leader tip by a short gold stem and built as two crossed closed star prisms, north-south and east-west, so it reads as a solid star from every side; the timber handrail and the garland each built as one continuous closed tube swept round the rounded outline with mitred joints, so the corners bend smoothly with no gaps). The v004 fixes must still hold: round red and gold baubles and a warm light on every bough tip; the garland lying on top of the handrail reading from the ice and the deck, with round baubles and lights on both faces; the east chalet row as the large right-hand foreground of the front; the high aerial showing the whole rink and all twenty chalets inside the frontage ring; window rows up to the eaves on every town front. The v003 fixes must also still hold: separate chalets with about 1 m of setts between the eaves and a ridge board on every roof; the tree as layered drooping fir skirts in two greens with no soil from above; the side and rear views holding the whole tree and star. Verify each in the pixels; do not take the builder's word.
