You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/viad/v002
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, arch_shopfront, pier_pilasters, track_ballast, parapet_coping, train_cars, cobbled_street, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a Victorian brick rail viaduct (the top view governs the plan): a long straight run of semicircular brick arches on massive piers with pilasters and stone imposts, the arches infilled with glazed shopfronts and timber frames, a parapet with coping, two ballasted tracks on top with a red-and-white train, a cobbled street and pavement along one side, brick terrace houses with slate roofs as context. a bridge (a street or path option, not a building): judge span form, structure, deck, edges, supports, contact with banks and ground, and pedestrian-scale finish, not storeys; the surrounding city is simplified context; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (long brick arch viaduct with pilastered piers, glazed shopfronts in the arches, coped parapet, twin tracks and a train on top, cobbled street alongside),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/viad/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions, arch count and rhythm, piers and pilasters, imposts and arch rings, shopfront infill (glazing, frames, signs), parapet and coping, track deck (ballast, rails, sleepers), train, cobbled street and pavement, context terraces, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/viad/v002/review/independent-review.md. Do not run the build.
This is version 2. The v001 review found 0 P0, 8 P1 and 9 P2.

The v001 P1s were:
1. The cobbled street showed only transverse joint lines, so it read as a planked or corrugated deck.
2. There was no ballast; sleepers and rails sat on a flat light-grey slab.
3. The imposts were token cubes beside each jamb, and the arch ring did not spring from them, so the openings read as round-headed architraves.
4. The street-tree canopies cut into the terrace facades, with windows poking through the foliage.
5. The train sat flush against the far end parapet.
6. The viaduct was a short closed box of about 11 bays with blind end walls at both ends, so both tracks dead-ended.
7. The front_corner and top cameras sat on the lawn side and hid the shopfront arcade that the oblique and top sources show; phone-01 also paired the locked top with the render aerial.
8. In left_side a foreground terrace roof and wall hid the lower half of the garden elevation.

The v001 P2s were:
- faceted arch rings;
- off-centre or truncated pilaster strips;
- a stray spandrel panel outline;
- the north terrace facing the viaduct front-on, with no yards;
- barn-like terraces with unbroken ridges;
- a visible ground edge;
- right_side occlusion by roofs;
- fascia ends running into the jambs;
- only a thin stripe of train showing in front.

The builder claims the following changes.

**Setts.** The carriageway now has granite setts in staggered courses:
- transverse bed joints every 0.25 m;
- cross joints every 0.34 m, offset by half a sett on alternate courses;
- one merged joint mesh;
- three longitudinal gutter courses along each kerb.

Beyond about the far end of the detailed run, only every second course line is drawn.

**Ballast.** Each track sits on a trapezoidal ballast bed: 3.6 m at the base, 2.7 m at the crest and 0.36 m high, with sloped shoulders down to the deck. Between the shoulders and the parapets a narrow concrete cess remains. The sleepers are bedded with their tops 4 cm above the crest, and the rails sit on the sleepers. Small faceted stones in two tones lie over the crest, crib and shoulders along the nearer part of the run.

**Imposts.** A stone impost course sits at the springing (3.84 to 4.2 m), on both faces:
- it runs across every pier and the abutment face, standing proud of the pilasters;
- it returns about 0.55 m into each reveal;
- the arch ring springs from its top;
- the jambs below are plain brick.

The pilaster face strips now start just under the impost. The rings have 24 segments on the detailed street arches and 16 elsewhere.

**Trees.**
- The street trees moved from the narrow far pavement beside the terrace to the wide arcade pavement near the kerb, at x = 9.2 m. Their canopies are about 1.5 m clear of the arcade and well clear of the terrace.
- Their positions avoid the close-up cameras.
- New garden trees stand in the west gardens, clear of both the viaduct and the yard wall.

**Train.**
- The train is mid-run, from about -28 to +24 m, with open track ahead of both cabs.
- There is a cab windscreen at each end.
- It now sits on the rail tops instead of 16 cm into them.

**Continuing run.**
- The far end wall is gone. The run continues for 10 more, plainer arches (simpler shopfronts, unlit vaults) to a mid-pier cut about 80 m past the old far end, well beyond the rear cameras.
- The tracks, ballast, parapets, street, terraces and an exported context ground continue with it.
- Only the near end keeps its blind-arch end wall.
- The camera clip distance is raised to 900 m.

**Cameras.**
- front_corner and top are mirrored to the street side, high over the near end, so the near cut end, the shopfront arcade, the pavement, the street and the far terrace read as in the oblique and top sources.
- top stays a perspective view.
- phone-01 now pairs the locked top with the render top.
- left_side looks from over the gardens, high enough to clear the moved west terrace roofs.
- rear and rear_north are re-aimed now that the run continues.
- right_side is raised.

**P2s also changed.**
- The west terrace moved back to x = -36 to -27, with its rear yards facing the viaduct, low walls between the yards, a brick boundary wall and garden trees.
- The ground plane is extended.

**Not changed.** These P2s stand:
- the off-centre pilaster strips (beyond starting them under the impost);
- the spandrel panel outline;
- the terrace massing as long single barns with one ridge;
- the fascia width;
- the train stripe in front.

Verify each in the pixels; do not take the builder's word.
