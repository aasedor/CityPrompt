# Independent holistic review: clay-toronto-streetcar-street v001 (RLASM v6.1 architectural clay)

Reviewer: independent; I did not build this. I read only the three locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg), all 18 renders in renders/ at full resolution, and the four phone boards. I made zoomed crops into a new scratch folder (`review-crops-streetcar-68982eb2`). I did not treat metadata, build reports or builder evidence as proof.

## 1. Verdict

**Verdict: VISUAL_REWORK_REQUIRED.** The street section, track slab, overhead line, markings and most of the street wall match the sources well. Four P1 defects still block approval: the streetcar's livery is wrong, its cab ends are boxy and vertical, the cross-street facade of the west Romanesque corner block is invented, and the front_corner camera clips the glass slab.

Counts: P0 = 0, P1 = 4, P2 = 8

Previous-version findings: none. This is v001, the first version, so there is no previous review to carry forward or close.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, streetcar_nose, track_slab, pantograph_wire, east_sidewalk, span_wire_pole | The streetcar side is red from the skirt up to the window sill. Only a thin white stripe sits under the windows and another over them. In the source front, the body below the windows is a wide white band over a narrow red skirt, so the car reads as red and white with white dominant on the sides. The render reads as an all-red car with pinstripes. | The livery band heights were swapped or mis-sized. The lower side panel uses the red skirt material, and the white band was built as a thin stripe instead of the full lower body panel. | On every module and both cab sides, set the stack (bottom to top) to: narrow red skirt (about 0.35 m), full white lower band up to the window sill, dark window band with black joint stripes, narrow white band, red roof band. Re-render front, streetcar_nose and track_slab. |
| 2 | P1 | streetcar_nose, front, track_slab, rear | Both cab ends are flat vertical boxes. A flush rectangular windscreen sits on a near-vertical face, the sides are only slightly chamfered, and there is a squared-off red cap. The source front shows the Flexity nose: a raked, rounded cab with a large windscreen wrapping toward the sides under a curved red roof cap. In the render the vehicle reads as a bus or a generic tram box, which weakens a named identity element ("sloped cab ends with large windscreens"). | The cab was built as a box with a chamfered plan only. There is no rake in section and no curvature at the roof cap. | Rebuild each cab end with a forward rake of about 10-15 deg from bumper to roof, round the roof-cap and side transitions, and enlarge the windscreen so it wraps slightly onto the side chamfers. Keep the amber destination sign at the head of the windscreen. Re-render streetcar_nose and front. |
| 3 | P1 | front_corner, aerial, left_side (against the oblique source) | The cross-street (south) facade of the west Romanesque corner block shows about 13 uniform bays of round-arched windows on both upper storeys, over a continuous stone-pier storefront arcade along the whole cross street. In the oblique source this facade has plain flat-headed sash windows grouped in pairs with an irregular rhythm. Its ground floor is mostly solid brick with a few doors and one shopfront near the corner. The arched windows and full storefronts belong only to the main-street facade (and the corner return). The visible grammar of the source is invented over the block's longest facade, in the matched oblique view. | The main-street facade module (arched bays plus storefront arcade) was mirrored or wrapped onto the cross-street elevation instead of authoring that elevation from the oblique source. | Keep the corbelled cornice turning the corner and the corner pier. Keep arched bays and storefronts on the main-street facade and the first one or two bays of the cross-street return. Rebuild the rest of the cross-street elevation with flat-headed paired sash windows (stone sills and lintels) and a mostly solid brick ground storey with a few doors and windows. Re-render front_corner, aerial and left_side. |
| 4 | P1 | front_corner | The camera cuts the ten-storey glass slab off at the top edge of the frame, so its green roof and penthouse are lost in the view matched to the oblique source, which shows them. The slab also reads as an endless tower here, so the height relationship between the brick wing and the slab cannot be checked in this role. (The slab is complete in aerial, rear and rear_side.) | The front_corner frame was tuned to the corner blocks without checking the tallest street-wall mass. | Pull back or raise the front_corner camera, or tilt it down slightly, so the whole slab, its green roof and its penthouse fit inside the frame with a margin. Keep the intersection and both corner blocks in view. |
| 5 | P2 | roof_skylights, front_corner, top | The two east-corner skylights are low curbs with almost flat glazing. The source shows clearly hipped glazed skylights (one elongated ridge, one pyramidal). | The hip pitch is too shallow. | Raise the glazing to a visible hip of about 30-35 deg and make one of the two elongated with a ridge. |
| 6 | P2 | victorian_arches | Small black slivers show at both ends of the gable coping, where it meets the main cornice cap. | The coping and the cornice cap do not quite meet (a coplanar gap or offset). | Extend or merge the coping ends into the cornice cap. |
| 7 | P2 | victorian_arches, left_side | The second-storey segmental heads and the third-storey round heads are too alike. At street distance both rows read as round arches. | The segmental rise is too high. | Lower the second-storey arch rise to about a quarter to a third of the opening width. |
| 8 | P2 | condo_balconies, rear, aerial | The east charcoal condo balconies are separate per-bay slabs between frame fins. They read as a near-continuous run, but not the continuous glass-railed balconies the brief describes. | Balconies were built per bay. | Join the balcony slabs and glass rails across each floor, passing in front of the fins. |
| 9 | P2 | front, intersection_crossing, east_sidewalk, span_wire_pole | The street trees are chunky double-icosphere crowns at second-to-third-storey height. They read as mature trees, not the young trees in the sources. | The tree scale and form are generic. | Shrink the crown and trunk height by about 30 percent and use a lighter single crown. |
| 10 | P2 | boards/phone-01 | The board pairs "Locked top" with "Render aerial" instead of the render top, so the plan comparison does not compare like roles. | Board layout. | Put renders/top.png beside the locked top. |
| 11 | P2 | renders/ (provenance) | The brief's detail list names facade_close, architecture_close and glass_close, but none of them exist. The brief's total ("18 views") matches the 18 files present, and their coverage comes from victorian_arches, corner_storefront and condo_balconies. | The brief lists generic view names next to family-specific ones. | Either render the three named views or correct the brief's list. |
| 12 | P2 | left_side, right_side | The side views look along the cross street at the corner blocks. The main-street section appears only in the distance, and a pale context block fills a third of left_side. | The side cameras are on the cross-street axis. | Optional: move the cameras so each one sees its main-street wall plus the cross-street return. |

## 3. Source conformance checklist

| Item | Status | View used |
|---|---|---|
| Section order: storefronts / sidewalk / brick strip / curb lane / track lane / yellow line / track lane / curb lane / strip / sidewalk | conforms | top (crop), front, track_slab |
| Section widths (about 25 m overall; west sidewalk about 3.9 m, east about 5.3 m; wide curb lanes) | conforms: measured about 4.0 m west / 5.0 m east / 4.4 m curb lanes / 3.6 m track lanes against about 25 m overall | top |
| Pale concrete track slab with transverse joints | conforms | track_slab, intersection_crossing, front |
| Twin embedded grooved-rail tracks, gauge and centres | conforms: about 1.5 m gauge, about 3.6 m centres, rails flush in the slab | top (crop), track_slab |
| Single yellow centre line between the tracks | conforms | track_slab, top |
| White lane dashes | conforms | front, top, streetcar_nose |
| Two-line crossings over both streets, and stop bars | conforms | top (crop), intersection_crossing |
| Yellow centre line on the cross street | conforms | top, left_side, right_side |
| Curb returns | conforms | top, intersection_crossing |
| Tall grey steel poles and span wires pole to pole | conforms | span_wire_pole, front, top |
| Hangers and insulators | conforms | span_wire_pole, front |
| Contact wire over each track | conforms | front, pantograph_wire |
| Long-armed cobra-head lights on the same poles | conforms | span_wire_pole, condo_balconies, intersection_crossing |
| Streetcar: five modules with black joint stripes | conforms | top, front |
| Streetcar livery bands | deviates (finding 1) | front, streetcar_nose |
| Streetcar cab ends (sloped, large windscreen) | deviates (finding 2) | streetcar_nose |
| Amber destination sign | conforms | streetcar_nose, rear |
| Doors | conforms (simple door panels with windows) | pantograph_wire, front |
| Wheels on the rails | conforms as massing: the skirt sits on the slab, centred on the east-track rails; bogies not shown | top, streetcar_nose |
| Northbound on the east track, mid-block | conforms | top, rear, front_corner |
| Pantograph raised to the wire | conforms: the collector bar meets the contact wire | pantograph_wire (crop) |
| Red TTC stop pole on the east corner | conforms | corner_storefront, intersection_crossing, front_corner |
| Tree pits and young trees in the brick strip | conforms in placement; the trees read mature (finding 9) | east_sidewalk, top |
| Bins | conforms | east_sidewalk, corner_storefront, top |
| Brick-paver furnishing strips and pale scored concrete sidewalks | conforms | east_sidewalk, front |
| West Romanesque corner block: round-arched third storey, segmental second storey | conforms on the main-street facade; the segmental/round distinction is weak (finding 7) | victorian_arches |
| West corner block: corbelled stone cornice turning the corner | conforms | front_corner, victorian_arches |
| West corner block: central gable with plaque | conforms (minor coping gap, finding 6) | victorian_arches, front_corner |
| West corner block: corner pier | conforms | front_corner |
| West corner block: cross-street elevation | deviates (finding 3) | front_corner, aerial, left_side |
| Plainer west block with white bracketed cornice | conforms | streetcar_nose, front_corner |
| Seven-storey west brick condo wing, glass-railed balconies on alternate bays | conforms (7 storeys counted) | rear_side (crop), front_corner, span_wire_pole |
| Ten-storey glass slab with floor bands, green roof and penthouse | conforms in aerial, rear and rear_side; clipped in front_corner (finding 4) | rear, aerial |
| East corner block with storefronts on both streets | conforms | corner_storefront, right_side, front_corner |
| East corner block skylights (two, glazed, hipped) | conforms in number and placement; the pitch is too flat (finding 5) | roof_skylights, top |
| Second east brick block: segmental windows and bracketed cornice | conforms | corner_storefront, aerial |
| Low two-storey east block with a dark roof | conforms | top, aerial |
| East six-storey charcoal-framed condo: balconies, green roof, set-back penthouse | conforms; the balconies are per-bay (finding 8) | aerial (crop), rear, condo_balconies |
| Storefront glazing at grade, with transoms, bulkheads and doors | conforms | corner_storefront, east_sidewalk |
| Roofs and parapets (brick parapets, flat roofs, rooftop units) | conforms | roof_skylights, front_corner |
| Context south of the cross street and beyond the back lanes (plainer massing) | conforms | aerial, left_side, right_side, rear_side |
| Pedestrians not modelled | conforms (correctly omitted) | all |
| Materials hierarchy (brick, cream stone trim, charcoal frame, blue-grey glass, pale concrete, red pavers, asphalt, green roofs) | conforms | all |

## 4. Camera validity

- **front_corner:** the glass slab's top, green roof and penthouse are cut off by the top of the frame (finding 4, P1). The primary street target is legible and not occluded.
- **left_side:** a pale context block fills about a third of the frame, and the main street appears only in the distance. The corner block is legible, so the view is valid (finding 12, P2).
- **right_side:** valid. The east corner block and the west street wall are legible.
- **front, aerial, top, rear, rear_side:** valid. The target is unoccluded and the whole street option is legible.
- **Detail views** (streetcar_nose, pantograph_wire, track_slab, span_wire_pole, intersection_crossing, corner_storefront, victorian_arches, condo_balconies, east_sidewalk, roof_skylights): all valid. In span_wire_pole and victorian_arches a foreground tree crown fills a corner but does not hide the target.
- The detail views facade_close, architecture_close and glass_close are named in the brief but not present (finding 11, P2).
