You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hpg/v005
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, gate_arch, gate_piers_fence, bandstand, bandstand_roof, carpet_beds, inner_lawn_beds, loop_benches, mature_trees, side_entrance, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is an open space, not a building: a fenced rectangular Victorian public garden block (about 43 x 57 m, long axis north-south) between city streets on all four sides (the top view governs the plan). A straight brick-paved axis runs from the main south gate to the north fence; an east-west cross path meets it at a round paved circle holding an octagonal white timber bandstand with a pink-copper ogee roof, balustrade, fretwork arches and a front stair, ringed by a flower bed. An oval loop path leaves the axis north of the bandstand, swells out to cross the cross path near the side fences and returns straight south to the gate, framing four leaf-shaped inner lawns each with a long carpet bed (white hydrangeas on the spine, lavender, purple and pink flowers either side) and four outer lawns under big mature shade trees. Granite edging lines every path. A black wrought-iron picket fence on a granite curb closes the block; the south front has a grand gate of two tall brick piers on granite bases with iron lanterns, an iron arch with the gilded sign HALIFAX PUBLIC GARDENS / FOUNDED 1867 under a crest (lettering is abstract blocks in clay), double iron gates thrown open, and two lower ball-capped side piers with gates where the loop legs enter. Benches line the loop, lamp posts stand at the circle and side entrances; brick mid-rises and a glass office block line the streets as plain context. North and side entrances, bed planting mixes and the street blocks are teaching assumptions; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (fenced Victorian public garden: grand brick-and-iron sign gate on the south axis, white octagonal bandstand with a pink-copper roof at the centre of a paved circle, oval loop and cross paths framing leaf-shaped carpet beds of hydrangeas and mauve flowers, mature shade trees in the corner lawns, black iron picket fence),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hpg/v005/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan and proportions (block ratio, axis, cross path, paved circle, oval loop legs and swell, four leaf lawns, four outer lawns), path paving colour and granite edging, gate (tall brick piers on granite bases, lanterns, iron sign arch with crest and two-line sign, open double gates, ball-capped side piers and side gates), fence (pickets, rails, posts, granite curb, continuity round the block), bandstand (octagon, posts, fretwork arches, balustrade, stair, ogee copper roof and finial, ring bed), carpet beds (shape, hydrangea spine, colour bands, soil edge), shade trees (count, placement, trunks at grade), benches and lamps, context streets and buildings, no coplanar paving or bed surfaces, all vertices at or above grade, framed locked views. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/hpg/v005/review/independent-review.md. Do not run the build.

## Context for this review (v005)

v005 is v004 (bed plants from the shared planting kit, which closed the bed-plant finding) with one targeted rework of
the two v004 P1s. Score it against the candidate v002 (0 P0 / 1 P1) and v004 (0 / 2). Nothing outside the planting
changed except the soil colour and two granite caps at the ring ends.

- **v004 P1 #1, the rim read as a tube (pink/lilac bolster, magenta outline from the air): removed.** No clipped rim
  band remains on any leaf bed, north border or the bandstand ring. Each bed now ends in its own raised dark-mulch
  margin (the soil role darkened to a near-black brown), with a flat low groundcover starting about 0.11-0.13 m inside
  it and the plants running out to that margin. Look at carpet_beds, inner_lawn_beds, bandstand, rear_north, top,
  aerial and front_corner: there should be no coloured outline round any bed.
- **v004 P1 #2, sparse fill and lost mauve bands: filled.** The thin lavender spikes (invisible in plan) are replaced
  by a mauve mophead hydrangea with broad light-purple heads, massed in drifts either side of the white hydrangea
  spine together with salvia and ageratum, at about 0.55 m centres; near the bed edges each plant shrinks to fit or
  falls back to a low ageratum cushion, so the beds read full to the margin. The bandstand ring bed is now one
  continuous mass of white and mauve hydrangeas and salvia along its centre line (about 0.66 m centres), with ageratum
  and salvia along both edges, over green groundcover (the pale pink centre band is gone). Builder's hue check on a
  1440 px top render, same crops as the v004 review (SW bed x 575-700, y 580-870; NW bed x 540-690, y 340-480):
  lavender-hue pixels 3.1% and 3.6% (v003 4.9%, v004 0.0%).
- **New P2 in v004, brown soil slab at the ring ends beside the bandstand stair:** both ring ends are now capped by a
  granite beam across the bed, and the groundcover runs to the caps.

Still as in v004 (P2s, not addressed): faceted shade-tree crowns, the free-standing faceted white shrubs, the boxy arch
scrolls, the foreground bench on the sidewalk, the world-edge band in rear, the forecourt plank joints. The kit's
known weakness (dark leaf shade visible between hydrangea leaves) is unchanged.
