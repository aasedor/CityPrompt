You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/streetcar/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, streetcar_nose, pantograph_wire, track_slab, span_wire_pole, intersection_crossing, corner_storefront, victorian_arches, condo_balconies, east_sidewalk, roof_skylights)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a street option, not a building: a straight north-south run of a Toronto streetcar main street north of a cross street, the top view governing the plan. The section, building line to building line about 25 m: a 3.9 m west sidewalk and a 5.3 m east sidewalk of pale scored concrete with red brick-paver furnishing strips at the curb holding tree pits with young trees, bins and tall grey steel poles; a wide curb lane each way with white lane dashes; two centre track lanes on a pale concrete track slab with transverse joints, carrying twin embedded grooved-rail streetcar tracks (1495 mm TTC gauge) either side of a single yellow centre line. Overhead: span wires strung pole to pole across the street with hangers and insulators carry two contact wires, one over each track, and the same poles carry long-armed cobra-head street lights. A red-and-white five-module articulated low-floor streetcar (Flexity type: red skirt, white band, dark window band with black joint stripes, white band, red roof band, sloped cab ends with large windscreens and an amber destination sign) runs northbound on the east track mid-block with its pantograph raised to the wire. At the cross street: corner curb returns, Toronto two-line crossings over both streets, stop bars, a yellow centre line on the cross street, and a red TTC stop pole on the east corner. The street wall: on the west a three-storey red-brick Romanesque corner block with segmental second-storey and round-arched third-storey windows, a corbelled stone cornice that turns onto the cross street and a central gabled parapet with a plaque; a plainer three-storey brick block with a white bracketed cornice; a seven-storey brick condominium wing with glass-railed balconies on alternate bays in front of a ten-storey glass slab with floor bands, a green roof and a penthouse. On the east a three-storey red-brick corner block with storefronts on both streets and two glazed hipped roof skylights; a second three-storey brick block with segmental windows and a bracketed cornice; a low two-storey block with a dark roof; and a six-storey charcoal-framed condominium with continuous glass-railed balconies, a green roof and a set-back penthouse. Storefront glazing at grade throughout. The blocks south of the cross street, beyond the corner blocks and beyond the back lanes are plainer context; the pedestrians in the sources are not modelled. Judge it as a street section: band order and widths, track slab and rails, overhead line, markings, surfaces, furniture, planting, the streetcar, and the street wall at pedestrian scale, not storeys; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (Toronto streetcar main street: twin embedded tracks on a concrete slab in the centre lanes under span-wire contact wires, a red-and-white articulated streetcar with its pantograph up, wide curb lanes, brick-strip sidewalks, and a Victorian red-brick storefront street wall with newer balconied condominiums),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/streetcar/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: section order and widths (storefronts, sidewalk, brick furnishing strip, curb lane, track lane, yellow centre line, track lane, curb lane, strip, sidewalk), track slab with joints, twin grooved-rail tracks at the right gauge and centres, white lane dashes, crossings and stop bars on both streets, curb returns, poles and span wires, hangers and insulators, contact wires over each track, cobra-head lights, the streetcar (modules, livery bands, joints, cab ends, windscreen and destination sign, doors, wheels on the rails, pantograph at the wire), TTC stop pole, tree pits and young trees, bins, west Romanesque corner block (arches, corbelled cornice turning the corner, gable and plaque, corner pier), plainer west block, west brick condominium wing and glass slab, east corner block (storefronts on both streets, skylights), east brick and low blocks, east charcoal condominium (balconies, green roof, penthouse), storefront glazing, transoms, bulkheads and doors, roofs and parapets, context south of the cross street, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/streetcar/v003/review/independent-review.md. Do not run the build.
This is version 3. The v002 review found 0 P0 and 1 P1.
1. The streetcar cab nose was only partly fixed (the v001 cab-nose finding). The windscreen wrapped the corners and the plan corners were rounded, but in side profile (east_sidewalk) the cab end ran dead vertical with no visible rake. In streetcar_nose, track_slab and front, the red cap was a flat panel with a straight horizontal top and square shoulders, where the source cap is domed and rounded.

The builder claims it is fixed. This is the second targeted fix of the cab-nose finding:
- The two end modules' boxed bands, red roof band and grey roof now stop 1.9 m short of each cab end. They had run to the cab-end line and masked the nose behind a square box end.
- That last 1.9 m is lofted from plan rings in the body's livery bands: red skirt, white band, the glass band (the wrapped windscreen at the front), upper white band and red roof cap.
- In profile the nose reaches 0.52 m ahead of the cab-end line at the light band. It rakes back about 20 degrees over the windscreen (0.51 m at 1.30 m height to 0.02 m at 2.65 m), then curves back about 1 m into the roof as a domed red cap.
- The cap's plan corners grow from 0.62 m to about 0.85 m radius, and its sides draw in by up to 0.40 m at the top, so it has rounded shoulders that blend back to the body's square section at the junction.
- The swept surfaces are smooth-shaded.
- Front overlays wrap 0.1-0.42 m round the corners: a white lower apron, a red light band with the headlights, the windscreen running up to 2.68 m, and a red brow joining the cap. The amber destination sign follows the rake at the windscreen head. A white pillar marks the windscreen edge on each side.

Verify it in the pixels; do not take the builder's word. Check the rake in profile in east_sidewalk. Check the domed cap and rounded shoulders in streetcar_nose, front and track_slab. Check that the junction between the boxed body and the lofted cab shows no gap, step slot or black seam, at both ends (rear for the south cab).

Earlier fixes that must still hold:
- White-dominant livery on every module, bottom to top: red skirt 0.30-0.75 m, wide white band 0.75-1.18 m, dark window band 1.18-2.40 m, wide white band 2.40-2.85 m, narrow red roof band 2.85-3.10 m.
- The west Romanesque corner block's cross-street facade: one corner shopfront with a short sign-band return, a mostly solid coursed-brick ground storey with doors and small sashes, and pairs of flat-headed sashes at an irregular rhythm on both upper storeys. The main-street facade keeps its segmental and round arches and storefront arcade.
- The front_corner camera holds the whole glass slab with its green roof and penthouse.
- Smaller street trees.
- Twin grooved-rail tracks at 1495 mm gauge on the pale centre slab with a single yellow line.
- Span-wire catenary on paired poles with real contact-wire tubes, and the pantograph touching the wire.
- The TTC stop pole.
- The Romanesque main-street facade with segmental second-storey and round-arched third-storey windows, the corbelled cornice and the central gable.
- The east corner block with storefronts on both streets and two skylights.
- The brick condo wing and charcoal condo with glass-railed balconies.
