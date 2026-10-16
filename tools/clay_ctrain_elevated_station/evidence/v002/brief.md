You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ctrain/v002
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, platform_canopy, skywalk_bridge, street_underpass, tower_cap, train_platform, interior, east_skywalk)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a downtown elevated CTrain station: a three-storey red-brick headhouse whose south face meets an elevated light-rail guideway, square brick stair towers at its two south corners each with a tall glazed stair bay and a pale projecting cap above the roof, a continuous glazed band along the top storey; two side platforms either side of two tracks on a concrete deck carried on round piers and cap beams over the east-west street, each platform with a long glazed gable canopy on steel posts, glass guards on the outer edges, yellow tactile edges, a red station pylon near the south end and a stair down to the sidewalk; a glazed steel-truss Plus 15 skywalk leaving the west face across the west street, an east link to a long north-south skywalk on columns; a two-car red-and-white light-rail train at the west platform. The neighbouring towers that the skywalks reach in the sources are not part of the asset, so the skywalks end at glazed stair pavilions; the north face is not visible in any source; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (brick headhouse with glazed stair towers and pale caps, elevated twin side platforms with glazed gable canopies, guideway deck on piers over the street, Plus 15 skywalks with truss bracing, red pylons, light-rail train),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ctrain/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, headhouse and glazed band, stair towers and caps, deck and piers, platforms (guards, tactile edges, pylons, stairs), canopies, skywalks, train, streets, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/ctrain/v002/review/independent-review.md. Do not run the build.

This is version 2. The previous independent review (v001) found: P0 interior camera occluded by an unlit slab; P1 glazed stair bays narrow and flush on the south faces instead of wide projecting bays on the outer (west/east) faces; P1 skywalks joining well north of the stair towers; P1 guideway a blocked stub (blank wall in the headhouse, open deck end at the south); P1 street stairs floating ribbons with detached rails; P1 whole-envelope framing too small and the front not the source's street-level view toward the south-west tower. The builder claims: interior camera now in the upper concourse looking south through the glazed band; wide projecting glazed bays on the outer tower faces with a slot on the south faces; skywalks moved alongside the towers; tracks pass through the headhouse to a guarded north tail track with buffer stops and descend south on a ramp to grade; solid street stairs descending outward from the platform ends with posted handrails; tighter site and a street-level front from the south-west. Verify each in the pixels and record for each v001 finding whether it is resolved.
