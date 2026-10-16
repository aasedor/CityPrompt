# Independent holistic review: hospital v004 (RLASM v6.1 architectural clay)

Reviewer: independent; not the builder. Evidence: rendered pixels in `renders/` and `boards/`, compared against `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg` only. I read all 18 renders at full resolution, the three sources and the four phone boards. I made zoomed crops in a separate scratch folder (`indrev_hosp_v004_crops/`). I did not change any candidate file.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The v003 hanger-rod defect is fixed and the three-volume envelope, storey counts and identity elements now match the sources. One P1 is left: the main entrance under the cable-hung canopy is closed off by the atrium's diagonal mullion net, which runs all the way to grade across the doors. The source shows a clear storefront with a revolving door at that position.

Counts: P0 = 0, P1 = 1, P2 = 11

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, entrance_canopy, front_corner (crop) | Below the entrance canopy, the atrium's diamond mullion net keeps going to the pavement. Diagonal members cross the full door zone, and the two curved revolving-door drums sit behind the lattice with no clear opening. In the source front, the net stops at the canopy line. Below it is a straight vertical-mullion storefront with a revolving door at right of centre and posts in line with it. The hospital's main public entrance reads as closed. | The atrium diagrid generator fills the whole south face from z=0 up and ignores the entrance zone. | Stop the diagrid at a transom at canopy height, around the top of the ground storey. Below it, fill the atrium's south face with a vertical-mullion storefront and a recessed revolving door, plus one swing-door pair, with visible jambs and reveals. Keep the canopy posts on the storefront grid. |
| 2 | P2 | entrance_canopy | This detail camera is under the canopy at close range. It shows the two edge beams and posts against the atrium base, but not the glass top, the hanger rods or their anchors. The canopy's identity can be checked only in front, front_corner and architecture_close. | The camera target and height are set to the atrium base, not the canopy. | Raise the camera to about first-floor height, set it back 8 to 10 m south-south-west, and aim at the canopy front edge so that the rods, anchors and glass deck all appear in one frame. |
| 3 | P2 | front, right_side, rear, rear_side, rear_north | The ward exoskeleton columns continue to grade in front of the brick base on every face, so the base reads as a colonnade. In the source front and oblique, the braced frame bears on a ring beam at the top of a solid brick podium, and no columns run down the brick. | The column extrusion starts at z=0 instead of at the podium top. | Start the exoskeleton columns at the podium ring beam, or drop only the corner columns to grade if structural expression is wanted. |
| 4 | P2 | front, front_corner vs source front/oblique | The atrium is a narrow full-depth slot, about 11% of the frontage. In the source front and oblique, the atrium is a wide glass box that projects toward the street. The top source supports the narrow slot, and the brief says the top view governs the plan, so this is a source conflict, not a build error. | Plan taken from the top source. | Optional: widen the atrium toward the source-front proportion if the top source allows, or record the conflict. |
| 5 | P2 | front, architecture_close | The signage panel sits among perforated screens, with a dark glazing strip to its east. In the source, the clinical block's east end bay is plain pale panelling that frames the sign, with no perforation. | The perforated-screen module is applied across the whole south face. | Swap the last screen bay or two either side of the sign for solid pale panels. |
| 6 | P2 | facade_close, architecture_close | The perforations read as flat mid-grey printed squares. The strip glazing behind does not show through. | Perforations are a texture or decal, not openings. | Cut the perforations through, or give them a darker see-through value, so the glazing behind registers. |
| 7 | P2 | front, left_side, front_corner, aerial | The ward roof sits level with the top of the raised roof canopy. In the source oblique and front, the ward rises clearly above the canopy and crowns the composition. Storey ratios to the brick base are otherwise consistent. | The canopy posts are a little tall, or the plant storey is a little high. | Lower the canopy deck by about half a storey, or add a parapet upstand to the ward, so the ward reads as the tallest volume. |
| 8 | P2 | front (above atrium roof), roof_canopy | The east leg's west face above the atrium roof is plain grey panel in the front view and plain mullioned glazing in roof_canopy. It has no exoskeleton, so it breaks the ward's braced grammar. No source shows this face. | The exoskeleton is emitted only on street faces and the courtyard face of the north bar. | Carry the braced frame, or at least columns and ring beams, onto the visible part of this face. |
| 9 | P2 | front, front_corner | The entrance canopy has two posts, at its outer front corners. The source places slender posts in the storefront line under the canopy. | Simplified post layout. | Move the posts, or add posts, on the storefront mullion grid. This ties into fix 1. |
| 10 | P2 | braced_frame, rear_north | Each X-braced tier is about 1.4 clinical storeys tall and has a floor slab at mid-tier. In the source south face, each X spans two glazed storeys and is more elongated. | The tier height is not set to an integer number of ward storeys. | Set the tier height to two ward floors so the slabs fall on ring beams and the mid-node. |
| 11 | P2 | interior | The atrium interior is very dark, though still legible: clinical brick and screens at left, ward glazing at centre and right. | Low interior light. | Add an interior fill light, or raise the exposure for this view. |
| 12 | P2 | brick_base | The windows have only shallow reveals and the jamb return is barely visible. The brick shows horizontal coursing only. | Shallow inset. | Deepen the window inset to about 150 to 200 mm so the jamb and head returns read. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Overall silhouette (low screened block, taller braced block, glass atrium between, raised roof canopy) | conforms, with small deviation (ward roof about level with canopy, P2 #7) | front, front_corner, aerial vs source front/oblique |
| Storey counts: clinical 2 brick + 5 screened + recessed plant | conforms | front, left_side |
| Storey counts: ward 2 brick + braced tiers | conforms (2 brick + 5 tiers, the same tier count as the oblique; tier/floor rhythm P2 #10) | front, right_side, rear vs oblique |
| Plan: three volumes (clinical SW; L-shaped ward N + E; atrium between) | conforms to the top source | top, aerial vs top.jpg |
| Clinical: two-storey red brick base with large windows | conforms (reveals shallow, P2 #12) | front, brick_base, left_side |
| Clinical: perforated pale screens over strip glazing | conforms (perforations flat, P2 #6) | front, facade_close |
| Clinical: tall dark signage panel near east end | conforms (surrounding solid end bay missing, P2 #5) | front, front_corner, architecture_close |
| Clinical: recessed plant storey behind dark louvre band | conforms (setback ledge visible) | front, roof_canopy |
| Clinical: raised canopy frame over western roof | conforms (posts land on the plant-storey parapet; perimeter frame and deck present) | top, roof_canopy, front |
| Ward: exoskeleton bays, columns, ring beams | conforms (columns to grade, P2 #3) | braced_frame, rear_north, right_side |
| Ward: full-height X-braces with node plates | conforms | braced_frame, rear_north, front |
| Ward: brick base at east street | conforms | right_side, front_corner |
| Atrium: full-height glass with diagonal mullion net | conforms above canopy; **deviates at ground floor** (net blocks the entrance, P1 #1) | front, glass_close, architecture_close, entrance_canopy |
| Atrium roof | conforms (glazed, gridded roof between the clinical plant storey and the ward) | aerial, top, roof_canopy |
| Entrance canopy: glass deck, tension rods | conforms; the rods are anchored on structure (see section 5) | front, front_corner, aerial, architecture_close |
| Entrance canopy: posts | deviates, minor (corner posts only, P2 #9) | front, front_corner |
| Roof plant (ward roof units, clinical plant-roof units) | conforms | roof_plant, aerial, top |
| Materials hierarchy (red brick base < pale screens / grey steel < glass; dark louvre and sign accents) | conforms | all whole-envelope views |
| North and west faces of ward (not in sources) | coherent with the visible grammar | rear, left_side, rear_north |

## 4. Camera validity

- Whole-envelope views (front, front_corner, aerial, top, left_side, right_side, rear, rear_side): valid. The whole asset is in frame and legible in each, with nothing occluded or clipped.
- facade_close, architecture_close, glass_close, braced_frame, roof_canopy, roof_plant, brick_base, rear_north: valid and legible.
- entrance_canopy: weak (P2 #2). The frame is valid, but its named subject, the canopy deck and rods, is mostly out of frame. It does show the entrance blockage in P1 #1.
- interior: legible but very dark (P2 #11).
- No view has an occluded target or a clipped asset. No view is an invalid camera at P0 level.

## 5. Previous-version finding (v003) check

**v003 P1, "several entrance-canopy hanger rods end on non-structural surfaces (the signage panel, the perforated screen face, mid-pane on the atrium glass) with no visible anchor": RESOLVED in the pixels.**

- front (zoomed): the rods run in three pairs. The west pair converges on the atrium's west steel edge post. The middle pair converges on the atrium's east edge post. The east pair rises to the middle column of the ward leg's braced frame, at a ring-beam node. None ends on the signage panel, the screen face or mid-pane on the atrium glass. The west pair passes in front of the sign in projection but terminates on the post.
- architecture_close: small anchor plates are visible at all three origins: the west atrium post, the east atrium post, and the ward column at its ring-beam node. The rods fan down from each plate.
- front_corner and aerial (zoomed): the same three anchor origins. All rods land on the canopy's front edge, and none pass through the canopy deck or the diagrid.
- glass_close: one rod passes in front of the diagrid toward the ward column. It does not terminate on the glass.

The builder's claim (pairs from three anchor plates on structure only, down to the canopy front edge) agrees with the pixels.
