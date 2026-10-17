You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/sblk/v001
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, balcony_bands, twisting_tower, tower_loop, courtyard, roof_terraces, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a sculptural white residential superblock on a street corner with streets south and west (the top view governs the plan): a perimeter block about 1.4 times as wide as deep round a rounded inner court; fluid white bands at every floor, reading as spandrels between white piers with punched windows on the straight street faces and thinning to sinuous projecting balcony bands over ribbon glazing round the rounded corners; the roof line rising to about nine storeys at the south-west corner and falling along the south wing to a low podium at the south-east corner, where a twisting tower of about fourteen storeys with spiralling white blades rises and ends in an open loop; a glazed retail ground floor recessed behind sculpted white piers; terraced planting in the court; roof terraces with skylights. The north face is not visible in any source; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (fluid white perimeter block with sinuous balcony bands and punched-window street faces, swooping roof line, twisting looped tower at the south-east corner, rounded court with terraced planting),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/sblk/v001/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey counts round the ring, plan and court, floor bands (corners vs straight faces), piers and punched windows, roof line and parapet band, tower (twist, blades, floor plates, loop), retail ground floor, court terraces, roof terraces and skylights, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/sblk/v001/review/independent-review.md. Do not run the build.
This is version 1, the first build of this family; there is no previous review. Record every P0 and P1 precisely, with the view that shows it, so the builder can fix each one in the next version.
