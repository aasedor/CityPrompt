You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plus15/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, plus15_bridge, lobby_entry, curtain_grid, roof_terrace, crown_penthouse, interior, rear_service)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a square downtown office tower of sixteen floors over a double-height lobby: every floor a pale spandrel band under a dark vision band divided by closely spaced mullions, pale corner columns the full height, a parapet band, the lobby glazing recessed behind a perimeter colonnade, an enclosed glazed Plus 15 bridge leaving the west end of the south face at the second level and crossing the street on two piers, and a green roof with vegetated beds around an L-shaped glazed and louvred mechanical penthouse with rooftop units. Streets on all sides; the builder records sixteen floors where the oblique reads sixteen to eighteen; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (pale spandrel bands and close mullions over dark glass, corner columns, recessed lobby on a colonnade, Plus 15 bridge, green roof with glazed penthouse),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plus15/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, floor count, spandrel and mullion rhythm, corner columns and parapet, lobby colonnade and entry, bridge, green roof and penthouse, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plus15/v003/review/independent-review.md. Do not run the build.

This is version 3, the last permitted version. The v002 review found 0 P0 and 5 P1: the mechanical penthouse about 0.8 storey high against two storeys in the oblique; penthouse faces as solid frames with one glass strip instead of close vertical fins; rooftop units on the penthouse roof instead of the lower deck in the north-west notch; lower-floor vision glass transparent over empty plates; the interior view crushed to black above and below the glazing. Verify each in the pixels of this version; do not take the builder's word. Record every remaining P0 and P1 precisely, since no further version will be built.
