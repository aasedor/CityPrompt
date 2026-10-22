You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plateau/v002
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, facade_close, architecture_close, glass_close, iron_stair, balcony_gallery, mansard_caps, corner_building, sidewalk_trees, roof_parapets, rear_yards)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a street option, not a building: the corner of two narrow one-way residential streets in Montreal's Plateau Mont-Royal, the top view governing the plan (the block corner at the bottom of the frame, one street running up-left and the other up-right). Both streets are lined by continuous rows of three-storey plexes with flat membrane roofs behind cornices and side parapets. The corner building is a large brick plex with a grey limestone corner pavilion on the east street and limestone quoins on the north street, three floors of windows with stone sills and lintels, stone belt courses, a mitred bracketed cornice round the corner, and teal sheet-metal mansard caps with gabled dormers over the corner and both street ends; a gallery balcony and black iron exterior stair at its north end. Along the north street (the row in the front view) the corner building is followed by a grey limestone plex with an octagonal turret on a corbel under a slate spire, then limestone and red-brick plexes and a second turret plex. Along the east street a row of red-brick and limestone plexes with teal mansard caps over stone bays at the party lines. Each plex has a raised ground floor with stone steps to a pair of panelled doors, wide windows with coloured frames (blue, green, red, white, teal), a second-floor door pair onto a timber gallery balcony with a painted fascia and an iron railing, reached by a black iron exterior stair that runs down the front yard alongside the facade and curls a quarter turn toward the sidewalk, and a third-floor door pair onto a smaller balcony; bracketed cornices with scroll consoles. Small front yards behind low iron fences on a stone curb, a few shrubs; pale concrete sidewalks with scored joints and young street trees in square soil pits; curb returns at the intersection; dark asphalt roadways with cars parked along the far curbs. The rows across both streets and the corner opposite are plainer context, and the block interior is a lawn with trees. The pedestrians, cafe tables, bicycles and the dog in the sources are not modelled; the clay trees are simplified masses. Judge it as a street scene: the street section and corner, the continuous plex walls, the stairs, balconies and doors, cornices, caps and turret, surfaces, planting and pedestrian-scale finish; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (Plateau residential rue: continuous rows of limestone and brick plexes with curling black iron exterior stairs, iron gallery balconies, coloured doors, cornices and teal mansard caps, over small fenced front yards and tree-lined sidewalks on narrow one-way streets meeting at a corner),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plateau/v002/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: plan (two streets meeting at a corner, building lines, yards, sidewalks, roadways, curb returns), corner building (limestone pavilion and quoins, brick, windows, belt courses, mitred cornice, corner and end mansard caps, north-end balcony and stair), north-street row (turret plex: corbel, octagonal turret, windows, spire; limestone and brick plexes), east-street row (brick and limestone plexes, stone bays and teal caps at the party lines), doors and door pairs (colours, stoops), windows (frames, transoms, sills, lintels), gallery and third-floor balconies (decks, fascias, brackets, railings), iron exterior stairs (treads, stringers, rails, pickets, curl, newel), cornices and consoles, flat roofs, parapets, vents and chimney, front yards (paving, fences, gaps at stairs and stoops, shrubs), sidewalks (joints, tree pits, street trees), roadway and parked cars, context rows, block interior, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plateau/v002/review/independent-review.md. Do not run the build.

## Context for this review (v002)

v001 was reviewed FAIL with P0 = 0, P1 = 6, P2 = 8 (`tools/clay_montreal_plateau_rue/evidence/v001/independent-review.md`).
v002 targets the six P1s; score against v001 (0 / 6). Judge from the pixels.

| v001 P1 | v002 change | where to look |
|---|---|---|
| 1 stair stringer through the gallery deck; stair arriving under the fascia; balcony brace through the stringer | Each stair now starts with a landing tread flush with the deck (5 mm under the deck top, lapping 5 cm under the deck end) just past the open railing end; both stringers start 3 cm past the deck end, below the landing, so nothing rises through the deck or the fascia. The gallery bracket on the stair side moved 0.5 m inboard, clear of the stringer. Applies to every plex stair and the corner building's stair. | front, iron_stair, balcony_gallery, facade_close |
| 2 curl does not read (Z-jog in the handrail, loose tall newel) | The v001 rails paired the street-side flight rail with the curl's outer (wall-side) radius, causing the jog. Now the wall-side rail runs continuously down the flight and round the outer radius of the quarter turn to a foot newel capped at rail height; the street-side rail ends on a central newel capped at its own rail height at the flight foot. Winders are fanned about the centre, and the last riser steps onto the yard (no tread on the yard plane). | iron_stair, front, balcony_gallery, sidewalk_trees |
| 3 pure-black slit at the turret/parapet seam (left_side) | Ray-cast to the north row end (y = 70): the cornice end cap and the facade carrier's end face were coplanar. A cornice end that faces a lower neighbour or a row end now runs 3 mm past the party line (the corner building's cornice too, which previously stopped 2 mm short). | left_side, right_side, roof_parapets |
| 4 rear windows as flat dark rectangles | Every rear window (all plexes and the corner building's courtyard faces) is now a white frame standing 9 cm proud with the glass set 6 cm back inside it, and a stone sill. | rear, rear_yards, roof_parapets, rear_side |
| 5 context rows boarded up | Context windows: white surround, glass 3 cm proud of it, stone sill. Context balconies: top and bottom rails with pickets at 0.3 m and open returns (no solid slabs). | left_side, right_side, aerial, roof_parapets, rear_side, sidewalk_trees |
| 6 corner_building camera cuts the corner cap | Pulled back and raised (location (-12, -12, 7.5), target (6, 6, 8), 24 mm); the cap and finial clear the top edge. | corner_building |

The P2s are untouched except as side effects. GLB 3,989,084 bytes.
