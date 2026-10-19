# Independent holistic review: clay-plateau-stair-triplex v003 (RLASM v6.1 architectural clay)

Reviewer: independent (did not build). Evidence used: rendered pixels in `renders/*.png` (all 18 opened at full resolution), the three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`) and the four phone boards. Zoomed crops were written only to a new folder, `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/ireview-v003-crops-7f3a/`. The builder's notes, metadata and evidence JSON were not treated as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: every identity element is present and three of the six v002 findings are fixed in the pixels, but the façade plan is flat where all three sources show side bays breaking forward of a recessed centre, the south-east cornice return and the consoles still read as stacked blocks, and new pure-black voids appear at the canopy fascia ends and at grade.

Counts: P0 = 0, P1 = 5, P2 = 11

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top, front_corner, aerial, front (vs sources top, oblique, front) | The street façade is a single flat plane. The cornice and attic run in one straight line across the full width (top: one straight cornice edge; front_corner/aerial: no break). In all three sources the two side bays project a short distance forward of a recessed centre. The cornice breaks back over the centre with angled (chamfered) returns, and the raised crest sits on the recessed centre; the front source even shows the right bay's west return face. | The plan was modelled as a rectangle with only the porch recessed, so the side-bay projection was left out of the front line. | Push the two side bays (quoined piers, windows and cornice) forward about 0.4–0.6 m, or set the centre back by the same amount. Return the cornice, frieze and side parapets around each bay end with the angled transition seen in sources top and oblique. Keep the attic and canopy on the recessed centre. Re-render top, front_corner, aerial and front. |
| 2 | P1 | right_side, architecture_close | **v002 finding 1 is not resolved.** Seen from the east, the south-east cornice return is still a stack: corona slab, two modillion cubes, then a heavy lower slab that projects almost as far as the corona, then a separate small block above the quoins. Between the soffit and the lower slab there is a near-black slot: pixels measure about RGB 32–40 at the corner in architecture_close, against about 111 for the same soffit shadow mid-run. | The bed/frieze band is a separate box that projects too far and does not meet the corona soffit at the return, leaving a cavity at the corner. | Make the corona, bed moulding and frieze one continuous stepped profile and mitre it around the corner. Pull the frieze projection back to about 1/3 of the corona projection and close the soffit-to-frieze gap so no near-black pixels remain at the return. Re-check right_side, architecture_close and front. |
| 3 | P1 | architecture_close, facade_close, glass_close, front | **v002 finding 4 is only partly resolved.** Each porch-pier console still reads as a pile of two or three cubes: a large block, a set-back block and a small cube below with a dark shadow line above it, so the bottom cube looks hung on. In architecture_close the middle block runs into the end of the right-bay window lintel, so the console is not clear of the window head in that view. | The console was built from stacked boxes instead of one shaped profile, and its width ignores the lintel end. | Model each console as a single extruded side profile (a tapered or scrolled bracket) that is one piece from the frieze down. Narrow it or move it inboard so there is a visible gap of at least about 5 cm to the lintel end. |
| 4 | P1 | cornice_parapet, aerial, top | Both ends of the canopy front fascia show a pure-black square opening (RGB 0–1 in cornice_parapet at about x128,y766). The same black dots appear at both canopy corners in aerial and as two black dots in top. This is the same class of defect as v002 finding 2: an open, unclosed end. | The fascia or gutter member is an open channel or uncapped box, and its ends are not closed against the cornice or pier. | Cap both fascia ends with end faces, or run the fascia into the pier and cornice faces. Re-render cornice_parapet, aerial and top and confirm there are no pure-black pixels at the canopy ends. |
| 5 | P1 | iron_stair, front | A pure-black horizontal slot (RGB 0,0,0, about 45×20 px in iron_stair at x665–710, y868–890) sits at grade under the west quoined pier, where the plex meets the neighbour. It reads as the wall lifted off the ground or as an opening with no back. It is also visible through the fence in front (about x470–505, y880–890). | Either the plinth or base course stops short of grade there, or a basement-window cut has no reveal or back face. | Run the plinth down to finished grade along the full front. If a basement window is intended there, give it a frame, glazing, reveal returns and a back face like the other basement windows. |
| 6 | P2 | architecture_close, front_corner, cornice_parapet | The side-bay parapets are plain low planks set back on the cornice and stop short of the south-east corner, with a block at the end. In the sources the side bays carry ornamental frieze or scroll panels and run to the corner. | Simplified parapet runs. | Run the side parapets to the bay ends and add a simple relief panel face on each (clay level). |
| 7 | P2 | aerial, rear_side, left_side | From above and behind, the raised attic reads as a deep box sitting on the roof rather than a thin parapet panel. | The attic is modelled at full cornice depth. | Reduce the attic to a parapet thickness of about 0.3–0.4 m behind its face and cap. |
| 8 | P2 | architecture_close, right_side | A visible vertical butt seam splits the corona and its cap at the south-east corner. | The corona is made of two boxes. | Merge them into one corona piece, or mitre it at the corner. |
| 9 | P2 | facade_close, balcony_canopy, front | Diagonal knee braces from the lattice columns to the canopy do not appear in any source. In balcony_canopy the west brace's top end shows in front of, or through, the canopy fascia face. | Added structural braces. | Remove the braces, or end them on the canopy soffit inboard of the fascia. |
| 10 | P2 | interior | A small pure-black notch (RGB 0) sits where the porch-box wall meets the floor (about x325–340, y830–840). Separate floor plates overlap each other, leaving a visible step and seam along the walls. | A wall stops short of the floor slab; there are duplicate floor plates. | Extend the porch-box wall to the slab and merge the floor plates into one level slab. |
| 11 | P2 | rear, rear_north, left_side | Rear windows and doors are glazed in an opaque brown and read as panels or shutters, while the glazing on other faces is grey. The rear wall shows none of the brick coursing seen on the east wall. | A different glass material and no coursing on the north wall. | Use the same glass material and the same brick coursing as the east wall. |
| 12 | P2 | roof_skylights, top, aerial | The roof-hatch lid is black and reads as a hole in top. The source hatch is a pale box with a ladder. | Iron material applied to the lid. | Give the lid the pale roof or flashing colour and keep the ladder black. |
| 13 | P2 | front_corner, aerial, top | The front yard is mostly paved, with two small lawn rectangles. The sources show lawn filling the yard behind the fence. | Ground patches are undersized. | Enlarge the lawn to fill the yard outside the steps, stair foot and walk. |
| 14 | P2 | iron_stair, front | The handrails and stringers show dark notches at every segment joint (faceted polyline). | Segmented sweep with gaps. | Weld the segments, or sweep one continuous rail. |
| 15 | P2 | rear_side | A foreground street tree hides most of the rear balconies and the north-east corner. Rear and rear_north cover that face, so this is a polish issue rather than a validity issue. | Camera placement. | Move the camera or the tree so the rear-east corner is clear. |
| 16 | P2 | front, front_corner, glass_close | The front limestone is very pale and close in value to the grey brick side walls. The source contrast between warmer limestone ashlar and the smaller-coursed side brick is weak. | Palette values are too close together. | Shift the front stone slightly warmer or darker and keep the side brick a distinct cooler grey. |

(The severity counts are taken from this table: 5 rows are P1, 11 rows are P2 and no row is P0.)

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette | deviates: overall flat-roofed corner plex is right, but the front plane is flat with no side-bay projection or cornice break (finding 1) | top, front_corner, aerial vs all sources |
| Storey count and basement | conforms: two storeys over a half-basement with small basement windows at grade | front, right_side, iron_stair |
| Limestone coursing and quoins | conforms: block coursing lines on the front; long-and-short quoins at both front corners and the south-east return. Palette is pale (P2 #16) | glass_close, front, right_side |
| Porch recess (both floors) | conforms: deep recess on both floors, with walls running to the soffit and no black band | facade_close, balcony_canopy, front_corner |
| Doors (colours) | conforms: a pair of red glazed doors upstairs and a green door at the ground porch | facade_close, balcony_canopy, interior |
| Balcony and railing | conforms: projecting stone balcony slab with an iron picket railing | front_corner, balcony_canopy |
| Canopy and lattice columns | conforms with polish issues: flat canopy on two black lattice columns. It adds knee braces (P2 #9) and has open fascia ends (P1 #4) | facade_close, balcony_canopy, cornice_parapet |
| Windows (frames, transoms, sills, lintels) | conforms: wide timber frames with transom lights, stone sills and stone lintels, with visible reveals and interior depth | glass_close, front, east_side |
| Iron stair (flight, curl, rails, newel) | conforms: one flight from the west yard to the balcony's west end, curling at its foot around a capped newel, with inner and outer rails. Rail joints are notched (P2 #14) | iron_stair, front, top |
| Cornice, consoles and raised parapet | deviates: bracketed cornice and flush raised attic with cartouche are present, but the cornice is straight (P1 #1), the south-east return is stacked with a dark slot (P1 #2) and the consoles are cube piles (P1 #3) | architecture_close, cornice_parapet, right_side, front |
| Side walls and windows | conforms: plain grey brick coursing on the east wall with narrow windows, stone sills and lintels, and basement windows | east_side, right_side |
| Roof (membrane, skylights, hatch) | conforms with polish issue: pale membrane, three skylights in a row and a hatch with a ladder; hatch lid is black (P2 #12) | roof_skylights, top, aerial |
| Yard | conforms with polish issue: front yard is present but under-grassed (P2 #13) | front_corner, top |
| Lawn | deviates slightly: small lawn patches only (P2 #13) | top, aerial |
| Fence | conforms: black iron fence along the sidewalk, turning at the east corner | front, front_corner, top |
| Sidewalks | conforms: south sidewalk and east side-street sidewalk with a road | top, aerial |
| Neighbour | conforms: attached brick neighbour to the west, the full depth of the plex | top, front, left_side |
| Materials hierarchy | conforms, weakly: stone front over grey brick sides with black iron, timber frames, red and green doors. Front and side values are close (P2 #16) | front, front_corner |
| North face (not shown by any source; judged for coherence only) | coherent: centred rear doors on two floors with timber balconies on iron posts and plain narrow windows. Glazing material differs (P2 #11) | rear, rear_north, left_side |

## 4. Camera validity

- All 18 views frame a legible target. None is clipped so far that the asset cannot be judged, and none is occluded in a way that invalidates it.
- top: now tight on the plex, which fills about 85% of the frame height. The neighbour and side street are included only because of the aspect ratio. Valid.
- rear_side: a foreground tree hides most of the rear balconies (P2 #15). The face is covered by rear and rear_north, so the view is still valid.
- left_side: the west wall is a party wall and cannot be seen. This view actually shows the north face and roof from the north-west, which is valid as a coherence view.
- front: the fence in the foreground partly hides the basement windows. Acceptable.

## 5. Previous-version (v002) findings: verified in pixels

| v002 finding | builder claim | status in v003 pixels |
|---|---|---|
| 1. South-east cornice return built as stacked slabs with black slits | one continuous cornice whose east return starts behind each front band | **Not resolved.** right_side still shows corona, modillion cubes, a heavy lower slab and a small block as a stack. architecture_close shows a near-black slot (RGB about 32–40) between the soffit and the frieze at the corner (now P1 #2). |
| 2. Open black hole at the east end of the raised central cornice | flush attic panel with closed ends | **Resolved** at the attic: both attic ends are closed in architecture_close, cornice_parapet and aerial. A new black hole of the same class now appears at both canopy fascia ends (P1 #4). |
| 3. Raised parapet reading as a plank set back behind the corona, with a loose cartouche | flush stone attic panel on the cornice with a cap and the cartouche on its face | **Resolved** for the central attic: the panel is flush with the cornice face, capped, and the cartouche sits as relief on its face (front, cornice_parapet, front_corner). The side-bay parapets remain plain set-back planks (P2 #6). |
| 4. Consoles reading as cube piles hanging onto the window heads | one shaped console each side, clear of the window heads | **Partly resolved.** There is now one console each side, clear of the head in facade_close. It still reads as two or three stacked cubes with a hung lower cube, and in architecture_close it runs into the right-bay lintel end (P1 #3). |
| 5. Top view framed too wide | tight top view on the plex | **Resolved.** The plex fills the frame height and the plan is legible. |
| 6. Porch walls stopping short of the ceiling, leaving a black band and slots | porch walls up to the roof deck and floors run into the walls | **Resolved** on the exterior porch: walls meet the soffit with no band or slots (facade_close, balcony_canopy, front_corner). Inside the unit a small black notch remains at the base of the porch box, with overlapping floor plates (P2 #10). |
