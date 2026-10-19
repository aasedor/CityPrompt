You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/rink/v004
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/rink/v004/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions, ice, dasher boards (board, glass, posts, rail), deck, tree island (ring wall, glass ring, tree, ornaments, star), chalets (count and arrangement, walls, counters, awnings, snowy roofs, garlands), benches and skating aid, setts, lamps, town fronts, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/rink/v004/review/independent-review.md. Do not run the build.
This is version 4. The v003 review found 0 P0 and 4 P1: every tree ornament an axis-aligned cube reading as dice or gift boxes, some red and gold cubes interpenetrating, far sparser than the source's dense round baubles and warm lights; the front view's handrail reading bare from the ice because the garland hung on the outer (deck) face, and the east chalets showing only as small gable tips at the right edge instead of the source's large right-hand foreground; the aerial camera so low that the near south-east frontage hid the whole near long row of six chalets, one short-row chalet and about a third of the rink; the west (salmon) town front carrying only two window rows with a blank two-storey band up to the eave. The builder claims every one is fixed (the cubes replaced by smooth round baubles, red and gold, hung just under alternate bough tips with smaller ones on the upper skirts, and a small warm light on every bough tip; a lush garland laid along the top of the dasher handrail, reading from both the ice and the deck, with round red baubles and warm lights on both faces; the front camera standing on the ice just inside the east boards near the south end at about 2.2 m, looking almost due north so the garlanded handrail and the east chalet row with their wreathed gables run large down the right of the frame and the tree stands left; the aerial raised to about a 50-degree depression with a longer lens so the whole rink, all twenty chalets and the deck read inside the frontage ring; window rows up to the eaves on every town front, three rows on the west front). The v003 fixes must still hold: separate chalets with about 1 m of setts between the eaves and a ridge board on every roof; the tree as layered drooping fir skirts in two greens with no soil from above and a gold star; the side and rear views holding the whole tree and star. Verify each in the pixels; do not take the builder's word.
