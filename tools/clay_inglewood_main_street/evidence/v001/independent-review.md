# Independent holistic review: clay-inglewood-main-street v001 (RLASM v6.1, architectural clay)

Reviewer: independent; did not build this candidate. Evidence used: only locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`), the 18 PNGs in `renders/`, and the 4 phone boards. Every render and all three sources were opened at full resolution, and zoomed crops were made (into a new scratch folder) of the source corner/middle blocks, the source bulb-out, the source front block sequence, the render end block, the rear windows, the bracket console and both top-view street bands. Metadata, build reports and builder notes were not used as proof.

## 1. Verdict

**Verdict: VISUAL_REWORK_REQUIRED.** The street section reads correctly overall: the band order, angled parking, double yellow line, brick crossings, furniture and the five-block street wall are all there. Five clearly visible fidelity and coherence defects still block approval: the corner block is merged with the lower bay next to it, the middle block has the wrong window heads, the end block is not taller, the bulb-outs have the wrong surface and taper, and the rear windows are painted on.

Counts: P0 = 0, P1 = 5, P2 = 11

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top, front_corner, left_side, corner_entrance, aerial (vs top.jpg, oblique.jpg) | In top.jpg the frontage next to the cross street is a narrow corner block (about 160 px), then a separate bay with a lower membrane roof and rooftop plant (about 140 px). Above that lower roof, the middle block's brick side wall with punched windows is exposed (clearly visible in oblique.jpg). Its main-street face carries about 3 window bays. The render instead makes this whole frontage one full-height corner block (top 180-535 px) with about 9 evenly spaced single windows (left_side, front_corner). The lower bay, its own roof level and the exposed side wall are missing, and the corner block's upper windows are single and evenly spaced, not paired. | The corner-block footprint was stretched across two source lots, and its window grammar was repeated across the merged width. | Split the footprint at the source ratio (about 53:47 corner:lower bay in top.jpg). Drop the second bay's roof and parapet below the corner and middle blocks, and expose the middle block's west party wall above it with punched, recessed windows. Group the corner block's upper windows into pairs across about 3 bays on the main street, keeping the belt and white cornice turning the corner. |
| 2 | P1 | front_corner, roof_parapets, aerial, right_side | Every upper window on the middle block (the one with the raised parapet and name panel) has a full semicircular head with a cream hood. These are the same heads as the round-arched block two lots east, so the street wall loses its block-by-block window differentiation. The brief calls for segmental arches here, and in oblique.jpg the middle-block windows are near-flat or segmental heads under stone lintels, not semicircles. | The round-arch window module was reused for the middle block. | Give the middle block's upper windows segmental heads (rise about 1/6 to 1/8 of the span) with a cream lintel or hood, and keep semicircular heads only on the round-arched block. Keep the bracketed block's segmental hoods distinct from both. |
| 3 | P1 | right_side, aerial, front_corner, front (vs front.png) | The end block (cream fascia, cream end pier, flat-headed windows) has its coping at the same height as the round-arched block beside it, and its upper windows have the same proportions as the neighbours'. In front.png the end block is clearly the tallest: its second storey and parapet rise well above the round-arched block's corbelled cornice, and its upper windows are much taller. The "taller end block" identity cue is absent. | The end block uses the shared storey height and window module. | Raise the end block's second storey and parapet by about 1.0 to 1.5 m relative to its neighbour, and lengthen its upper windows to about 2.2:1 height to width with flat stone lintels and sills. Carry the cream fascia and end pier to the new height. |
| 4 | P1 | top, front_corner, crosswalk_bulbout, left_side, front (vs top.jpg, oblique.jpg) | The curb extensions at the cross street are almost entirely red brick: one large brick rectangle fills each bulb-out, and it merges with the brick crossings into one red field. They also taper back to the parking lane with a straight 45-degree chamfer. In top.jpg and oblique.jpg the bulb-outs are pale scored concrete with a narrow brick band that follows the curved curb, plus small brick pads at the lamp and bench, and the tapers are smooth reverse curves. This inverts the materials hierarchy at the most visible node. | "Brick pads" was modelled as a full-surface brick slab, and the taper was a simple polygon chamfer. | Pave the bulb-outs in pale concrete with scored joints. Continue the furnishing-strip brick band around the bulb-out curb, keep small brick pads only under the bench and lamp, and replace the straight chamfers with curved tapers (radius about 3 to 4 m) at both cross-street and mid-block bulb-outs. |
| 5 | P1 | rear, rear_lane, rear_side | Every rear upper window on the north row is a flat dark rectangle painted flush on the wall with only a thin sill: no reveal, frame, glazing or head. The rear walls also have none of the brick coursing used on the street faces, and they read as untextured slabs. No source shows these faces, but this is incoherent with the deep-reveal front grammar and falls under the explicit "openings without visible depth or returns" failure. | The rear facades are placeholder decals and flat material. | Cut the rear openings with 100 to 150 mm reveals, a frame and dark glazing, a brick segmental or flat head, and a sill. Apply the same brick coursing material as the street faces. Keep the rear doors recessed likewise. |
| 6 | P2 | storefront_close, angle_parking | The bulkheads are plain flat green slabs with no panelling. | Simplified bulkhead box. | Add 1 or 2 inset panels per bay. |
| 7 | P2 | sidewalk_section, front, right_side | The street trees have large low-poly crowns that reach the second-floor sills. The source trees are young and slim with small, open crowns. | Generic crown scale. | Reduce crown diameter by about 35% and narrow the trunks so they read as young trees. |
| 8 | P2 | top, right_side, aerial | The mid-block white ladder crossing sits on plain asphalt. In top.jpg it sits on a red brick band with white edge lines. | Crossing material not applied. | Lay a brick band under the ladder bars, with edge lines. |
| 9 | P2 | roof_parapets, front_corner (vs oblique.jpg) | The middle block's raised stepped parapet is low and short. The source gable rises markedly with a stepped or curved profile. The modillions are faint dashes. | The parapet was under-scaled. | Raise the central parapet by about 0.8 m and widen the name panel; deepen the modillions. |
| 10 | P2 | arched_windows (vs front.png) | The round-arched windows have cream stone hoods with keystones. The source arches are brick voussoirs. | Shared hood module. | Switch the hoods on that block to brick arches. |
| 11 | P2 | bracketed_cornice, front | The end console of the dark bracketed cornice comes down directly over the head of the adjacent window and crowds or occludes its hood. | Window bay not offset from the console. | Shift the end window inward or narrow the console so they are at least 150 mm apart. |
| 12 | P2 | right_side, left_side, crosswalk_bulbout, aerial | Context buildings (the block east of the end block, and the corners across the cross street) have flat painted window squares or completely blank street walls. | Context placeholders. | Give the street-facing context walls simple recessed openings. |
| 13 | P2 | (review coverage) | The brief's list of detail views names facade_close, architecture_close and glass_close, but no such renders exist. The brief's own count (18) matches the 18 renders present, and storefront_close and arched_windows cover glazing and architecture. | View list includes roles not produced. | Render the three named views, or correct the view list. |
| 14 | P2 | top (vs top.jpg) | The north sidewalk is about 15% wider relative to the half-carriageway than in top.jpg (building line to curb). | Band width rounding. | Trim the sidewalk band to the source ratio. |
| 15 | P2 | front, angle_parking | The car placeholders have a translucent green glass cabin box that reads oddly at eye level in the front view. It sits correctly on the body, so this is not floating. | Glass material on placeholder cabin. | Make the cabin opaque clay. |
| 16 | P2 | top (vs top.jpg) | The first stall after the cross-street bulb-out is not drawn as the source's closed triangular hatch. | Marking omitted. | Add the triangle closing line. |

No P0 findings. Every element is in contact with the ground or its host. The street wall is continuous at two storeys, the section is legible, and every camera shows its target.

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Section order (storefronts, sidewalk, brick furnishing strip, 50-degree angled parking, travel lane, double yellow centre line, travel lane, parking, strip, sidewalk, south row) and mirror | conforms | top, right_side, angle_parking |
| Section widths | deviates (minor): north sidewalk about 15% wide (#14) | top vs top.jpg |
| Curb extensions and tapers | deviates: all-brick surface, straight chamfer tapers (#4) | top, crosswalk_bulbout, front_corner |
| Angled stall lines and edge line | conforms (about 50 degrees, edge line present); first-stall triangle missing (#16) | top, angle_parking |
| Double yellow centre line | conforms | angle_parking, crosswalk_bulbout |
| Brick crossings with white edge lines at the intersection (both streets) | conforms | left_side, crosswalk_bulbout, top |
| Mid-block white ladder crossing | conforms (ladder and bulb-outs present); not on brick band (#8) | top, right_side, aerial |
| Sidewalk scored joints | conforms (faint grid) | angle_parking, sidewalk_section, top |
| Brick furnishing strip and tree pits | conforms on the straight run; strip does not follow the bulb-outs (#4) | angle_parking, street_furniture, top |
| Young street trees | deviates (minor): crowns oversized (#7) | sidewalk_section, front |
| Black lamps with red banners | conforms | crosswalk_bulbout, right_side, front |
| Bins | conforms | angle_parking, sidewalk_section |
| Bike hoops | conforms | street_furniture, sidewalk_section |
| Benches on bulb-outs | conforms | crosswalk_bulbout, left_side, top |
| Corner block: pier at the corner | conforms | corner_entrance |
| Corner block: stone belt and white cornice turning the corner | conforms | corner_entrance, rear_side |
| Corner block: side shopfronts | conforms | corner_entrance, rear_side |
| Corner block: paired upper windows, width and bay count | deviates: single evenly spaced windows; block merged with the lower adjoining bay (#1) | left_side, corner_entrance, top |
| Lower-roof bay between corner and middle blocks | deviates: absent (#1) | top, front_corner |
| Middle block: cream pilasters and sign band | conforms | front_corner, roof_parapets |
| Middle block: segmental windows | deviates: semicircular (#2) | roof_parapets, front_corner |
| Middle block: modillion cornice | conforms (weak, #9) | roof_parapets |
| Middle block: raised stepped parapet with name panel | conforms (under-scaled, #9) | roof_parapets, front_corner |
| Bracketed block: dark bracketed metal cornice, segmental windows, dark sign band | conforms | bracketed_cornice, front, aerial |
| Round-arched block: round-arched upper windows, corbelled brick cornice | conforms (hood material minor, #10) | arched_windows, front |
| End block: cream fascia, cream end pier, flat-headed windows | conforms | right_side, aerial |
| End block: taller | deviates (#3) | right_side, aerial, front_corner |
| Storefront glazing, transoms, glazed doors | conforms | storefront_close, corner_entrance, street_furniture |
| Panelled bulkheads | deviates (minor): plain (#6) | storefront_close |
| Blade signs | conforms (simple boxes) | corner_entrance, street_furniture, sidewalk_section |
| Roofs: flat gravel inside parapets, rooftop units | conforms | roof_parapets, rear, top |
| Back lane | conforms in layout; rear openings flat and incoherent (#5) | rear_lane, rear, top |
| South-side context row, corners across the street, low buildings beyond the lane | conforms as plainer context (#12 minor) | right_side, left_side, aerial, top |
| Materials hierarchy (red brick, cream trim, dark green storefronts, pale concrete, red brick paving, dark asphalt) | conforms except bulb-out paving (#4) and untextured rear walls (#5) | front, front_corner, angle_parking |
| Vehicles as simple clay placeholders; no people, dogs or awnings | conforms | front, top, angle_parking |

## 4. Camera validity

- front: valid. It matches the front.png role: an eye-level view from the mid-block bulb-out looking along the north wall, with the end, round-arched, bracketed and middle blocks in source order and the ladder crossing in the foreground. Nothing occludes the target.
- front_corner and aerial: valid. front_corner matches the oblique.jpg role. In aerial, the foreground south-row roofs take up a large share of the frame but the north street wall and section stay legible (P2 note only).
- top: valid, a nadir view over the governing plan.
- left_side, right_side, rear_side: valid and legible.
- rear: valid. A foreground context box hides the lane surface in the lower third, but the rear walls, the target of this view, are legible.
- rear_lane: valid.
- All detail views (storefront_close, bracketed_cornice, arched_windows, corner_entrance, angle_parking, crosswalk_bulbout, street_furniture, sidewalk_section, roof_parapets): valid, unclipped and legible.
- facade_close, architecture_close and glass_close are named in the brief's view list but were not rendered (#13). The brief's stated count of 18 matches the delivered set, so no view is invalid. Those three roles are covered only indirectly.

No view has its target occluded, clipped or illegible.

## 5. Previous-version findings

This is the first version (v001), so there are no previous-version findings to carry forward or close.
