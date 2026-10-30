You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/viad/v003
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/viad/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions, arch count and rhythm, piers and pilasters, imposts and arch rings, shopfront infill (glazing, frames, signs), parapet and coping, track deck (ballast, rails, sleepers), train, cobbled street and pavement, context terraces, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/viad/v003/review/independent-review.md. Do not run the build.
This is version 3. The v002 review found 0 P0, 2 P1 and 16 P2.

The v002 P1s were:
1. **The run ended in frame.** In front_corner and aerial the viaduct, tracks, parapets, pavements and street all stopped on one clean line against empty grey, about 80 m past the detailed run. In cobbled_street the street ended at a ground edge against the sky.
2. **The street trees were on the wrong side.** They had been moved to the arcade kerb as an even avenue of about 9–10 trees, which screened shopfront bays. The oblique and top sources put about four trees, irregularly spaced, on the far, terrace-side pavement, and keep the arcade pavement to planters, cafe tables and bollards.

Both are the second and last targeted fix for their findings: v001 already raised the continuing run (the closed box) and the tree placement (canopies cutting the terrace).

Among the v002 P2s:
- a visible ground-plane edge;
- an empty grey plane beyond the terraces;
- pale smooth ballast;
- no impost on the near-end blind arch;
- faceted arch rings;
- slot-like pilaster strips;
- a stray spandrel outline;
- barn-like terraces;
- a blank east-terrace rear wall;
- fascia ends behind the imposts;
- a thin train stripe in front;
- train track and livery;
- distant sett aliasing;
- door framing;
- the lawn strip on the garden side;
- right_side and rear_north composition;
- phone boards omitting aerial.

The builder claims the following changes.

**No scene end in any camera.**
- **Far run.** The arched run (10 shop arches plus 10 plainer ones, to about y = 123 m) now carries on plainly for another 520 m to a far cut at about y = 643 m. The far run has:
  - a solid brick body;
  - parapets with the same coping and deck string course;
  - both ballast beds and both pairs of rails;
  - on each face, every arch shown as a dark arch-headed recess plate with a brick ring, at the same 8.2 m pitch.
- **City belt.** The far cut is buried inside a belt of city blocks across the end of the run: one 240 m long, 20 m high block straddling the viaduct, the street and both terraces, with three staggered rows of 15–30 m blocks behind it. The street and both terraces also run on to the belt, so every view along the run reaches the horizon through continuing buildings.
- **Near end.**
  - A flagged forecourt sits in front of the near end wall.
  - South of it, a cobbled cross street (11 m, with a pavement) runs across the whole scene.
  - Four rows of gabled terrace blocks stand beyond it, so the views looking south (front, rear, rear_side, rear_north) close on buildings.
- **Sides.** Five rows of gabled terrace blocks stand behind each terrace, out to about ±100 m from the viaduct, broken every 50–70 m by cross alleys. They have varied heights, alternating brick tones and slate roofs. This replaces the empty grey plane beyond the terraces.
- **Ground and clip.** The context ground is 6 km square and the camera clip distance is 9 km, so no ground edge is in any frustum.

**Street trees.**
- The trees are back on the far, terrace-side pavement, which is widened from 2.3 to 4.1 m (far pavement edge x = 21.3).
- The trunks stand in soil pits 0.55 m from the kerb.
- Crowns are smaller (spread 1.3, height 8.4 m) and end about 1.7 m short of the terrace face.
- Positions follow the sources: four in the matched frame, opposite arches 1–2, 4, 8–9 and 10–11 (y = −24.6, −4.1, 32.8, 49.2 m), irregularly spaced. Three more continue the line further along (y = 83, 104, 141 m).
- The arcade pavement now has no trees, only the planters, cafe tables and bollards.

**Fixes that must still hold (v001 and v002):**
- staggered setts with gutter courses;
- trapezoidal ballast beds with sleepers and rails;
- stone impost course with the rings springing from it on both long faces;
- train mid-run with open track ahead of both cabs;
- front_corner and top on the street side, showing the shopfront arcade;
- phone-01 pairing the locked top with the render top;
- left_side clear of the terrace roof.

The remaining v002 P2s are not addressed in v003. The terrace windows and chimneys run about 60 m past the arched run; beyond that the terraces and context rows are plain massing.
