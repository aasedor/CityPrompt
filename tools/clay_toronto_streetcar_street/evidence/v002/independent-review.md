# Independent holistic review: Toronto streetcar main street, v002 (RLASM v6.1 architectural clay)

Reviewer: independent; judged only rendered pixels against the three locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders at full resolution, the three sources and the four phone boards, and made zoomed crops into a new folder, `indrev-crops-9663f762`, under the scratchpad.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** Three of the four v001 P1s are fixed in the pixels: the white-dominant livery, the west block's cross-street facade and the front_corner framing. The Flexity cab is only partly fixed. Its windscreen now wraps the corners and its plan corners are rounded, but the face is still vertical in profile and the red roof cap is still a flat-topped, square-shouldered panel. That leaves one P1 on the hero identity element.

Counts: P0 = 0, P1 = 1, P2 = 5

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | streetcar_nose, track_slab, front, east_sidewalk, front_corner | **Cab nose still reads as a vertical box (v001 finding 2 only partly fixed).** The windscreen shell now wraps about 0.3–0.4 m onto both sides, the plan corners are rounded (rear/top) and the light band, white apron and anti-climber are present. However, in the side profile (east_sidewalk, south cab) the cab end's silhouette runs dead vertical from the roof band to the skirt, with no visible rake. In streetcar_nose, track_slab and front the red cap above the windscreen is a flat vertical panel about 20% of the face height. Its top edge is straight and horizontal, it meets the flat grey roof at a sharp right angle, and its shoulders are square. In the source front (cab crop) the Flexity cap is a domed red hood whose upper corners round off strongly and sweep back over the roof, and the white side band curves forward into the cab. The claimed 11–13° rake and lofted cap with rounded shoulders do not show in any render. | The loft's rake offsets (0.48 m at 0.95 m, 0.18 m at 2.5 m) are too small to read, or they are applied below the cap, which is still a box. The cap is lofted in plan only, so it has no vertical curvature back over the roof. | Increase the visible rake so the windscreen top sits about 0.4–0.5 m behind the bumper line. Rebuild the red cap as a vertical-section loft: the front face curves back over the roof through a radius of about 0.4–0.5 m, and its top corners round off (r ≈ 0.4 m) into the side roof band. Re-render streetcar_nose, a true side profile and front, and confirm the sloped silhouette in the profile. |
| 2 | P2 | roof_skylights, aerial, front_corner, top | The east corner block's two skylights are small (about 3 m), low, near-flat glazed boxes. In the source oblique and top they are prominent hipped glazed lanterns, one elongated with a ridge and one pyramidal, with clear facet ridges. | The skylight pitch and size are under-scaled. | Raise the hips to about 30–35° with a visible ridge, and lengthen the western skylight to about 2:1. |
| 3 | P2 | front, condo_balconies, rear | The east charcoal condo's balconies read as separate per-bay trays between deep fins. The source front's near-left condo shows continuous horizontal balcony bands. | Fins project as far as the trays and break the row. | Pull the fins back behind the slab edge, or run one continuous slab edge and glass rail per floor. |
| 4 | P2 | east_sidewalk (south cab) | Where the windscreen shell wraps onto the side, it reads as a dark plate standing proud of the white side, with square exposed top and bottom ends. | The wrap shell is offset outward and not blended into the side. | Set the wrap flush with the side skin, or bevel its ends. |
| 5 | P2 | top, intersection_crossing, rear_side | The curb returns are plain concrete. The source corners carry curved brick-paver bands following the return. Separately, in rear_side the street and streetcar are mostly hidden behind the east condo. This is acceptable for a rear-side envelope view but weak. | The brick strip stops before the corner, and the camera is low behind the 6-storey box. | Continue the brick band around each return. Optionally raise the rear_side camera about 10 m. |

## 3. Source conformance checklist

Scale from the top render: building line to building line is 320 px, which is 25 m, so about 12.8 px/m.

| Item | Status | View(s) used / note |
|---|---|---|
| Section order: storefronts \| sidewalk \| brick strip \| curb lane \| track lane \| yellow line \| track lane \| curb lane \| strip \| sidewalk \| storefronts | conforms | top (pixel profile), rear, intersection_crossing |
| Widths | conforms | top: W sidewalk incl. strip ≈ 50 px ≈ 3.9 m; E sidewalk ≈ 68 px ≈ 5.3 m; curb lanes ≈ 50 px ≈ 3.9 m each; slab ≈ 99 px ≈ 7.7 m; brick strips about 1.0–1.3 m |
| Track slab, pale concrete with transverse joints | conforms | track_slab, intersection_crossing, rear |
| Twin grooved-rail tracks, gauge and centres | conforms | top: rails at 739.5/758.5 and 785.5/804.5 px, so gauge ≈ 19 px ≈ 1.48 m (1495 mm) and track centres ≈ 46 px ≈ 3.6 m; yellow line at 772 px is exactly centred. Grooves have light edges in track_slab |
| Single yellow centre line | conforms | track_slab, top, front |
| White lane dashes | conforms | front, streetcar_nose, top |
| Two-line crossings on both streets | conforms | top, intersection_crossing |
| Stop bars | conforms | top (main street spanning curb + track lane to the centre line; cross-street approaches), intersection_crossing |
| Cross-street yellow centre line | conforms | left_side, right_side, aerial |
| Curb returns | conforms (P2 #5: no brick band at the return) | top, intersection_crossing |
| Paired poles and span wires | conforms | top (3 span pairs), span_wire_pole, front |
| Hangers and insulators | conforms | pantograph_wire, front (hanger with white insulator), span_wire_pole |
| Contact wires over each track | conforms | pantograph_wire (two wires with hangers), front |
| Cobra-head lights on the poles | conforms | span_wire_pole, front, intersection_crossing |
| Streetcar: 5 modules | conforms | top (4 joints), front_corner |
| Streetcar livery bands | conforms (v001 #1 fixed) | front, streetcar_nose, east_sidewalk: red skirt, white band, dark window band, broad white band, narrow red roof band; white-dominant sides |
| Streetcar black joint stripes | conforms | front, east_sidewalk, pantograph_wire |
| Streetcar cab ends | deviates (P1 #1) | streetcar_nose, track_slab, east_sidewalk |
| Windscreen and amber destination sign | conforms | streetcar_nose, track_slab |
| Doors | conforms | front (red door leaves), pantograph_wire |
| Wheels on the rails | conforms | east_sidewalk (bogies under the skirt); top: car centred on the east track (796 vs 795 px), length ≈ 30.5 m, width ≈ 2.5 m |
| Pantograph raised and touching the wire | conforms | pantograph_wire, track_slab and front crops: the head bar meets the contact wire at the arm head; single-arm, on the centre module |
| Streetcar northbound on the east track, mid-block | conforms | top, front, aerial |
| TTC stop pole on the east corner | conforms | corner_storefront, front_corner, intersection_crossing |
| Tree pits and young trees | conforms | east_sidewalk (pit square), front; trees now smaller and lighter |
| Bins | conforms | east_sidewalk, corner_storefront, aerial |
| West Romanesque corner block: segmental 2nd-storey and round 3rd-storey arches | conforms | victorian_arches, front_corner |
| West Romanesque block: corbelled cornice turning the corner | conforms | front_corner, left_side, victorian_arches |
| West Romanesque block: central gable with plaque | conforms | victorian_arches, front_corner, right_side |
| West Romanesque block: corner pier | conforms | front_corner (stone corner pier at the shopfront) |
| West Romanesque block: cross-street side | conforms (v001 #3 fixed) | left_side, front_corner, aerial: 7 flat-headed paired sashes per upper storey at an irregular rhythm, stone sills and lintels; solid brick ground with doors and small sashes; one shopfront at the corner with a short sign-band return. Matches the oblique |
| Plainer west block with white bracketed cornice | conforms | front_corner, fc crop, front |
| West 7-storey brick condo wing, balconies on alternate bays | conforms | front_corner, span_wire_pole, rear |
| West 10-storey glass slab: floor bands, green roof, penthouse | conforms | front_corner (now fully in frame), rear, top |
| East corner block: storefronts on both streets | conforms | right_side, front_corner, corner_storefront |
| East corner block: two skylights | deviates (P2 #2: under-scaled, near-flat) | roof_skylights, aerial, top |
| Second east brick block: segmental windows, bracketed cornice | conforms | corner_storefront, east_sidewalk |
| East low 2-storey block with dark roof | conforms | top, rear_side |
| East 6-storey charcoal condo: balconies | deviates mildly (P2 #3) | front, condo_balconies, rear |
| East 6-storey charcoal condo: green roof and set-back penthouse | conforms | rear, aerial, top |
| Storefront glazing at grade throughout | conforms | corner_storefront, east_sidewalk, condo_balconies, front |
| Transoms, bulkheads and doors | conforms | corner_storefront |
| Openings with depth and returns | conforms | corner_storefront, victorian_arches |
| Roofs and parapets | conforms | roof_skylights, front_corner, aerial |
| Context south of the cross street and beyond the back lanes: plainer | conforms | intersection_crossing, left_side, right_side, rear_side |
| Materials hierarchy (brick, stone trim, pale slab, asphalt, brick strip, charcoal, glass) | conforms | all views |
| Plan versus top source | conforms | top: block sequence on both sides matches |
| Front matched role | conforms to the governing plan | The source front shows Victorian storefronts at near right where the plan (top source) places the brick condo wing. The sources conflict here, and the render follows the governing top view, so this is not counted as a defect |

## 4. Camera validity

- All 18 renders are present, legible and unclipped on their target. No view is invalid.
- **front_corner**, camera (34, -38, 50): the whole ten-storey glass slab, its green roof and its penthouse are inside the frame, along with both corner blocks and the intersection. v001 #4 is resolved.
- **rear_side**: the main street and streetcar are mostly hidden behind the east condo. It is still a valid rear-side envelope view (back faces, lane and party walls are legible); see P2 #5.
- **span_wire_pole**: a steep worm's-eye view, but the pole, span-wire insulator, cobra-head and contact wires are all legible.
- The brief's generic list names facade_close, architecture_close and glass_close. These files do not exist. The stated count of 18 views does match the files present, and corner_storefront, victorian_arches and condo_balconies cover those roles.
- The phone boards match the renders.

## 5. Previous-version (v001) findings: resolved in the pixels?

1. **Livery red-dominant: resolved.** In front, streetcar_nose, east_sidewalk, track_slab and pantograph_wire, every module reads red skirt, wide white band, dark window band, broad white band, then a narrow red roof band. The sides are now white-dominant. At the cab, a white frame closes the window band, so the white wraps round the windows.
2. **Flat vertical box cab ends: partially resolved, still P1 (finding #1).**
   - Fixed: the windscreen wraps the corners, the plan corners are rounded, and the light band, white apron, anti-climber and amber sign are present.
   - Still wrong: the face is still vertical in profile (east_sidewalk), and the red cap is still a square-shouldered flat panel with a sharp horizontal top edge (streetcar_nose, track_slab, front). The claimed rake and curved cap are not visible.
3. **West block cross-street side repeating the arcade: resolved.** left_side, front_corner and aerial show seven irregular paired flat-headed sashes per upper storey with stone sills and lintels. The ground storey is solid brick with two doors, a service door and three small sashes, plus one corner shopfront whose sign band returns only a short way. This matches the oblique. The main-street segmental and round arches, the arcade, the corbelled cornice and the gable are kept.
4. **front_corner clipping the slab: resolved.** The slab's top, green roof and penthouse are fully in frame.

Also taken (P2): the street trees are visibly smaller, with lighter crowns.

Earlier facts that still hold, all verified in the pixels:
- 1495 mm-gauge twin tracks on the pale slab, with one centred yellow line
- span-wire catenary on paired poles with contact wires
- the pantograph touching the wire
- the TTC stop pole
- the Romanesque segmental and round arches, corbelled cornice and gable
- the east corner block with storefronts on both streets and two skylights
- the brick condo wing and the charcoal condo with glass-railed balconies
