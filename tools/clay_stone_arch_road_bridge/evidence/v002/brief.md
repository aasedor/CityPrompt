You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/stonebr/v002
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, arch_spandrel, cutwater_pier, balustrade, lamp_standard, roadway_deck, river_underside, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a heritage stone arch road bridge over a river (the top view governs the plan): three semicircular cut-stone arches on piers with pointed cutwaters, solid spandrel walls with a moulded cornice, stone balustrades with pedestals, ornate double-lantern lamp standards, a carriageway with lane markings and footways, splayed approach walls and quays at both ends, old town blocks as context. a bridge (a street or path option, not a building): judge span form, structure, deck, edges, supports, contact with banks and ground, and pedestrian-scale finish, not storeys; the surrounding city is simplified context; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (three-arch cut-stone road bridge with cutwaters, cornice, balustrades and double-lantern lamps over a river between quays),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/stonebr/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions, arch count and form, voussoirs and spandrels, piers and cutwaters, cornice, balustrades and pedestals, lamp standards, carriageway and footways, approaches and quays, river, context, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/stonebr/v002/review/independent-review.md. Do not run the build.
This is version 2. The v001 review found 1 P0, 10 P1 and 8 P2.

**P0:** the whole-envelope front view clipped the bridge. Only one pier and about one and a half arches were in frame, and the near abutment and approach were missing.

**P1s:**
- front_corner cut the near abutment and approach wall at its bottom edge.
- The plan was a mirror-symmetric cross with at-grade crossings. The source has the east quay road passing under a fourth land arch, a curved north-east quay and a narrower upstream river.
- The splayed approach walls were tiny stubs.
- The curved approach wall overhung the quay face, with a black saw-tooth underside and a loose wedge.
- Every pier had a see-through black slit where the arch jamb met the cutwater.
- The lamps were plain utility lamps.
- The scene visibly ended: the river stopped against a grey plane, a quay block end was exposed, and a grey band showed through the arches.
- The stone was cool grey, not the source's warm sandstone, and the water was teal, not dark olive. Stone, quay and paving were hard to tell apart.
- Two trees hid the near arch and abutment in rear_side.
- left_side and right_side showed the bridge at under 8% of the frame and were near-identical mirror images.

**P2s:**
- a double centreline;
- square balusters;
- a plain pier pilaster;
- the keystone notching the dentils;
- shadow smears on the deck;
- oversized upstream cutwaters;
- a bus hiding the deck in roadway_deck;
- repetitive context blocks.

**The builder's claimed fixes:**
- **Plan, east bank.** The plan is re-derived from the top view. The east river pier now stands at the edge of a low quay (about 3 m above the water). That quay's road passes under a fourth, 10 m land arch between the east river pier and the east abutment, and an 8 m retaining wall separates the low quay from the town.
- **Plan, upstream.** North of the bridge the low quay curves west, so the upstream channel is about 44 m wide against 59.5 m downstream.
- **Plan, west bank.** The west quay is high, and its quay road meets the bridge road at grade with zebra crossings.
- **Abutment corners.** All four corners have a quadrant wall: a balustrade on a plinth, the plinth and rail each one seamless swept solid, sweeping the footway round onto a coped quay or retaining-wall parapet. The end pedestal and a larger double lamp stand at the tangent point.
- **No overhang at the corners.** At the west, the quay face is set 4.5 m back from the abutment and the quay wall itself curves round each corner under the parapet. At the east, the retaining wall top does the same.
- **Cutwater slit.** The cutwaters run 5 cm proud of the pier jambs and start inside the pier body, so no face is shared.
- **Lamps.**
  - Each lamp has a moulded bell base, a round shaft with two rings and fluting, and a collar.
  - Two C-scroll arms with volutes carry hexagonal glazed lanterns with corner posts, domed caps and finials.
  - A central finial tops the shaft.
- **Scene edges.** River, quays and ground run 2.4 km each way, and the camera clip distance is raised so nothing ends in view. Simple and plain massing blocks with hipped roofs continue the town along both banks.
- **Palette.** Warm honey sandstone, with lighter voussoirs and cornice and darker joints; quay and retaining walls darker and greyer; cool grey paving; dark olive water.
- **Cameras.**
  - front stands on the north-west quay promenade behind the near abutment and looks along the north face. The river is at left, the quadrant and end lamp at right, and the arches recede left.
  - front_corner is high over the west bank, with the south face on the right and the near south-west quadrant in the lower part of the frame.
  - left_side is a lateral view of the west abutment and its curved quay corner from the river.
  - right_side looks north along the low east quay road through the land arch, showing the east pier and retaining wall.
  - rear, rear_side and rear_north are reframed, with no trees in their sight lines.
- **P2 fixes.**
  - a single centreline;
  - a recessed panel on each pier pilaster;
  - a lower keystone and dentils returned near it;
  - smaller upstream cutwaters;
  - roadway_deck moved a lane over;
  - varied block heights and colours.
- **P2s not addressed:** the balusters are still square stacks, and the footways are not widened.

Verify each in the pixels; do not take the builder's word.
