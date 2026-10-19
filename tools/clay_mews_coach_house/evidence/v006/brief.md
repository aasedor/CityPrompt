You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mews/v006
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, coach_door, front_door, roof_chimneys, east_side, eaves_corner, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is the two-storey end house of a London mews row on a corner, the cobbled mews south and a side street east (the top view governs the plan), with its attached neighbour to the west: painted white brick over a black plinth, a thin white eaves band under a black gutter, a grey slate roof hipped at the corner end and a party gable to the west; on the south face a wide red vertical-boarded coach-house door with a glazed transom, a white panelled front door with a fanlight, six-over-six sashes on the upper floor; the neighbour repeats the door, fanlight and sashes; brick chimney stacks with clay pots on the party walls; two small skylights on the rear slope; setts, pavements, a plane tree and a black lamp standard. The north face is not visible in the front or oblique; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (white-painted brick mews house, red boarded coach door with transom, white panelled door with fanlight, six-over-six sashes, hipped slate roof with chimney stacks and pots, cobbled mews),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mews/v006/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count and proportions, painted brick and plinth, coach door (boards, transom), front door and fanlight, sashes, eaves band and gutter, roof (hip, slate, chimneys, pots, skylights), neighbour, setts, pavement and street furniture, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mews/v006/review/independent-review.md. Do not run the build.
This is version 6. The v005 review found 0 P0 and 3 P1 (v004: 3 P1, v003: 4, v002: 4, v001: 8 + 2 P0): every party wall carrying the same short square stack with three stubby square pots, where the sources show one long stack on the end-house/neighbour party wall with two clusters of tall round clay pots (5 and 4) and no stack on the neighbour's west party wall; the rear wing's downpipes dropping from the gutter overhang and standing clear of the wall, with an apparent orphan stub near one pipe foot; a free-standing beige wall panel and red door leaf on the east pavement with no jamb, head or enclosure, where the oblique source shows a continuous garden wall with the red door set into it. The builder claims each is fixed: one long two-step stack on the end-house/neighbour party wall running from just in front of the ridge down the rear slope, with a stone cap and oversailing course on each step, five tall round terracotta pots with rims on the ridge step and four on the rear step, and the west party wall left as a coped parapet with no stack; the wing downpipe taken from an outlet under the gutter by a swan-neck back to the wing's east wall, running 3 cm off the wall face with clips, ending in a shoe; a coped brick garden wall along the side street from the house's north-east corner to the line of the back wing and back west to the wing, enclosing the rear yard, with the boarded red door set between capped brick piers under a timber head. Builder also claims some v005 P2s: kneelers raised to sit at the eaves line, the east string course run to the south-east corner, six-over-six sashes on the rear face, the lamp arm turned over the carriageway.

The v004 fixes must still hold (the v004 review raised them): the upper south sashes are rectangular six-over-six sashes under a shallow flush gauged arch (rise about 0.1 of the span), not tall round-headed windows; the neighbour's back wing is a hollow hipped wing about 70% of the bay wide, centred on the bay, its ridge rising out of the main rear slope at mid-height with two valleys and a hipped north end; the back-wing windows are framed sashes with bars, sills and reveals. Verify every claim in the pixels; do not take the builder's word.
