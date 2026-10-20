You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mktsq/v004
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mktsq/v004/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions (plaza flare, bowl arcs and chord, stage on axis), paving slabs and joints, bollard grid (rows, spacing, offset, size), floor drains, seating tiers (count, steps, stone risers, concrete treads, terraces), cheek walls, raised meadow beds and stone retaining walls with copings, upper terrace, stage platform and curved fascia, pavilion (slat cladding, returns, roof slab, loudspeakers, backstage door), floodlight masts and lamp heads, trees and meadow, lawn and context, materials hierarchy, grounding (nothing floating or below grade). Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mktsq/v004/review/independent-review.md. Do not run the build.
This is version 4. The v003 review found 0 P0 and 3 P1:
1. P1: the bowl no longer read as nested concentric arcs. The upper tiers bent the other way to the foot: their middles bulged south toward the plaza and their ends swept north, so the plan read as a pinched bow-tie with triangular wings. Two straight-fronted rectangular high beds flanked the stage. In the source all three tiers are parallel arcs concave to the plaza, and the outer ends of the upper tiers curl north beside the stage up to the stacked-stone cheek walls.
2. P1: the three-tier rhythm was lost. The terrace walks had been cut to about 1.0 m, narrower than the stepped bands, so the bowl read as one continuous flight of about 9 pale treads. The source shows three distinct warm-stone tier bands separated by broad pale terraces wider than each band.
3. P1: the plaza did not keep flaring south. The bed walls fanned it at the head, but south of the beds the plaza edges ran nearly parallel to the axis and bollard rows 3 to 5 were the same length. The source shows a continuously flaring trapezoid with lawn wedges outside both edges.

The builder claims each is fixed:
1. Every tier line is now an arc of the same centre, 73.5 m south of the foot apex on the axis, so all lines are concentric and concave to the plaza (36 m foot chord; about 54 m top tier). No line reverses its bend. Beyond 14 m off the axis, just outside the stage, the upper lines curl gently north; the curl grows with height up the bowl, from none at the foot to about 6 m at the top tier's end. The bowl-end walls run steeply north-outward from the foot ends to the top tier's ends. The high-bed front behind the top walk follows the same curve from the bowl end in to the stage cheek walls, and the cheek walls now run forward to meet that corner. So the top walk and tier ends wrap up beside the stage to the cheek walls, and no straight-fronted rectangular bed faces the bowl.
2. Each tier is a band of three steps (0.30 m risers, 0.45 m treads) in coursed warm-grey ledgestone, under light warm-stone treads with a 5 cm nosing shadow line. The bands are separated by broad PALE concrete terrace walks, about 2.75 m deep (2.3 m walk plus the last tread): roughly twice the depth of a band. The top walk in front of the stage is about 2.8 m. From above, the bowl reads as three narrow warm bands between broad pale walks. The front camera was raised to 6.2 m so the three bands and the walks between them read as distinct in the front view.
3. The low bed walls leave each foot end 22 degrees off the foot line and stop at a bed corner about 27 m off the axis. From there the plaza edge keeps flaring outward all the way to the south edge (half-width 18 m at the foot, about 25 m at y = -8, 29 m at -12, 34 m at -21, 38.6 m at the south edge), against open lawn wedges outside both edges. The bollard rows moved about 1.5 m south and lengthen row by row.

Verify each in the pixels (top, aerial, front_corner, front, seating_tiers, cheek_walls, bollard_grid, meadow_beds, left_side, right_side); do not take the builder's word. Compare the tier arcs and their ends, the walk-to-band proportion and the plaza flare against the locked top and oblique.

The v003 fixes must still hold:
- the 27 m curved stage platform with its dark fascia, about 0.75 of the foot chord;
- the 21.6 m slatted pavilion, about 0.6 of the foot chord, with loudspeakers and the backstage door;
- legible individual steps, each tread nosing throwing a shadow line over its stone riser;
- the bed walls fanning about 22 degrees at the bowl foot;
- single square drain grates.

The v002 fixes must also hold:
- the lowest tier concave to the plaza;
- stubby drum bollards on the 3 m grid, five rows with alternate rows offset;
- stacked-stone cheek walls at both stage ends.

The v001 fixes must hold too: stacked ledgestone on every riser, with bed and staggered head joints reading as dark lines.

So must everything the source shows that earlier versions got right:
- square slabs with stronger 6 m joints;
- the two floodlight masts with stacked lamp heads;
- the raised stone-walled meadow beds with shade trees;
- the meadow and lawn beyond.
