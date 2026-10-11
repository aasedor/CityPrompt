You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/chamfer/v006
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/chamfer/v006/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, chamfer bay and dome, window rhythm and balconies, ground-floor arches and entrance, cornice and parapet, roof elements, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/chamfer/v006/review/independent-review.md. Do not run the build.

This is version 6. The user lifted the three-version cap and asked for every building to be carried to a review with zero P0 and zero P1. The v005 independent review found 1 P0, 3 P1 and 8 P2: P0 the lantern floated above the dome apex with background showing under its base disc; P1 the chamfer entrance was a flat-headed glass panel where the sources show a round-arched glazed door with a transom, a frieze band over the arch and projecting piers, with a corbelled underside to the bow; P1 the dome was a squat hemisphere on a tall plain stone cylinder where the sources show a taller ribbed dome whose copper skirt and cresting sit directly on the bay cornice with no stone drum (that reviewer read the v004 'blind drum with pilaster strips' note as a misreading of the top-storey frieze); P1 the cornice was a flat fascia where the sources show a heavily projecting bracketed cornice with a shadowed soffit. P2s: bow balconies segmented per facet, mauve dome colour, flat pyramid rooflight, flat bow soffit, pale brick, no rear light-well, front camera on a wing elevation, no balustrade dies. Verify each in the pixels of this version; count the source storey rows yourself and state your reading; do not take the builder's word. Report every remaining P0 and P1 precisely, and say for each v005 finding whether it is resolved in the pixels.
