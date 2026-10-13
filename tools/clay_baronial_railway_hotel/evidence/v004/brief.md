You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/railway/v004
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/railway/v004/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, entrance tower and porte-cochere, tower tourelles and parapet, corner tourelles, crow-stepped gables, roof slopes and dormers, window rhythm and surrounds, court, fence and lawn, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/railway/v004/review/independent-review.md. Do not run the build.

This is version 4. The v003 review found 1 P0 (a full-height black slot inside the porte-cochere at the junction of the porch reveal and the tower passage wall, also present in v002) and 4 P1 (in the two-tier gables the lower window heads merged into the step copes and the outer jambs sat flush with the risers; the tower-side flank of the gable next to the tower read as a straight rake with no risers over a near-black wedge; the tower's conical stair tourelle was too small and too low and invisible at eye level; black notches where the court string courses meet at the inner corners, also present in v002). The builder claims all five are fixed: the passage walls now sit behind the tower arch reveal; each crow gable is built as stacked step slabs with windows fitted to clear the copes and risers; the stair tourelle is corbelled out above the ridge at the tower's rear-east corner with a taller shaft and cone; the court side-face courses are offset so the corner overlaps share no face. To stay under the 4 MiB GLB limit the east face uses lighter window frames, the rustication joints are slightly wider spaced, the court brick coursing is sparser and the six side tourelles use fewer segments. The porte-cochere slot and the court-corner notches have each now had two targeted fixes; say plainly whether either survives. Verify each in the pixels; do not take the builder's word.
