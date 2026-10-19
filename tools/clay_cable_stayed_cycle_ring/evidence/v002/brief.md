You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ring/v002
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, pylon_head, cable_fan, ring_deck, ramp_landing, column_support, intersection_under, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a cable-stayed circular cycle bridge (the top view governs the plan): a ring deck with a red cycle surface and white railings hung from one tall central steel pylon by a fan of radial cables, carried also by a few concrete columns, with straight ramps landing at the roads, over a busy road intersection with lane markings, low brick blocks and trees as context. a bridge (a street or path option, not a building): judge span form, structure, deck, edges, supports, contact with banks and ground, and pedestrian-scale finish, not storeys; the surrounding city is simplified context; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (circular red cycle ring hung by radial cables from a single tall central pylon over a road intersection, white railings, ramps),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ring/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions, ring radius and width, pylon, cable fan, deck surface and edges, railings, columns, ramps and landings, intersection beneath, context, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ring/v002/review/independent-review.md. Do not run the build.
This is version 2. The v001 review found 1 P0, 5 P1 and 5 P2. The P0: the ramp's ground landing was never shown; ramp_landing framed only the rising mid-ramp and every whole-envelope view lost the ramp while it was still raised. The P1s: the ring's outer edge kerb ran straight across the ramp mouth as a raised bar; both ring balustrades were open bar fences without the source's glazed infill panels (glass_close showed no glass); the front camera sat on the near deck at rail height, losing the near arc fascia, column and ramp the source front shows; the pylon tip left the top edge of every whole-envelope view (front_corner also cut the cable collar, pylon_head cut the mast top); the gable triangles of the context houses rendered pure black. The P2s: a drum-shaped cable collar with a mast tapering to a needle; straight prismatic columns with cap blocks; zebra crossings instead of Dutch block-dash cycle crossings; a deck too light and pink; rear and rear_north near-duplicates. The builder claims every one is fixed: ramp_landing now stands at the ramp foot looking up the ramp, and the foot lands on a red apron with white kerb lines and block dashes joining the cycle path by the north-south road; aerial and top are reframed to show the whole ramp from ring to foot; the outer kerb is an arc that stops either side of the ramp mouth so the deck runs flush onto the ramp; each ring balustrade bay now carries a pale glazed infill panel under the top rail with a low shoe rail (the ramp keeps open bars); front stands outside the ring by the ramp a little above the deck (near arc, a column, ramp descending right, pylon centred); front_corner, aerial, left_side, right_side, rear, rear_side and front are pulled back so the full pylon fits, and pylon_head is re-aimed on the mast top; the context houses carry brick gable triangles over the roof-plate ends; a downward-flaring conical cable spreader with a constant-diameter mast above; tapered concrete blade columns widening towards the deck; red cycle-crossing bands with block-dash edges replace the zebras; a darker red-brown deck; rear_north moved to a low north-north-east viewpoint. Verify each in the pixels; do not take the builder's word.
