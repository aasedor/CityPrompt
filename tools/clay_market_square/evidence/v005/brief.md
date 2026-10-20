You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mktsq/v005
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, stage_pavilion, slat_wall, seating_tiers, cheek_walls, bollard_grid, paving_drain, light_mast, backstage_door, meadow_beds, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is an open space, not a building: a serviced civic market and event square (the top view governs the plan). A large plaza of pale square concrete slabs (1.5 m slabs, a stronger joint every 6 m) flares outward toward the south and is set out with a regular 3 m grid of short grey utility bollards in five rows (alternate rows offset) with small square floor drains; there are no stalls or chalets in the source. At its north head a curved seating bowl of three concentric tiers on 29 m arcs (about 38 m chord), each tier three low steps of stacked warm-grey stone risers under pale concrete treads, with a wide terrace walk between tiers, rising to an upper terrace. On it a raised stage platform with a gently curved dark front edge and an open-fronted pavilion: back and side walls clad in vertical timber slats of mixed widths, depths and three tones, a deep flat dark roof slab, a loudspeaker near each end of the back wall. Two slender dark floodlight masts with six stacked lamp heads stand just outside the pavilion. Stacked-stone cheek walls step up beside the bowl; raised meadow beds retained by stacked stone line both flared plaza edges, planted with broad shade trees; lawn, a meadow field and a tree belt beyond. The backstage door in the east return, the stage side steps and the far lawn and tree belt are teaching assumptions; the meadow grass is abstracted as clumps. The source is backlit at golden hour; judge form and material hierarchy, not lighting.; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (flared bollard-gridded plaza of square slabs facing a curved three-tier stone-and-concrete seating bowl and a timber-slatted stage pavilion under a flat dark roof, framed by stacked-stone meadow beds with shade trees and two floodlight masts),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mktsq/v005/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions (plaza flare, bowl arcs and chord, stage on axis), paving slabs and joints, bollard grid (rows, spacing, offset, size), floor drains, seating tiers (count, steps, stone risers, concrete treads, terraces), cheek walls, raised meadow beds and stone retaining walls with copings, upper terrace, stage platform and curved fascia, pavilion (slat cladding, returns, roof slab, loudspeakers, backstage door), floodlight masts and lamp heads, trees and meadow, lawn and context, materials hierarchy, grounding (nothing floating or below grade). Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mktsq/v005/review/independent-review.md. Do not run the build.
This is version 5. The v004 review found 0 P0 and 2 P1:
1. P1: the top tier still reversed its bend. Traced in the top view it was a shallow W: north on the axis, dipping south at about +-14 m, then turning north again at the ends. It read as a gull-wing ribbon in aerial and front_corner, with pale terrace wedges at its ends. In the source every tier line is concave to the plaza with its outer ends furthest south; only two bands run in front of the stage, and the third tier appears only as stepped wings rising beside the stage to the cheek walls.
2. P1: the band-to-walk proportion was the inverse of the source. The pale walks were about 3 to 4 times the depth of the warm bands, and the 0.45 m treads were stair-scale, so the bowl read as a pale ramp with thin stone stripes. In the source each stone seating band is about 2.5 to 4 times the depth of a walk.

The builder claims both are fixed:
1. The north curl is removed entirely. Every tier line is now a plain arc of one shared centre, 73.5 m south of the foot apex, so every line is concave to the plaza with its outer ends furthest south and none reverses. Only two full bands run across the bowl in front of the stage. The third band exists only as two wings of three seat steps rising beside the stage, from a 1 m pale walk at the upper-terrace level up to the high meadow beds, concentric with the bowl and with their inner ends buried in the stage cheek walls. The cheek walls now start just in front of the first wing riser and retain the wings.
2. Every step is now seat-scale: 0.40 m risers in coursed stone under 0.85 m light warm-stone treads. The first band is three such steps, about 2.55 m deep, followed by a narrow 1.0 m pale concrete walk. The second band is two treads and the sixth riser, which is the upper-terrace edge. The pale terrace before the stage is about 1.75 m deep on the axis. From above, the bowl now reads as broad warm-stone seating bands with narrow pale walks. The bowl foot moved 4 m north (apex at y = 1.0) so the stage, terrace and bands keep their proportions.

Verify each in the pixels (top, aerial, front_corner, front, seating_tiers, cheek_walls, left_side, right_side); do not take the builder's word. Trace the tier lines in the top view and confirm none reverses. Compare the band and walk depths, the wings beside the stage and the cheek walls against the locked top and oblique.

The v004 fix must still hold: the plaza flares continuously from the bowl foot to the south edge between the 22-degree splayed bed walls and then against lawn wedges, and the bollard rows lengthen southward.

The v003 fixes must still hold:
- the 27 m curved stage platform with its dark fascia, about 0.75 of the foot chord;
- the 21.6 m slatted pavilion, about 0.6 of the foot chord, with loudspeakers and the backstage door;
- legible individual steps, each tread nosing throwing a shadow line over its stone riser.

The v002 fixes must also hold:
- the lowest tier concave to the plaza;
- stubby drum bollards on the 3 m grid, five rows with alternate rows offset;
- stacked-stone cheek walls at both stage ends.

The v001 fixes must hold too: stacked ledgestone on every riser, with bed and staggered head joints reading as dark lines.

So must everything the source shows that earlier versions got right:
- square slabs with stronger 6 m joints;
- single square drain grates;
- the two floodlight masts with stacked lamp heads;
- the raised stone-walled meadow beds with shade trees;
- the meadow and lawn beyond.
