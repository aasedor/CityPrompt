You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mktsq/v001
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

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mktsq/v001/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions (plaza flare, bowl arcs and chord, stage on axis), paving slabs and joints, bollard grid (rows, spacing, offset, size), floor drains, seating tiers (count, steps, stone risers, concrete treads, terraces), cheek walls, raised meadow beds and stone retaining walls with copings, upper terrace, stage platform and curved fascia, pavilion (slat cladding, returns, roof slab, loudspeakers, backstage door), floodlight masts and lamp heads, trees and meadow, lawn and context, materials hierarchy, grounding (nothing floating or below grade). Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/mktsq/v001/review/independent-review.md. Do not run the build.
