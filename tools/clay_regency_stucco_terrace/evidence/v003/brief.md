You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/regency/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, porch_balcony, giant_order, end_pediment, mansard_dormers, east_side, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a palatial Regency (Nash-style) stucco terrace block round a small light court, streets on the south, east and west, a row of brick terrace houses against its north side (the top view governs the plan): cream stucco throughout; a channelled (rusticated) ground storey; a giant order of engaged Corinthian columns through the first and second floors between the window bays; a full entablature and modillion cornice; a balustraded parapet with pedestals over the columns; three porches of paired Tuscan columns carrying stone balconies on the long south front; a central pediment over the giant order on the east and west ends; tall first-floor windows with iron balconettes and cornice heads, shorter second-floor windows; a steep grey slate mansard above the balustrade with dormers and white party-wall fins carrying chimney stacks, a flat lead top; basement areas behind iron railings along the pavements; street trees and lamps. The north party side is not visible in the front or oblique; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (cream stucco palace front with a giant engaged Corinthian order, entablature and balustrade, paired-column porches carrying balconies, end pediments, iron balconettes, slate mansard with dormers and party-wall fins),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/regency/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, plan and light court, rustication, giant order (columns, capitals, rhythm), entablature and cornice, balustrade and pedestals, porches and balconies, end pediments, windows (sizes per floor, balconettes, heads), mansard (dormers, fins, stacks, flat top), areas and railings, streets and trees, terrace houses north, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/regency/v003/review/independent-review.md. Do not run the build.
This is version 3. The v002 review found 0 P0 and 2 P1 (v001: 1 P0, 7 P1): black voids where the coping meets the corner pedestals on every porch balcony and at the main parapet corners; the front render not matching the source front (too low and close, the mansard, dormers and fins hidden, a street tree over the corner order, the pediment end dominating instead of the long porch front). The builder claims both are fixed (every pedestal now rises past the rail top with its own cap, burying the rail crossings at the corners; the front camera stands further back in the south-west so the long west porch front recedes to the left under its mansard, dormers and fins with the south end to the right, and the street trees moved along the west front clear of the corner). Verify each in the pixels; do not take the builder's word.
