You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mill/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, arched_windows, corner_entry, roof_pavilion, chimney_contact, shopfront, interior, rear_yard)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a converted four-storey red-brick mill on a corner with streets south and west: segmental-arched shopfronts with dark frames between brick piers on the ground floor, three upper storeys of segmental-arched windows in recessed panels between full-height pilasters, a stone sill band over the ground floor, a dentil cornice under the parapet, a slate roof pitching from a ridge along the long axis to raked gable parapets on the short faces, a glazed rooftop pavilion with a terrace rail on the front slope over the western bays, rooflights on the rear slope and a tall square brick chimney at the north-east corner. The north face is not visible in any source; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (arched shopfronts and arched windows between pilasters, dentil cornice, slate roof with raked gables, glazed rooftop pavilion, tall corner chimney),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mill/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, bay rhythm and pilasters, arched openings, cornice and band, roof and gables, pavilion and chimney, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mill/v003/review/independent-review.md. Do not run the build.

This is version 3, the last permitted version. The v002 review found 1 P0 (the west street face six bays per storey against four in both ground sources, so the plan was 1.44:1 instead of near-square) and 1 P1 (pavilion glazing over 86 to 90 percent of the ridge with no end terraces, against about 73 percent with a railed deck beyond the north end and open slate before the south gable). It also flagged, on pixels, flat-headed openings and a brick first floor; the orchestrator checked the locked sources and they show segmental-arched windows on every storey and arched shopfronts on this building, so arches stay. Verify each finding in the pixels of this version; do not take the builder's word. Record every remaining P0 and P1 precisely, since no further version will be built.
