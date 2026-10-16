You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hospital/v005
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, braced_frame, entrance_canopy, roof_canopy, roof_plant, brick_base, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a regional hospital of three volumes on a corner with streets south, west and east (the top view governs the plan): a seven-storey clinical block at the south-west with a two-storey red-brick base with large windows, five storeys clad in pale panels with perforated screens over strip glazing, a tall dark signage panel near its east end, a recessed plant storey behind a dark louvre band and a raised canopy frame over its western roof; a taller L-shaped ward block wrapping the north and east, glazed behind a standing steel exoskeleton of columns, ring beams and full-height X-braces, on a brick base at the east street; between them a full-height glass atrium with a diagonal mullion net opening south over a large glass entrance canopy hung on tension rods. The north and west faces of the ward block are not visible in the front or oblique. Signage text is not required in clay; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (braced steel exoskeleton over the glazed ward block, perforated pale screens over the brick base, glass atrium with the cable-hung entrance canopy, signage panel, louvre band and raised roof canopy),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hospital/v005/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey counts, plan (three volumes), clinical block (base, perforated screens, sign panel, louvre band, roof canopy), ward block (exoskeleton bays, braces, rings, brick base), atrium (diagrid, roof), entrance canopy (rods, posts), roof plant, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hospital/v005/review/independent-review.md. Do not run the build.
This is version 5. The previous independent review (v004) found: P1 the atrium's diagonal mullion net running to the pavement across the main entrance with the revolving doors behind the lattice, where the source has a straight vertical-mullion storefront with a revolving door below the canopy line. The builder claims: below the canopy line (5.9 m) the atrium front is a storefront with straight vertical mullions and a door-head transom, two revolving doors set in the facade line between storefront glass, and a steel transom at the canopy line; the diagonal net now starts above it. Verify it in the pixels and record whether the v004 finding is resolved.
