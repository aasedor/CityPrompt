You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/canalwh/v002
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, loading_doors, arched_doors, gable_tops, east_side, roof_deck, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a four-storey red-brown brick canal warehouse on the corner of a canal quay (south) and a side street (east), a second canal beyond the street (the top view governs the plan): two gabled sections side by side under parallel roofs running back from the quay, the western narrower and lower; each quay gable with a stone coping, raised shoulder piers at its feet, a pinnacle at the peak and a projecting hoist beam; on each section axis a stack of three green glazed loading doors with green board shutters folded back flat on the wall, over a round-arched timber cart door with stone springers and keystone; small segmental-arched windows with dark frames and stone sills flanking them; iron wall anchors; the long east wall with rows of small segmental windows, tall arched ground windows and a door, and a white timber cornice under the eave; behind the gables the inner slopes give way to a flat deck with round vents; a dormer on the east slope; brick chimneys; a brick-paved quay with a low brick parapet to the canal, a tree and a lamp; an attached gabled canal house west. The north face is not visible in the front or oblique; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (twin coped street gables with shoulder piers, pinnacles and hoist beams; stacked green loading doors with folded shutters over arched cart doors; segmental windows and iron anchors; canal quay),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/canalwh/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count and proportions (two sections, widths and heights), brick and joints, gables (copings, piers, pinnacles, hoist beams), loading doors and shutters, cart doors (arches, springers, keystones), windows (arches, frames, sills), anchors, east wall windows and cornice, roofs (two gables, valley, deck, vents, dormer, chimneys), quay, parapet, canals, neighbour, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/canalwh/v002/review/independent-review.md. Do not run the build.

This is version 2. The v001 review found 0 P0 and 9 P1: quay gables composed differently from the source (flanking windows on all three upper floors, the eave above the top loading door, an extra blank gable); the west section too narrow; the quay and side street too deep; a black line and post at the canal joint with grey streaks on the east canal; dark cracks along the valley roof planes and a chimney cut by a roof plane; a north face without arches, sills, anchors or joints; glass artefacts on the loading doors; the arched_doors camera missing the cart doors; front_corner and aerial framed too wide. The builder claims every one is fixed (the eave lowered so the top loading doors straddle it in gable panels, no top-floor flanking windows, lower gables, a 9.5 m west and 10.5 m east section, a 3.5 m quay and 4 m street, butting canal and parapet solids, joints kept on the paving, the hip plate and deck lifted proud with the stack on the deck, the north face given the street grammar, solid door panels in front of the glass, the arched_doors camera on the east cart door, tighter oblique and aerial). Verify each in the pixels; do not take the builder's word.
