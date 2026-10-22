You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/steps/v005
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/steps/v005/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions, central stair (steps, landings, handrails), terraces (risers, seats, paving), east parapet and pots, side stair, west parapet, flanking houses (doors, windows, heights stepping), bougainvillea, chapel and dome, belfry and cupola, lower plaza, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/steps/v005/review/independent-review.md. Do not run the build.

## Context for this review (v005)

v005 is v004 with one targeted rework of the four v004 P1s (`tools/clay_stepped_terraced_plaza/evidence/v004/independent-review.md`).
Score it against the candidate v003 (P0 = 0, P1 = 3) and against v004 (P0 = 0, P1 = 4). Nothing else changed.

| v004 P1 | v005 change | where to look |
|---|---|---|
| 1 East bougainvillea as four separate collars | Per terrace, the drape now hangs mainly on the OUTER (side-stair) face, its hem about 0.6 m above the side-stair treads with irregular tongues, up over the coping and 0.6 m down the inner face. At every parapet step a small drape climbs the step-end face from the lower coping onto the higher one, so no bare pier face shows between terraces. | side_stair, front, front_corner, parapet_pots |
| 2 Climber carrier visible as flat dark-green panels | The shared kit's `wall_drape` gained two opt-in arguments (defaults unchanged): `carrier_inset` stops the hidden carrier 8-12 cm inside the spray envelope, and `rim_sprays` adds a row of sprays along every envelope edge, kept 0.25 m clear of openings. Both plants use them. | architecture_close (foot of the corner column, right end of the roof canopy), side_stair (copings, pier sides) |
| 3 Black wedge at the south-west (corner) house door | The corner house's door moved from its east face, where the diagonal stair crossed it, to its south face onto the lower plaza; the sill sits 1 cm above the paving and the leaf runs 2 cm into it, so no gap shows. The east face now has two windows. | front_corner, aerial, top |
| 4 Black holes at the crossing of the chapel and belfry crosses | Each cross is now one closed plus-shaped solid (caps of five quads sharing the inner corners), so no faces coincide at the crossing; the belfry cross's foot now sits 14 cm into the cupola (it stood 26 cm above it before). | chapel_top, rear, front_corner, right_side |

Unchanged: the v004 fixes (west bougainvillea canopy over the roof edge, west foot splay and outside stair, pergola on the east house) and all v003 P2s. The west splay still covers two terraces (v004 P2 #5). Judge every item from the pixels.
