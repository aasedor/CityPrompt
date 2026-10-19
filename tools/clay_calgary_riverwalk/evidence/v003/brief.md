You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/rwalk/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, promenade_section, river_railing, planters_benches, riprap_bank, peace_bridge, aerial_section, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a street option, not a building: a straight run of Calgary's RiverWalk on the south bank of the Bow (the top view governs the plan): from the river inland, blue-green water, a rip-rap bank of grey boulders, a riparian strip of native grasses, shrubs and cottonwoods, a slender bronze handrail on low posts, a wide pale concrete promenade with scored joints for walking and cycling, a building-side edge of stone-faced raised planters and gabion walls with timber benches and small trees, and pale-brick mid-rise apartment blocks with ground-floor patios as context; the red helical-truss Peace Bridge lands at the north end and crosses to a wooded far bank. The skyline and mountains in the sources are distant context and not required. Judge it as a street section: band order and widths, surfaces, edges, furniture, planting and pedestrian-scale finish, not storeys; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (riverside promenade between a planted rip-rap bank with a slender rail and a building edge of stone planters and benches, cottonwoods, the red Peace Bridge),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/rwalk/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: section order and widths (river, rip-rap, planting, rail, promenade, edge, blocks), river, rip-rap, riparian grasses, shrubs and cottonwoods, handrail, promenade surface and joints, planters, gabions, benches, edge trees, lamps, blocks and patios, Peace Bridge (truss, deck, landing), far bank, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/rwalk/v003/review/independent-review.md. Do not run the build.
This is version 3. The v002 review found 0 P0 and 2 P1. The P1s: the right_side camera looked from the land side, so the blocks hid the whole street section (river, rip-rap, riparian strip, rail, promenade, bridge) and about 60% of the frame was empty ground and sky; and every block window showed an opaque black square where the vertical and horizontal frame bars crossed (glass_close, architecture_close, planters_benches, facade_close). The v001 P0 and all other v001 P1s were confirmed fixed in v002 and must stay fixed (bridge landing on an abutment at promenade level with an opening in the river rail; lattice-tube bridge; 6 m bands; packed dark rip-rap; continuous riparian cover; planters with rails; rear and end facades; no slot at the promenade base; rear, left_side and rear_side framed on the section). The builder claims both v002 P1s are fixed: right_side is now a raised three-quarter view from over the river, looking north-east up the section, so river, rip-rap, riparian strip, rail, promenade, planters, blocks and the Peace Bridge all read; the block windows' mullion now stops either side of the transom and sits 8 mm behind it, and both bars end in front of the pane, so no bars overlap or share a plane at the crossing. Also changed (P2): the river and planter handrails are a darker bronze, distinct from the timber benches. Verify each in the pixels; do not take the builder's word.
