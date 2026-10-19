You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hfxwh/v001
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, arched_windows, copper_cornice, granite_piers, east_side, roof_chimneys, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a two-storey Italianate commercial warehouse on a street corner, the street south and a side street east, a brick neighbour attached west (the top view governs the plan): red brick bays framed by rusticated grey granite piers; a tall ground storey of dark-green framed shopfront glazing with transoms and a double entrance door in the middle bay of the south front; a granite belt entablature; round-arched upper windows in granite archivolts with keystones, a triplet, one large arch and a pair across the south front and pairs on the east side; a deep verdigris copper cornice with brackets; a brick parapet with a copper coping, raised blocks over the piers and a raised panel over the middle bay; arched ground windows in brick on the east side behind the corner shop; a flat membrane roof with brick chimneys on the rear parapet; sidewalks, trees and a lamp. The north and west faces are not visible in the front or oblique; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (red brick bays between rusticated granite piers, round-arched upper windows with granite archivolts, dark-green shopfront ground floor, deep verdigris copper bracketed cornice, parapet with raised blocks),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hfxwh/v001/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count and proportions, piers (rustication, caps), brick bays, shopfronts and entrance, belt entablature, arched windows (counts per bay, archivolts, keystones, sills), copper cornice and brackets, parapet, raised blocks and coping, east ground windows, roof and chimneys, sidewalks, trees and lamp, neighbour, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hfxwh/v001/review/independent-review.md. Do not run the build.
This is version 1, the first build of this family; there is no previous review. Record every P0 and P1 precisely, with the view that shows it, so the builder can fix each one in the next version.
