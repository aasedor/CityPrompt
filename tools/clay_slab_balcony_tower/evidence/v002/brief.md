You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/slab/v002
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, balcony_close, fin_contact, lobby_entry, roof_penthouse, base_corner, interior, rear_lane)
- Phone boards: boards/*.png

This is version 2. The v001 review found 0 P0 and 4 P1: centre-bay spandrel and window ratio inverted, centre bay too wide, fin stubs above the parapet, black ground-floor soffit. Verify each in the pixels; do not take the builder's word.

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a square-plan mid-century concrete apartment tower of twelve storeys over a recessed glazed ground floor on columns: exposed concrete slab edges on every storey projecting as balcony plates with glass balustrades on the outer bays of each face, brick spandrels under a window band in the centre bay, full-height concrete fin walls at the bay lines and corners, a flat roof with a low parapet and a two-storey concrete mechanical penthouse with rooftop units. Streets lie south and west; the north and east faces are not visible in any source. The builder records twelve storeys where the oblique reads twelve to thirteen; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (stacked balcony plates with glass balustrades, exposed slab bands, concrete fins, brick spandrels, recessed glazed base, rooftop penthouse),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/slab/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, balcony stacks and slab bands, fins and corners, centre-bay spandrels and windows, recessed ground floor and lobby, penthouse and roof plant, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/slab/v002/review/independent-review.md. Do not run the build.
