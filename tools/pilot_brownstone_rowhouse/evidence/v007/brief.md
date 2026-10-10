You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/c8ebf69d-d6aa-5be2-bcf1-e104fd655028/scratchpad/dev-artifacts/CityPrompt/pilot-brownstone/v007
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (20 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, stoop_contact, areaway_door, roof_contact, rear_wing, side_openings, interior, stairs, roof_furniture, side_entrance)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The right elevation is a party wall in the source (the house is an end-of-row unit); a blank brick party wall is correct there.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture. Do fail it for wrong geometry,
  wrong bay rhythm, missing or extra storeys, missing identity elements (stoop, pediment, cornice, grilles, chimneys, lantern, rear wing),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/c8ebf69d-d6aa-5be2-bcf1-e104fd655028/scratchpad/dev-artifacts/CityPrompt/pilot-brownstone/v007/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, bay rhythm, stoop and entrance, garden level and grilles, cornice, roof and
   lantern/chimneys, flank openings, rear wing, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/c8ebf69d-d6aa-5be2-bcf1-e104fd655028/scratchpad/dev-artifacts/CityPrompt/pilot-brownstone/v007/review/independent-review.md. Do not run the build.
