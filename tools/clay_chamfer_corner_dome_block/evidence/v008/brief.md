You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/chamfer/v008
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, chamfer_dome, balcony_ironwork, ground_arcade, cornice_contact, roof_terrace, interior, rear_court)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a five-storey Eixample corner block with streets south and west: a rusticated stone ground floor with tall arched shop openings and the residential entrance on the chamfer, a stone piano nobile with a continuous iron balcony, three storeys of warm brick with stone surrounds and individual iron balconies on tall French windows, a heavy stone cornice and a balustraded parapet; on the 45-degree chamfer a bowed stone bay with glazing between columns over three storeys crowned by a round drum, a copper dome and a lantern; a flat terracotta-tiled roof with a pyramid rooflight, small rooflights and chimney stacks. The north and east faces are not visible in any source and are authored plain; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (chamfered corner with the bowed bay and copper dome, iron balconies on tall French windows, rusticated arched shop floor, cornice and balustrade),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/chamfer/v008/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, chamfer bay and dome, window rhythm and balconies, ground-floor arches and entrance, cornice and parapet, roof elements, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/chamfer/v008/review/independent-review.md. Do not run the build.

This is version 8, reopened after the user lifted the GLB size limit (now 4 MiB); the rule-2 counter was reset and up to two further versions are allowed. The v007 independent review found 0 P0 and 5 P1: the dome foot was a ring of opaque dark panels over a plain stone band where the sources show a strongly projecting cornice disc with pierced copper cresting on its lip; the dormers were cream toothed rings with flat hood plates where the sources show smooth copper round dormers with curved bonnet hoods merging into the dome; the dome ribs were segmented and stood off the shell where the sources show about eight continuous seated ribs; the chamfer bay was three flat facets with brick strips beside it where the sources show a continuously bowed stone bay with five lights per level and one curved railing; the front render was a wing elevation rather than an eye-level view centred on the chamfer. v008 rebuilds all five: a round dome-foot cornice disc projecting about 1 m on a bed mould with open copper arch cresting on its lip, smooth copper dormers with swept bonnet hoods, eight continuous ribs half-embedded in a smoother 32-segment shell, a seven-facet bow with five tall lights per level between round stone columns and one curved railing on a curved sill per level with stone beside the bay, and a front camera at eye height on the chamfer normal. Verify each in the pixels of this version; do not take the builder's word. Report every remaining P0 and P1 precisely, and say for each v007 finding whether it is resolved in the pixels.
