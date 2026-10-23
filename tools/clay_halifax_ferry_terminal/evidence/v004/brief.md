You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ferry/v004
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, entrance_canopy, facade_close, glass_close, architecture_close, roof_boxes, roof_mechanical, interior, brick_neighbour, lawn_bench, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a contemporary two-storey glass and concrete ferry terminal on a downtown Halifax corner (the top view governs the plan: about 20 m on the south street and 41 m along a wide west street), with a three-storey brick heritage block adjoining on the east: on the south front a cantilevered glass box over the entrance, three tiers of clear glazing in a slim dark aluminium grid between grey concrete end frames, a frosted top band and a projecting cap, over a deep entrance canopy whose fascia is lettered HALIFAX FERRY TERMINAL, with glazed storefronts and two pairs of glass doors below; the west third of the south front is a lower glazed bay whose canopy wraps the south-west corner and runs along the west front; the long west front has a glazed ground floor under that canopy, glazed upper bays between three full-height concrete fins, and on top of each fin a white box that cantilevers over the lawn strip; the north end and the exposed east wall are concrete with punched windows, a service door and a loading door; a flat roof of pale membrane panels inside a gravel border and a coped parapet, with a louvred mechanical enclosure around an air-handling unit, three skylights, hatches and vents; next door a red-brick block with cast-iron shopfronts, segment-headed second-floor and round-headed third-floor windows with stone hoods and keystones, brick pilasters, stone string courses, a corbelled frieze, a bracketed stone cornice under a brick parapet with corner finials, a pedimented gable with an oculus, and steep hipped clay-tile roofs with chimneys; a hipped brick wing, a narrow flat-roofed range and a parking court behind it; concrete sidewalks, a lawn strip with a bench along the west front, street trees in pits, a tactile strip at the entrance, crossings at the corner, low commercial blocks across the west and north streets, and the harbour with piers and a ferry beyond the blocks to the north. The north end, the east wall and the parking court are not visible in the front or oblique. The front view draws the west bay of the south front wider and the west front less foreshortened than the top and oblique allow; the top view governs the plan and the front camera is fitted to the glass box and the brick block; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (two-storey glass and concrete ferry terminal with a cantilevered glass box over a lettered entrance canopy and a long west front of glazed bays between concrete fins carrying cantilevered white roof boxes, beside a three-storey red-brick heritage block with a pedimented gable and a hipped tile roof),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ferry/v004/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette and storey count, plan (top view: proportions, the glass box, the fins and roof boxes, the brick block and its roofs), glass box (end frames, three glazing tiers, mullion grid, frosted band, cap, cantilever), entrance canopy and its lettering, storefronts and doors, wrapping canopy on the west bay and west front, west front bays and fins, roof boxes, parapet bands and copings, roof (membrane panels, gravel border, mechanical enclosure and AHU, skylights, hatches, vents), north and east walls, brick block (shopfronts, window types per floor, hoods and keystones, pilasters, courses, frieze, cornice, parapet and finials, pediment and oculus, hipped tile roofs, chimneys), streetscape (sidewalks, lawn strip and bench, tree pits and trees, tactile strip, curbs, crossings, lane markings), context blocks and the harbour, glass reading as glass with interior depth, no black slots, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ferry/v004/review/independent-review.md. Do not run the build.

## Context for this review (v004)

v004 is v003 with one targeted fix for the v003 review's only P1 (N4): the upper-lounge seating rows had no
legs and floated about 0.4 m above the lounge floor. Every lounge seating row (x = -6.5 and -4.0) and each of the
three south lounge benches now stands on a dark hardware pedestal that runs from 2 cm into the lounge floor to
2 cm into the seat. Nothing else changed. Check glass_close, front_corner and roof_boxes for lit floor between the
seats and their shadows, and confirm the v003 bench-joint fix and every v001 fix still hold. Score against the
candidate v002 (0 / 1) and v003 (0 / 1).
