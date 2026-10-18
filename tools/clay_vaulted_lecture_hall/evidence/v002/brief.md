You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/lect/v002
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, y_columns, fin_screen, vault_ribs, roof_masses, entrance_steps, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a campus lecture hall on a street corner with streets south and west (the top view governs the plan): a near-square block; a full-height glazed ground floor recessed behind white branching Y-columns; above it a three-storey sculpted white composite-panel mass with horizontal slot windows; a screen of tall vertical aluminium fins wrapping the west face and turning the south-west corner; over the roof a barrel vault spanning east-west ringed by white arch ribs, its crown a field of white pillowed membrane cushions on a rib grid and its lower flanks clear glazing; under the vault four angular white masses with dark louvred sloping faces in a pinwheel on the roof terrace; wide steps and planting along the south front. The north face is not visible in any source; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (barrel vault with pillowed membrane crown, glazed flanks and white arch ribs, white sculpted mass with slot windows, vertical fin screen, Y-column glazed base, pinwheel louvred masses),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/lect/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, vault (span, rise, ribs, cushions, glazed flanks, ends), white mass and slot windows, fin screen, Y-columns and glazed base, louvred masses, steps and planting, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/lect/v002/review/independent-review.md. Do not run the build.

This is version 2. The previous independent review (v001) found: P0 the interior view black; P0 the four louvred roof masses small orthogonal boxes in mirrored pairs outside the vault ends instead of a rotated pinwheel of large angular masses under the arch; P1 louvred faces reading as staircases; P1 the vault a full semicircle with closed flat glass ends (source flatter, springing from the outer parapet edges, open ends); P1 crown cushions flat pads in a narrow band; P1 the white mass a plain box without faceted planes, sloping soffit and deep carved slots; P1 the glazed ground floor too squat; P1 black holes at the Y-column nodes; P1 the fin-screen return stopping in mid-air at the south-west corner; P1 a gap at the east end-rib foot and end glazing floating above the deck. The builder claims: interior camera moved out of the lobby core with more light; four rotated angular masses astride the open vault ends with flush framed louvre panels and light blade lines; a flatter semi-elliptic vault springing from beams on the parapet edges with open ends; pillowed cushions on the rib grid over most of the crown; deep carved slot reveals (the faceting and sloping soffit are not attempted); a double-height glazed ground floor; Y-column node collars; fins standing on the podium with rails meeting at the corner; rib feet on the springing beams. Verify each in the pixels and record for each v001 finding whether it is resolved.
