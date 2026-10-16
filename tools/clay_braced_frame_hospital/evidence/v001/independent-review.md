# Independent holistic review: clay-braced-frame-hospital v001

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The massing, storey counts and plan follow the locked sources (three volumes, an L-shaped ward block, the atrium between them, the canopy at the south). Six P1 defects block approval. Two are identity faults on the steel exoskeleton (one face missing, wrong tier rhythm). One is an extra black corner element that appears in most envelope views. The other three are black node artefacts, an atrium that reads as a recessed slot instead of a glass volume, and a screen pattern of diagonal dark streaks that the sources do not show.

Counts: P0 = 0, P1 = 6, P2 = 8

Method: I opened all 18 renders, the 4 phone boards and the 3 locked sources (front.png, oblique.jpg, top.jpg) at full resolution. I wrote zoomed crops only to the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/hospital-v001-review-crops/`. I did not consult metadata, the builder's evidence files or the scripts.

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, front_corner, aerial, roof_canopy (sources: front, oblique, top) | The south face of the ward block's north bar, above the clinical plant storey and the atrium, is plain strip glazing with no exoskeleton. Above the atrium, the front view shows a blank grey panel with a sloping top edge. In all three sources this face carries the full X-braced frame: the source front shows two tiers of X above the atrium at x≈540–700, the oblique shows the braced face above the clinical roof, and the top view shows a braced band along the bar's south edge. The top render shows the frame line only on the north, east and west edges of the bar. | The exoskeleton generator runs only on street-facing faces, so the courtyard face of the bar was skipped. | Run the same column, ring-beam and X-brace module along the bar's south face from the atrium's east edge to the bar's west end, above the clinical roof line. Clad the blank panel over the atrium with that bay module. Then confirm in front, front_corner and aerial. |
| 2 | P1 | front (right edge), front_corner, aerial, right_side (left edge), rear_side (left edge), glass_close (right), entrance_canopy (black vertical seam at the brick corner and black horizontal band behind the canopy) | A solid black vertical bar about 1 m wide runs the full braced height at the south-east corner of the ward's east wing. It stands outboard of the brick base and stops at the bottom of the frame. The top view shows it as a black dot at the corner. In entrance_canopy, a black seam runs from ground to frame at a brick corner, and a thick black band runs along the back edge of the canopy where it meets the atrium. No source has any black element at the corner; the source corner column is the same grey steel as the others. | Either a stray dark-material corner closure or edge cap, or a gap between the glazing and brick volumes that exposes an unlit void. | Delete the black corner element, or close the corner with the standard grey steel column and glazing return. Give the canopy back beam the steel material. Make sure the brick base volumes meet without a slot. Check the corner again in front_corner, right_side and entrance_canopy. |
| 3 | P1 | braced_frame, rear_north, architecture_close, roof_plant, entrance_canopy (upper right), glass_close (diagrid nodes) | Every crossing of an X-brace shows a black diamond, and every diagrid node shows a black dot. They read as holes through the steel, at every node of the main identity element. | The two diagonals are coplanar and overlap at the crossing, which leaves inverted or coincident faces. Or a black node material was assigned. | Offset one diagonal by a few cm in depth, or boolean-union the pair. Alternatively, add a node plate in the steel colour at each crossing. Recolour the diagrid nodes to steel. |
| 4 | P1 | right_side, rear, front, left_side, rear_north, front_corner (sources: front, oblique) | The exoskeleton has three tall tiers, each X spanning about two storeys with a tall-narrow aspect of about 1:1.6, plus a squat half-height tier at the top with smaller, flatter X's. In the sources the braced shaft has about five even tiers of near-square X panels. The oblique shows about 5 tiers on the street face above the brick base; the source front shows 4–6 tiers. The changed top tier breaks the frame grammar. | Ring beams are placed every two floors over a seven-storey braced height, and the leftover storey becomes a short tier. | Split the seven braced storeys into equal tiers: 5 tiers of 1.4 storeys, or at minimum 4 even tiers. Put ring beams on those lines and use one near-square X per bay per tier. Remove the special top tier. |
| 5 | P1 | front_corner, aerial, front (sources: front, oblique) | The atrium is a narrow recess between the clinical block and the east wing, slightly behind both faces. In front_corner and aerial, the views matched to the oblique, it is almost invisible behind the east wing. In the source oblique and front it is a separate full-height glass volume: it stands forward with side returns, a visible glass top and a diagonal net across its whole face, and it is the second-strongest element after the exoskeleton. | The atrium was modelled as infill between volumes with its face on or behind their line, so it has no projection or returns of its own. | Keep the width from the top view, but bring the atrium face 2–3 m forward of the clinical and east-wing faces. Give it glazed side returns with the diagonal net and its own roof edge, set below the ward parapet. Hang the canopy from that projecting face. |
| 6 | P1 | front_corner, aerial, front, left_side, facade_close (sources: front, oblique) | On the clinical block, the five screen storeys have one open, unscreened dark bay per row, offset by one bay each row. The result is strong diagonal dark streaks across the south and west faces, very visible in front_corner and aerial. In the sources the perforated pale screens form a continuous field over the strip glazing, with no open bays and no diagonal pattern. | The screen-panel generator leaves out a panel on a stepped offset each row. | Fill the screen field without gaps over the strip glazing. Get variation from perforation density or small panel offsets, not by removing panels. Leave the sign-panel zone as it is. |
| 7 | P2 | entrance_canopy, front | There is no expressed entrance door or revolving door under the canopy. The atrium base continues as the diagonal-net glazed wall down to the ground. The source front shows glazed entrance doors. | Ground-floor entrance not modelled. | Add a glazed door set with a frame recess under the canopy. |
| 8 | P2 | right_side, front, front_corner | The exoskeleton's bottom ring beam overhangs the brick base face by about 1 m, with no cornice or columns down to grade. In the source the frame sits on a projecting base cornice, and its corner columns run down to the ground in front of the brick. | The frame offset is applied above the base, but the base footprint is not grown to match. | Add a projecting cornice under the frame, or carry the corner and mid columns down to grade. |
| 9 | P2 | brick_base, entrance_canopy | The brick coursing reads as horizontal lap siding in a salmon tone; the source brick is a deeper red-brown. | The coursing texture is too regular and has no vertical joints. | Darken the base tone toward the source and add perpend (vertical) joints, or soften the coursing lines. |
| 10 | P2 | facade_close, architecture_close | The perforations are a few large square holes per panel, which read as tiny windows. The source perforation is fine-grained. | The perforation module is too coarse. | Use a smaller pitch and smaller holes, or a density map. |
| 11 | P2 | interior | The interior view is badly underexposed. The atrium side walls and the glazed ward face can just be read, but the diagrid net from inside is not legible. | No interior light fill, and the camera is aimed away from the net. | Raise interior or world fill and aim the camera to include the diagrid. |
| 12 | P2 | top, rear_side, roof_plant | Roof vents cast triple, propeller-like shadows from the multiple lights. | Multi-light rig. | Reduce the rig to one key light for roof views, or soften the fill shadows. |
| 13 | P2 | front, front_corner | The entrance canopy is narrower than in the source front, where it extends well past both sides of the atrium. It matches the top view, so this is polish only. | Canopy width taken from the top view. | If wanted, widen it by about one bay on each side. |
| 14 | P2 | front (above the atrium) | Behind and above the atrium top there is a sliver of grey face with a sloping edge, where the junction between the atrium roof and the ward bar is unresolved. Finding 1 likely resolves it. | Junction left unclad. | Fix through finding 1. |

## 3. Source conformance checklist

| Item | Status | View used |
|---|---|---|
| Overall silhouette (low clinical block with raised roof canopy, taller braced ward, glass atrium between) | conforms in massing, deviates in atrium presence (finding 5) | front, front_corner vs source front and oblique |
| Storey counts: clinical has a 2-storey brick base, 5 screen storeys and a plant storey | conforms | front, left_side |
| Storey counts: ward has a 2-storey brick base and about 7 braced storeys, roughly 1.25–1.3 times the clinical height, matching the source ratio | conforms | front, right_side vs source front |
| Plan: three volumes (clinical at the SW, ward as an L across N and E, atrium between, canopy to the south, streets on S, W, E) | conforms | top vs source top |
| Clinical: brick base with large windows | conforms (P2 tone and coursing, finding 9) | front, brick_base |
| Clinical: perforated pale screens over strip glazing | deviates (finding 6, open-bay diagonal streaks; P2 perforation scale) | front_corner, aerial, facade_close |
| Clinical: tall dark signage panel near the east end | conforms | front, architecture_close |
| Clinical: recessed plant storey behind a dark louvre band | conforms | roof_canopy, front |
| Clinical: raised canopy frame over the western roof | conforms | roof_canopy, top, front |
| Ward: exoskeleton bays | deviates (finding 1, missing on the bar's south face; finding 4, tier rhythm) | front, front_corner, right_side, rear |
| Ward: full-height X-braces | present, but with tier rhythm and black node artefacts (findings 3 and 4) | braced_frame, rear_north |
| Ward: ring beams | present; spacing deviates (finding 4) | right_side, rear_north |
| Ward: brick base at the east street | conforms (P2 frame overhang, finding 8) | right_side, rear |
| Atrium: diagonal mullion net | conforms on the south face (black nodes, finding 3) | glass_close, architecture_close |
| Atrium: roof | present as a dark glass roof with transverse members; it does not read as its own projecting volume (finding 5) | top, front |
| Entrance canopy: tension rods | conforms | entrance_canopy, front |
| Entrance canopy: posts | conforms | entrance_canopy, front |
| Entrance canopy: entrance doors | not expressed (finding 7) | entrance_canopy |
| Roof plant on the ward roof | conforms | roof_plant, top, rear_side |
| Materials hierarchy (red brick base, pale screen panels, light grey steel, blue-grey glass, dark louvres and sign) | conforms except the extra black corner element and black nodes (findings 2 and 3) | all |

## 4. Camera validity

- **Whole-envelope views.** front, front_corner, aerial, top, left_side, right_side, rear and rear_side are all valid: the target is unoccluded, unclipped and legible. The front render is a straight south elevation, whereas the source front is a three-quarter view from the south-south-east; the roles still match well enough to compare.
- **Detail views.** facade_close, architecture_close, glass_close, braced_frame, entrance_canopy, roof_canopy, roof_plant, brick_base and rear_north are all valid and legible.
- **interior.** This view is valid but marginal: it is underexposed, and the diagrid net cannot be read from inside (P2, finding 11).
- No camera produces a P0.

## 5. Previous-version findings

There are none. This is v001, the first build of this family, and the brief states there is no previous review. Nothing carries over to check in the pixels. Findings 1–6 above are the P1 baseline that v002 must clear.
