You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/zinc/v005
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, corner_dome, cafe_awning, balcony_ironwork, mansard_dormers, roof_court, interior, rear_court)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a Haussmann corner block with streets south and west around an inner court: a stone ground floor whose corner cafe wears a red awning wrapping the chamfer, a stone first storey, three storeys of red brick with stone string courses, quoins and window surrounds, tall French windows with individual iron balconies on the first and third storeys and continuous iron balconies on the second and fourth, a bracketed cornice, a zinc mansard with arched dormers and a flat top, and on the chamfer a stone drum with oeil-de-boeuf windows carrying a ribbed zinc dome with an oculus dormer, an open lantern and a gilded finial. The north and east faces are not visible in any source; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (zinc dome on the chamfer with oculus and lantern, brick-and-stone Haussmann facades with iron balconies, zinc mansard with dormers, red cafe awning wrapping the corner),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/zinc/v005/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, chamfer and dome, drum windows and lantern, balcony rhythm (individual and continuous), brick-and-stone banding, mansard and dormers, cafe awning and ground floor, cornice, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/zinc/v005/review/independent-review.md. Do not run the build.

This is version 5. The v004 review found 0 P0 and 1 P1: on the chamfer, the full-width balcony on two console brackets sat at the first storey directly over the awning frieze, where both sources put a window-width balcony at storey 1 and the full-width bracketed balcony at storey 2 (the chamfer should read narrow, wide, narrow, wide going up). The builder claims it is fixed (stone console balcony at storey 2, window-width iron balconies at storeys 1 and 3, continuous iron balcony at storey 4) and also addressed two v004 P2s: a zinc gutter now caps the wall heads above the main cornice where a brick band showed, with corner blocks closing the corner tops seen from above. Verify each in the pixels; do not take the builder's word.
