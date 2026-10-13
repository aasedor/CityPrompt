You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/cityhall/v004
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, clock_tower, porch_stair, pavilion_mansard, cornice_contact, roof_court, interior, rear_court)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a three-storey grey limestone Second Empire civic hall around an inner court with streets south and west: a rusticated ground floor of round-arched windows, a piano nobile of pedimented windows with stone balconies and iron rails on the projecting corner and central pavilions, a second storey of hooded windows under a bracketed cornice, a steep slate mansard with arched dormers and a zinc flat with cresting, taller square mansards on the corner pavilions, a four-column porch at the piano nobile over a rusticated arcade reached by a broad stone stair, and the square clock tower rising from the central pavilion with a tall arched opening per face, a clock stage with four faces, a convex-concave zinc cap and a lantern; iron fence and lawn forecourt. The north and east faces are not visible in any source; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (central clock tower over the columned porch and grand stair, corner pavilions with tall mansards, slate mansard with dormers, rusticated base, piano-nobile balconies, iron fence and forecourt),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/cityhall/v004/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, tower stages and clock faces, porch and stair, pavilions and mansards, dormer rhythm, window rhythm and hoods, cornice and rustication, fence and forecourt, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/cityhall/v004/review/independent-review.md. Do not run the build.

This is version 4. The v003 review found 0 P0 and 4 P1: the storey hierarchy (the source has a low rusticated basement of short windows, a round-arched main floor and a rectangular hooded upper floor); the tower lower stage a plain stone shaft where the source has a slate mansard stage with a segmental-pedimented aedicule, scrolls and urns; black square voids at the court coping corners; forecourt lawn trees the source lacks. The builder adopted the source's storey hierarchy and claims all four are fixed (basement, arched main floor and hooded upper floor; the stair rises to a podium terrace before the main-floor arcade with the loggia above; the tower now has a slate mansard stage with aedicules, scroll consoles and urns under the clock stage; coping corner blocks; hedges and shrubs). Verify each in the pixels; do not take the builder's word. Every earlier finding was verified resolved in v002 or v003.
