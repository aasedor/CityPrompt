You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/rink/v006
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/rink/v006/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions, ice, dasher boards (board, glass, posts, rail), deck, tree island (ring wall, glass ring, tree, ornaments, star), chalets (count and arrangement, walls, counters, awnings, snowy roofs, garlands), benches and skating aid, setts, lamps, town fronts, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/rink/v006/review/independent-review.md. Do not run the build.

This is version 6. The v005 review found 0 P0 and 1 P1: every chalet's outward-facing (rear) gable and both outer eaves were bare dark-brown boxes with only a ridge board (no garland, no lights, no bow), so the ten chalets seen from behind in square_aerial and the two foreground chalets in facade_close read as undecorated sheds, where the locked oblique shows a lit green garland along every eave and a red bow at the apex of every outward gable. The builder claims it is fixed in the one shared chalet module (so all twenty chalets carry it): a green garland with warm lights hung under both rear rakes, a red bow at the rear gable apex, and a green garland with warm lights along both outer side eaves just inside the eave edge. Verify in facade_close, square_aerial, front_corner, aerial and the side and rear views; do not take the builder's word.

The builder also claims these v005 P2s were addressed: the front camera yawed about 4 degrees west so the west chalet row shows to the left of the tree (the east row stays the right-hand foreground); a thin dark kick-plate along the foot of the dasher boards on the ice side so the board-to-ice line reads; the deck darkened to the source dark-timber tone and its corners chamfered to the chalet line so no square pad sticks out past the chalet ring; more warm lights on the ice-side face of the handrail garland; tree baubles pushed out past the bough tips so none are half buried in the skirt beneath.

Earlier fixes that must still hold. Check each in the pixels:
- the whole tree, the gold star and sky inside the front frame, with the garlanded boards and the east chalet row as the right-hand foreground;
- the star seated on the leader tip by a short gold stem as two crossed solid star prisms, reading as a solid star from every side, not a floating sliver;
- the timber handrail and its garland each one continuous swept loop round the rounded rink corners, with no black wedge gaps at any joint;
- round red and gold baubles and a warm light on every bough tip; the garland on top of the handrail reading from the ice and the deck, with baubles and lights on both faces;
- the high aerial showing the whole rink and all twenty chalets inside the frontage ring; window rows up to the eaves on every town front;
- separate chalets with about 1 m of setts between the eaves and a ridge board on every roof; rink-facing gables with garland, lights, wreath and apex bow;
- the tree as layered drooping fir skirts in two greens with no soil from above; the side and rear views holding the whole tree and star.
