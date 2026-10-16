You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/terr/v002
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, terrace_planters, raking_frame, birch_court, solar_roof, dark_block, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a terraced stepped residential tower (the top view governs the plan): a fifteen-storey block of dark charcoal brick across the north with narrow punched windows in a staggered rhythm and a flat roof carrying rows of solar panels and two skylight boxes; against its south face an east wing stepping down toward the south in seven two-storey terraces, each step face floor-to-ceiling glazing between cedar panels with white slab edges and a slim balcony rail on its upper floor, each terrace a timber deck behind a black steel railing with corten planters of grasses and small trees and garden furniture; a raking concrete frame following the step corners along the wing east and west edges; west of the wing at the foot of the dark block a paved court with a grove of birches. The north face is not visible in any source; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (dark brick slab with solar roof, stepped wing of timber-decked terraces with corten planters and black railings, cedar-and-glass step faces with white slab edges, raking frame, birch court),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/terr/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, step count and depth, step faces (glazing, cedar, slab edges, balcony rails), terraces (decks, railings, planters, furniture), raking frame, dark block windows, solar roof, birch court, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/terr/v002/review/independent-review.md. Do not run the build.
This is version 2. The previous independent review (v001) found: P1 the east raking element a slim white strut past a stepped cedar facade where the sources show a solid dark charcoal triangular wall with a light coping along the rake and the terraces ending against it; P1 the wing's court-facing west wall punched cedar where the sources show a projecting balcony on every floor with white slab edges, black rails and full-height glazing between cedar panels; P1 no ground colonnade (the sources set the ground storey back behind white round columns on the west and south fronts); P1 the birch court a flush lawn square and two lawn pads where the sources show a raised corten planter with dense underplanting and two planted raised beds with a paved path between; P1 terrace planting and furniture far too sparse. The builder claims: a solid charcoal raking wall from grade to the step line on the wing's east side, under a light coping, the terraces ending against it; the west elevation in step strips of full-height glazing between cedar panels with a projecting balcony (white slab edge, black rail with glass) on every floor; a glazed ground storey set back 1.5 m behind white round columns on the south and west fronts; the birch grove in a raised corten planter with dense underplanting and two raised corten beds with a paved path between them; on every terrace a long corten planter of tall golden grasses with multi-stem small trees, a sofa, a lounger and a dining set. Verify each in the pixels and record for each v001 finding whether it is resolved.
