You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/lect/v003
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/lect/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, vault (span, rise, ribs, cushions, glazed flanks, ends), white mass and slot windows, fin screen, Y-columns and glazed base, louvred masses, steps and planting, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/lect/v003/review/independent-review.md. Do not run the build.

This is version 3. The v002 independent review found: P0 the four roof masses not reading as a pinwheel in the top view (small, only two rotated, tabs past the vault ends; source four large masses rotated the same way out to the roof corners); P1 the white mass a plain extruded box with a flat soffit, slots punched rectangles; P1 the end-arch rims straight kinked box segments with black triangular gaps, 2-3 times heavier than the source rib; P1 the fin screen returning as 8 widely spaced bars over about 20% of the south face (source dense rhythm over about half); P1 the vault soffit through the open ends a blank grey shell without the rib grid. The builder claims: four 9 x 6 m masses, each the last turned 90 degrees about the centre, at the roof corners, with the vault shortened to leave the corners clear; arch ribs swept along the vault normal as continuous members, the end rim about half as heavy; a second rib grid under the shell; 23 fins at the west-face rhythm over half the south face; canted facets leaning out from the upper south and east faces and a soffit sloping up toward the south-west corner. Verify each in the pixels and record for each v002 finding whether it is resolved; also confirm the v001 findings resolved in v002 have not regressed.
