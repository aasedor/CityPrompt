You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/lab/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, v_pilotis, exoskeleton, roof_screen, cantilever, stacks, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a four-storey high-tech research laboratory on a corner with streets south and east (the top view governs the plan): three fully glazed laboratory floors in a curtain wall with thin white slab bands and blue, green and yellow ductwork visible behind the glass, cantilevering west over the street front on an angled soffit; a recessed glazed ground floor behind two white V-shaped pilotis on the south front, with concrete walls at its west end and round the service bays; on the east elevation a white-painted steel exoskeleton of columns, floor beams and alternating diagonals, infilled with grey vertical louvre panels and white panels, wrapping the south-east corner; on the roof a pale edge walkway, a perforated metal screen enclosing the plant, a raised penthouse with units, duct runs and clusters of three exhaust stacks. The north face is not visible in the front or oblique; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (glazed lab floors with coloured services behind glass, cantilever over V-pilotis, white steel exoskeleton with louvre infill on the east, perforated rooftop plant screen with exhaust stacks),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/lab/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, curtain wall and slab bands, coloured services, cantilever and soffit, V-pilotis and recessed ground floor, concrete base walls, exoskeleton (columns, beams, diagonals, louvre and white infill, corner wrap), roof (walkway, perforated screen, penthouse, ducts, stacks), materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/lab/v003/review/independent-review.md. Do not run the build.

This is version 3. The v002 independent review found: P1 the middle east bays with vertical slats in small inset panels with wide white margins (source horizontal blades filling each bay); P1 the roof screen perforated only on its outer faces, the far runs reading as a plain parapet from above; P1 the entrance portal inside the east V-piloti, a leg crossing the doorway; P1 a black block where the portal post meets its head and a black triangle at the foot of the west V. The builder claims: full-bay louvre openings with horizontal blades; perforations on both faces of every screen run; the door in the bay between the two V-pilotis, which were moved apart, with a proud portal head; piloti legs offset so their faces never coincide. Verify each in the pixels and record for each v002 finding whether it is resolved; also confirm the seven v001 findings resolved in v002 have not regressed.
