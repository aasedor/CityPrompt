You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/rink/v007
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/rink/v007/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions, ice, dasher boards (board, glass, posts, rail), deck, tree island (ring wall, glass ring, tree, ornaments, star), chalets (count and arrangement, walls, counters, awnings, snowy roofs, garlands), benches and skating aid, setts, lamps, town fronts, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/rink/v007/review/independent-review.md. Do not run the build.

This is version 7. The v006 review found 0 P0 and 1 P1: the v005 outward-chalet-trim finding was only partly fixed. In facade_close the outward gables carried a rake garland, lights and an apex bow, but the side-eave garland sat under the snow-slab overhang and did not show in any elevated view, and in square_aerial the rear-rake garland and bow were hairline slivers, so the ten rear-facing chalets still read as bare sheds, where the locked oblique shows a lit garland on every roof edge and a red bow on every outward gable. This is the second targeted fix of this finding. The builder claims it is fixed in the one shared chalet module (all twenty chalets): fat rounded garlands about 0.22 m in section now hang PROUD of the snow-slab lip, outboard of the slab end face on both rear rakes and outboard of the slab edge along both outer eaves, each with warm lights on its outer face; the rear apex carries a large red bow (two loops about 0.7 m across, a knot and two hanging tails). To keep the GLB under the cap the builder coarsened the tree baubles (6 by 4 sphere segments) and lengthened the sett cross-joint spacing from 0.60 m to 0.68 m. Verify in square_aerial, rear_north, left_side, rear_side, facade_close and aerial that every rear-facing chalet reads as decorated from above (a green garland line along every rake and eave and a red bow at every rear apex); do not take the builder's word.

Earlier fixes that must still hold. Check each in the pixels:
- the rink-facing gables with garland, lights, wreath and apex bow; the v006 front camera yawed west so the west chalet row shows left of the tree;
- the thin dark kick-plate at the foot of the dasher boards on the ice side; the dark timber deck with corners chamfered to the chalet line; denser warm lights on the ice-side face of the handrail garland; tree baubles clear of the bough tips (now slightly lower-poly);
- the whole tree, the gold star and sky inside the front frame, with the garlanded boards and the east chalet row as the right-hand foreground;
- the star seated on the leader tip by a short gold stem as two crossed solid star prisms, reading as a solid star from every side;
- the timber handrail and its garland each one continuous swept loop round the rounded rink corners, with no black wedge gaps at any joint;
- round red and gold baubles and a warm light on every bough tip; the garland on top of the handrail reading from the ice and the deck, with baubles and lights on both faces;
- the high aerial showing the whole rink and all twenty chalets inside the frontage ring; window rows up to the eaves on every town front; coursed setts with staggered cross joints;
- separate chalets with about 1 m of setts between the eaves and a ridge board on every roof;
- the tree as layered drooping fir skirts in two greens with no soil from above; the side and rear views holding the whole tree and star.
