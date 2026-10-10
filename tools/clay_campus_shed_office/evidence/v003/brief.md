You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/office/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, entrance_corner, dock_contact, terrace_roof, sawtooth_contact, clerestory_close, interior, stairs)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a corner-lot two-storey office in a converted sawtooth shed: four south-glazed monitors running east-west, a flat-roofed office box with a terrace along the south edge, galvanised portal columns with X-braces only in the corner and east-end bays and thin tie rods in the canopy bays, charcoal corrugated cladding, a corner entrance under a thin canopy on the west face only, two bays on the west face of the box, a cantilevered dock canopy over a raised loading dock with a ramp and two stairs on the south apron. The east gable end and the north wall are not visible in any source. This is version 3; the previous independent review (v002) found braces piercing the canopy, a door split by a column, a one-bay west face, a wrap-around canopy and X-braces in every bay, all of which the builder claims to have fixed; verify each in the pixels; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (sawtooth silhouette over a braced portal-frame office box, corner entrance canopy, dock canopy and dock, terrace rail and rooftop unit),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/office/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, bay rhythm (south and west), entrance and canopy, dock, ramp and stairs, portal frame and braces, monitors and clerestories, terrace and rooftop plant, gable ends, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/office/v003/review/independent-review.md. Do not run the build.
