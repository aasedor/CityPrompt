You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/bayg/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, bay_window, gable_bargeboard, porch_entrance, porch_frieze, west_side, west_gable, roof_chimney, foundation_fence, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a detached two-and-a-half-storey Toronto bay-and-gable house of red brick on a street corner, the street south and a side street west (the top view governs the plan): a raised ground floor over a rough grey stone foundation with basement windows; on the south front a steep cross gable with an ornate pierced bargeboard (roundels and drops), a curved fretwork arch, a spike finial and pendant over a triple attic window, above a two-storey canted bay with tall one-over-one sashes, amber stained-glass transoms, continuous buff stone sill and lintel bands and a small slate skirt roof between the floors; east of the bay a hipped entrance porch on turned posts with a spindle frieze, corner brackets and an iron balustrade, a dark green door with a stained transom, a stone stair with iron handrails down to a brick walk; a steep grey slate main roof, the front section gabled to west and east with a brick chimney at the east gable and the rear section hipped; a long west side elevation of tall sashes with stone sills and lintels and a paired attic window in the west gable; a low iron fence round the front lawn, shrubs, sidewalks and street trees. The north and east faces are not visible in the front or oblique; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (red-brick bay-and-gable house: two-storey canted bay with stained-glass transoms under a steep front gable with ornate bargeboard and finial, side entrance porch on turned posts, steep slate roof with east chimney, stone foundation),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/bayg/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count and proportions, brick and joints, stone foundation and basement windows, canted bay (three faces, sashes, transoms, stone bands, skirt roof), front gable (bargeboard, roundels, arch, finial, pendant, attic windows), porch (posts, frieze, brackets, balustrade, hipped roof), door and transom, stair and walk, roof (cross gable, west and east gables, rear hip, chimney), west side windows and gable window, fence, lawn, sidewalks and trees, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/bayg/v003/review/independent-review.md. Do not run the build.

This is version 3. The v002 review found 0 P0 and 2 P1, and confirmed all six v001 P1s fixed:
1. The front gable sat flush with the main south eave, while the upper bay projected about 0.7 m past the gable face under a separate flat slate ledge. In the sources the gable projects forward over the bay on a base cornice with corner brackets.
2. Every diagonal porch brace showed a black patch where it met the frieze rail and a black sliver where it entered the post, because the braces cut through the rail and the posts.

The builder claims both are fixed:
1. The front gable wall now stands on the plane of the bay's front face, 0.75 m in front of the main wall. The cross-gable roof, its ridge, the bargeboards, the fretwork arch, the finial and the pendant all come forward with it, and the cross-gable roof runs back into the main front slope along its valleys. The flat slate ledge over the bay is gone. The gable sits on one moulded base cornice (corona over a bed mould) running across its whole base, from the bay face back into the main wall. The cornice is carried on two knee brackets at its ends and two consoles at the bay's front corners. Fascias now run along the longer cross-gable side eaves.
2. Each porch brace is a cut piece narrower than the rail and the post. Its upper end finishes horizontally inside the frieze rail's underside and its lower end vertically inside the post, so no end cap or shared face is left in the open.

The builder also claims these P2 changes:
- The three attic windows are the same height under one shared stone head, and the pendant stops above that head.
- The gable shingle is a darker grey-brown with closer, darker courses.
- The porch beam is about 40% shallower, with the spindle frieze raised to meet it and the post caps carried up into it.
- The bay's own cornice, with its mitre slivers, is replaced by the straight gable-base cornice.
- front_corner and aerial no longer fit the whole street context. They frame the house from the source oblique's direction, so it fills most of the frame.

These earlier fixes must still hold:
- The fretwork arch is inside the gable and the bargeboards lie on the rakes, with no boards poking through.
- Every roof runs to one eave line, the rear wing's hip ridge dies into the main north slope, and there are no black voids at the hip corners or valleys.
- The plan is an L following the source top.
- The west gable has paired tall attic sashes.
- One mitred stone band per level wraps the bay.
- The door has raised panels, the stained transoms are only where the source shows them, and every upper lintel clears the eaves.

Verify each claim in the pixels; do not take the builder's word. Pay particular attention to these:
- front_corner, aerial, roof_chimney and top: the gable projecting over the bay on its cornice, and no flat ledge in front of it.
- gable_bargeboard and bay_window: the cornice, brackets and consoles, and the shared attic head.
- porch_entrance and porch_frieze: zoom on every brace end at the rail and at the post for any black patch or sliver.
