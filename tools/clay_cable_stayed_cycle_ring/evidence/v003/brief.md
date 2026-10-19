You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ring/v003
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ring/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions, ring radius and width, pylon, cable fan, deck surface and edges, railings, columns, ramps and landings, intersection beneath, context, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ring/v003/review/independent-review.md. Do not run the build.
This is version 3. The v002 review found 0 P0, 3 P1 and 6 P2, and confirmed the v001 P0 (ramp landing) and four of the five v001 P1s fixed in the pixels. The P1s: the cables stopped at the top of the inner deck kerb while their anchor blocks hung lower on the fascia with bare fascia between, so the cables did not land on their anchors and the blocks floated; every pitched context house still showed a solid black slot along the gable base or eave (the v001 black-gable finding, only partly fixed, surviving one targeted fix); the ramp deck carried the ring's red finish and dashed centre line where all three sources show a pale grey-beige concrete ramp with a solid white centre line, so the red ring against the grey ramp was lost. Among the P2s the cable collar was still a drum with a funnel narrowing downwards instead of the source's cone flaring downwards. The builder claims: each cable now ends inside its anchor block, which sits on the inner fascia centred on the cable end, so no bare fascia shows between cable and block; each context house is now one closed brick solid with its gable triangles built in, under one closed slate roof prism (thick eaves, closed soffit and verge, overhanging the gables) sunk 3 cm onto the body, with a ridge capping, replacing the open roof plates and the separate gable triangles; the ramp surface is pale grey-beige concrete with one solid white centre line running from the ring edge to the foot, while the ring keeps its red finish and dashed line; the cable spreader is a cone flaring downward to the cable ring. Verify each in the pixels, especially every house's gable base and eaves in front, rear_north, ramp_landing and rear; do not take the builder's word.
