You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/railway/v002
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, entrance_tower, porte_cochere, corner_tourelle, crow_gables, roof_court, interior, rear_court)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a six-storey pink-grey granite Scottish Baronial railway hotel: a quadrangle around an open court with streets south and west, a square entrance tower a quarter of the way along the south face with a pointed-arch porte-cochere through to the court, a crenellated parapet and round tourelles with conical caps at its front corners, round corner tourelles corbelled out above the first storey with conical slate roofs, crow-stepped wall gables rising through the eaves, steep slate roofs with dormers and chimney stacks, sash windows with stone surrounds in rusticated granite, and an iron fence on a low wall with lawn strips and trees. The north and east faces are not visible in any source; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (crenellated entrance tower with the porte-cochere and tourelles, conical corner tourelles, crow-stepped gables, steep slate roofs, rusticated granite with sash windows, iron fence and lawn),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/railway/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, entrance tower and porte-cochere, tower tourelles and parapet, corner tourelles, crow-stepped gables, roof slopes and dormers, window rhythm and surrounds, court, fence and lawn, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/railway/v002/review/independent-review.md. Do not run the build.

This is version 2. The v001 review found 7 P0 (seven levels against six; the porte-cochere a blind niche; a black gap at the tower junction; an open slot at an inner court corner; tourelle windows as proud black slabs; crow-step copes floating off the steps; a black interior view) and 10 P1: gables dormer-sized against wall gables of three to four bays; no intermediate tourelles; a dense window grid with no taller ground floor; pale walls without rustication relief and light slate; roofs too low; black dormer cheeks; a stray black cube on the parapet; cameras from the wrong corner; a lawn court against the source's paved court with four trees; rear_court underexposed and blocked by a tree. The builder claims every one is fixed (five storeys with a tall ground floor; a through passage between two court carriers; the tower centred on the south face as in the locked top; cut-in tourelle windows; copes on the treads; single merlons; a lit street-facing interior; two-bay crow-stepped gables with two windows beside the tower and the tourelles; intermediate tourelles on the west, east and north faces; 4.8 m bays; granite tone with recessed joints; 55-degree slate roofs with a corbel table; a paved court with corner trees and court lights; a front camera from the south with the tower at the left). Verify each in the pixels; do not take the builder's word.
