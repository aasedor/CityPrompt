# Independent holistic review: clay-amsterdam-canal-warehouse v002 (RLASM v6.1)

Reviewer: independent, adversarial. Evidence used: only the pixels of `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`, all 18 `renders/*.png` (each opened at full resolution) and the four `boards/*.png`. I did not use any builder metadata, counts, hashes or notes as proof. I wrote my zoomed crops to a separate scratch folder (`indrev-canalwh-v002-crops`) and did not touch any candidate file.

## 1. Verdict

**Verdict: VISUAL_REWORK_REQUIRED.** The quay elevation now matches the source well, and seven of the nine v001 findings are fixed in the pixels. Four P1 defects remain:
- the long east wall has an extra fourth row of attic windows that no source shows;
- every street door stands on a plinth band that runs across its opening;
- the two canals are joined into one L of water, which contradicts the top view;
- the hip plate behind the gables shows as a warped sheet lifted off the roof.

Counts: P0 = 0, P1 = 4, P2 = 13

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, front_corner, aerial, right_side, east_side, architecture_close, rear, rear_north, rear_side | **Extra row of attic windows on the side walls.** The long east wall has four rows of openings: a row of 7 small segmental attic windows tight under the white cornice, two rows of segmental windows, then the arched ground row. In `sources/front.png` and `sources/oblique.jpg` the east wall has only two upper rows of tall, narrow segmental windows over the arched ground row. Between the top row and the eave there is blank brick with iron anchors. The extra row adds a storey's worth of openings and changes the side-wall rhythm. The north face repeats it. | The builder applied the storey generator to all four floors of the long walls. The top floor actually sits in the gable/roof zone, where the east wall has no windows, only anchors and the dormer. | Remove the attic window row from the east and north walls. Keep the anchor row in that band. Re-render front, front_corner, right_side and east_side. |
| 2 | P1 | arched_doors, front_corner, aerial, right_side (east side door) | **Doors stop short of the paving.** The grey stone plinth (about 0.5 m) runs straight across the bottom of both quay cart doors and the east side door. The timber leaves stop at the top of the plinth, and the wheel-guard blocks stand in front of a solid sill. In both sources the cart-door leaves run down to the paving: the plinth stops at the jambs and the stone wheel guards flank the opening. As modelled, the doors cannot open onto the quay, which is an opening/contact defect on an identity element. | The plinth was built as one continuous band along the facade base, and no opening was cut through it. | Interrupt the plinth at every door opening, both cart doors and the east side door. Extend the leaves and reveals down to the paving level and keep the wheel guards at the jambs. |
| 3 | P1 | top, aerial, front_corner, front, rear_side | **The two canals are joined around the corner.** The south quay canal and the east canal form one continuous L of water wrapping the street corner, with a continuous L parapet. The street simply ends at the water. In `sources/top.jpg` (which governs the plan) the south canal ends at about the line of the east wall in a curved parapet. The street and quay paving continue south across the corner, and the east canal begins north of that paved corner. `sources/front.png` shows the same thing: cobbled street in the right foreground, where the render front shows water. | The site plate was modelled as one L-shaped water body instead of two separate canals with a paved corner. | Split the water into the south canal, ending in a curved parapet at the street line, and the east canal, starting north of a paved corner. Pave the corner and continue the street south. Re-check front and top. |
| 4 | P1 | gable_tops, roof_deck, (aerial) | **The hip plate reads as a warped sheet, not a roof plane.** The triangular plate between the gables sits above the inner slopes. It shows a smooth-shading dark blotch across what should be a flat triangle, a dark lip with a shadow gap along both valley edges, and in roof_deck a curved right edge. Its lower tip overhangs a flat tan (85,78,70) strip in the valley. The v001 "dark cracks" have turned into visible step lines and a floating lip rather than a clean valley. | The plate was offset proud to avoid z-fighting. The quad is non-planar or smooth-shaded, and the valley gutter is a separate tan box. | Rebuild the hip plate as a planar, flat-shaded triangle that meets both inner slopes exactly (shared edges, no offset). Give the valley a slate-coloured lead gutter, or make it coplanar. Re-render gable_tops and roof_deck. |
| 5 | P2 | architecture_close | Around the top east loading door, the brick joint lines stop at a rectangular panel edge (vertical seam beside the door, horizontal seam above). The rest of the gable field is plain, so the "gable panel" reads as a patch. | A separate panel mesh with its own joint mapping. | Merge the panel into the gable wall or continue the joint courses across it. |
| 6 | P2 | facade_close, front | The middle east loading door's upper glass shows a broad grey horizontal band across both panes. It looks like a reflected horizon or a slab edge and reads as a smear. | Environment reflection or interior slab edge seen through the glass. | Lower the glass reflectivity, or set the interior slab so it does not show through the door. |
| 7 | P2 | arched_doors, front_corner | The cart doors are plain board leaves. The source doors are two-leaf, with a glazed fanlight in the arch head. | Simplified door assembly. | Add the two-leaf division and a glazed arch-head transom. |
| 8 | P2 | facade_close, loading_doors | The shutters have two ledges and a vertical batten. The source shutters are ledged-and-braced (Z/diagonal brace). | Simplified shutter. | Add the diagonal brace. |
| 9 | P2 | front, architecture_close, gable_tops | The hoist beams are brown timber with a white slab on top. In the source they read as light stone/white-painted projecting hoods. | Material choice. | Use the light coping colour for the hoist hood and beam. |
| 10 | P2 | top, aerial, roof_deck | The deck vents are square boxes with dark caps. The source has round, cylindrical vents. | Box primitive. | Replace them with short cylinders. |
| 11 | P2 | top, aerial, right_side | The dormer sits mid-slope on the east roof. In the source top and oblique it sits low, near the east eave. | Placement. | Move the dormer down towards the eave. |
| 12 | P2 | front, aerial, gable_tops | Chimneys are placed differently from the source. The source shows a stack between the gables on the west roof near the valley (front) and one on the deck's front edge at the top of the hip area (oblique and top). The render puts a stack just behind the west pinnacle and one at the deck's north-west corner. | Placement. | Move the stacks to the source positions. |
| 13 | P2 | top, aerial | The deck runs ridge to ridge. In the source top the west section's inner slope stays tiled for the full depth beside the deck. | Simplified roof. | Narrow the deck so the west inner slope shows. |
| 14 | P2 | front, front_corner, aerial, rear, left_side | The neighbour is a pale beige plain box with dark rectangles. The source neighbour is a red-brown brick canal house with a white-trimmed neck gable. | Placeholder massing. | Use a brick colour and add a neck-gable outline. |
| 15 | P2 | all roofs | Every roof is uniform slate grey. In the source the west roof and the hip area between the gables are brown/terracotta tiles; the east roof is darker slate. | One roof material. | Give the west roof and the hip area a brown tile colour. |
| 16 | P2 | right_side, east_side, front | The east wall has 7 bays per row. The sources show roughly 5–6, with taller, narrower openings (about 1:2.5). | Bay count and proportions. | Reduce to 6 bays and stretch the window height. |
| 17 | P2 | front_corner, front, left_side, right_side, rear, rear_side | Camera matching is approximate. front_corner sits further east than the source oblique, so the east wall gets about twice its share of the frame. front is taken from water level, not the street. The four side/rear envelope views frame the building at roughly 25% of the image width. | Camera presets. | Swing front_corner azimuth towards the quay normal, and tighten the side and rear framings. |

(The brick joints are horizontal lines only, with no head joints. That is accepted for clay and not listed separately.)

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette (two parallel gabled sections on the quay, corner block with long east wall) | conforms | front, front_corner, aerial vs front/oblique |
| Storey count and proportions: four storeys on the quay (ground + three loading-door levels, the top one straddling the eave in the gable) | conforms | front, facade_close vs front/oblique |
| Two sections, widths: west narrower (about 0.90 of east in the render top; about 0.89 in the source top) | conforms | top vs top |
| Two sections, heights: west lower, same pitch | conforms | front, front_corner |
| Storey rhythm on the east wall | **deviates** (extra attic row, finding 1) | right_side, east_side vs front/oblique |
| Brick colour and joints | conforms for clay (red-brown; horizontal joints only, P2-level) | facade_close, glass_close |
| Gable copings (light stone) | conforms | front_upper crop, architecture_close |
| Shoulder piers at the gable feet | conforms | front, architecture_close |
| Pinnacles at the peaks | conforms | front, aerial |
| Hoist beams below the peaks | conforms in position; material deviates (P2) | front, architecture_close |
| Green glazed loading doors, three stacked per section with lower board panels | conforms | facade_close, loading_doors |
| Green board shutters folded flat on the wall | conforms (no Z-brace, P2) | loading_doors |
| Cart doors: round arches, stone springers, keystone, wheel guards | conforms | arched_doors |
| Cart doors: contact with paving | **deviates** (plinth across the opening, finding 2) | arched_doors, front_corner |
| Flanking windows: segmental arches, dark frames, stone sills, two upper rows plus ground, none on the gable floor | conforms | facade_close, glass_close |
| Iron wall anchors | conforms | facade_close, east_side, rear_north |
| East wall windows: tall arched ground windows and a door | conforms | right_side, east_side |
| East wall upper windows | **deviates** (extra attic row; 7 bays vs about 5–6, finding 1 and #16) | right_side |
| White timber cornice under the east eave | conforms | east_side, architecture_close |
| Roofs: two gables with a valley | conforms in form; the valley/hip plate finish deviates (finding 4) | gable_tops, roof_deck |
| Roofs: flat deck with vents | conforms in form; vents square, not round (P2) | aerial, roof_deck, top |
| Roofs: dormer on the east slope | conforms (placed mid-slope, P2) | aerial, top |
| Roofs: brick chimneys | conforms in presence; positions differ (P2) | aerial, top |
| Quay: brick-paved, about 3–3.5 m deep | conforms | top, front_corner |
| Side street about 4 m | conforms (about 3.6 m) | top |
| Low brick parapet with coping to the quay canal | conforms along the quay | front, front_corner |
| Canals: south canal and second canal beyond the street | **deviates**: the two are joined around the corner (finding 3) | top vs top |
| Tree and lamp on the quay at the west | conforms | front, aerial |
| Attached gabled canal house to the west | conforms in massing; colour and gable type deviate (P2) | front, aerial |
| Materials hierarchy (brick body, stone trim, green joinery, timber cart doors, dark roofs) | conforms | front, facade_close |
| North face (not in any source; checked for coherence only) | coherent: arches, sills, anchors and joints are present; it repeats the attic row of finding 1 | rear, rear_north |

## 4. Camera validity

- No view has an invalid camera: in every render the target is legible, and no envelope view clips the asset.
- **front:** the camera sits at canal level, so the quay parapet hides the facade base and the plinth. The building itself is fully legible. This is acceptable, but it does not match the source, which is taken from street level on the paved corner.
- **left_side:** the attached neighbour occludes most of the west face. That face is a party wall, so this is expected and the view stays legible.
- **left_side, right_side, rear, rear_side:** the building fills only about 25% of the frame width. They are legible but loose (P2, finding 17).
- **rear_north:** a deliberate close view of the north face. Clipping the top of the gable is acceptable for a detail view.
- **arched_doors:** now correctly centred on the east cart door.
- **interior:** shows a coherent storey with the loading door and arched windows in depth.

## 5. Previous-version (v001) findings: are they resolved in the pixels?

| v001 finding | status in v002 pixels |
|---|---|
| Quay gables composed differently: flanking windows on all three upper floors, eave above the top loading door, extra blank gable | **Resolved.** There are no flanking windows on the gable floor. The top loading doors straddle the eave line (front_corner: door head about 60 px above the shoulder). Only two quay gables exist. |
| West section too narrow | **Resolved.** Top view gives about 166 px vs 184 px (about 0.90), matching the source top at about 0.89. |
| Quay and side street too deep | **Resolved.** At top-view scale the quay is about 3.4 m and the street about 3.6 m, against about 3 m and about 4 m in the source. |
| Black line and post at the canal joint; grey streaks on the east canal | **Resolved** as artefacts: the parapet corner is clean and the water plain. However, the canal layout itself is wrong (new P1, finding 3). |
| Dark cracks along the valley roof planes; chimney cut by a roof plane | **Partly resolved.** The deck chimney now stands cleanly on the deck. The valley still shows dark step lines along the lifted hip plate, a shading blotch and a floating lip over a tan strip (P1, finding 4). |
| North face without arches, sills, anchors or joints | **Resolved.** rear_north shows segmental arches, sills, anchors, joint courses and an arched door. It inherits the attic row of finding 1. |
| Glass artefacts on the loading doors | **Largely resolved.** Solid lower panels are present and the glazing shows interior depth. A residual horizontal reflection band remains on the middle east loading door (P2, finding 6). |
| arched_doors camera missing the cart doors | **Resolved.** The east cart door is centred and fully framed. That framing is what exposes the plinth defect (finding 2). |
| front_corner and aerial framed too wide | **Resolved.** The building fills about 56–60% of the frame width, comparable to the source oblique. The azimuth is still more easterly than the source (P2, finding 17). |
