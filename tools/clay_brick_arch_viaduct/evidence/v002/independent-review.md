# Independent holistic review: clay brick arch viaduct, v002

Reviewer: independent RLASM v6.1 holistic reviewer (not the builder).
I opened all three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`), all 18 renders at full resolution and all four phone boards, and made zoomed crops into a new folder (`scratchpad/review-crops-509531300/`). I judged rendered pixels only and did not use the builder's notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: all identity elements are now present and most v001 P1s are fixed in the pixels. Two P1s remain. The continuing run still ends in frame in the matched oblique and aerial views. The street trees were moved to the arcade pavement, which contradicts all three sources.

Counts: P0 = 0, P1 = 2, P2 = 16

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front_corner, aerial, cobbled_street (also front, rear_north at the horizon) | **The run still ends in frame.** In front_corner (top right, about x 1100–1140, y 120–135) and aerial (about x 1150–1190, y 135–150), the viaduct, both tracks, the parapets, the arcade pavement and the street all stop on one clean line, with empty grey beyond. In the oblique and top sources the run goes off the frame edge into a dense city. In cobbled_street the arcade stops at about x 520, well short of the vanishing point. A few trees, bollards and a black rail carry on, then the setts end in a straight ground edge against the sky (y ≈ 527). The hero street view therefore looks down a street that ends in a void. | The cut at about +80 m and the context ground's end were set past the *rear* cameras only. The high mirrored front_corner and aerial cameras, and the axial street camera, can still see past them. | Extend the run, tracks, street, pavements, terraces and ground until the cut is outside every frustum, and check each camera. Alternatively, frame front_corner and aerial so the run leaves the image edge, as in the oblique source, and close the street vista with a simple context massing block or a bend, not open ground. |
| 2 | P1 | front, front_corner, aerial, top, right_side, rear_side, pier_pilasters, cobbled_street, rear_north, parapet_coping | **The street trees are on the wrong side.** In the oblique and top sources, 2–4 trees stand in pits on the far, terrace-side pavement. The arcade pavement carries only planters, café tables and bollards, as the front source also shows. The render now has an even avenue of about 9–10 trees on the arcade kerb. It screens shopfront bays in front (a tree in front of the third arch), right_side (four trees across the arches), rear_side and pier_pilasters (a canopy fills the top-right third). This changes the street's landscape structure in every matched view. | The v001 canopy clash with the terrace was fixed by moving the trees across the street, instead of by sizing and placing them on the source pavement. | Put the trees back on the terrace-side pavement at source spacing (about 4 in the matched frame, irregular). Narrow the canopies or set them 1.5 m clear of the terrace face, widening that pavement if needed. Keep the arcade pavement clear of trees (planters, tables and bollards only). |
| 3 | P2 | front_corner, aerial, rear, rear_side, rear_north, front | The ground plane's corners and edges are still visible: front_corner (about 450,155), aerial (about 540,128), rear (about 520,268), rear_side (about 960,268). In front and rear_north the street meets a lighter band at the horizon. Beyond the two terraces, the "city" is an empty grey plane. | The ground plane is finite and there is no outer context ring. | Make the ground larger than every frustum, or add a low-detail ring of context massing. |
| 4 | P2 | track_ballast, front_corner, aerial | The ballast beds are smooth, pale grey trapezoids with sparse confetti chips, only on the near run. The sleepers sit visibly proud of the crest. The source ballast is a continuous warm grey-brown gravel mass. | Chips are scattered thinly over a smooth prism. | Warm and darken the bed tone toward the source. Raise the crib level to the sleeper tops. Add chips more densely, or use a stepped stone relief. |
| 5 | P2 | front_corner, aerial | On the near-end (abutment) face, the blind arch ring runs straight down to the plinth with no impost, so it reads as an architrave (the v001 imposts symptom, on this face only). The corner pier shows only short impost stubs. | The new impost course was applied to the arcade and garden faces but not to the end elevation. | Continue the impost course across the end face at the springing, and spring the blind ring from it. |
| 6 | P2 | facade_close, arch_shopfront, architecture_close | The arch rings are still visibly faceted at close range: polygon kinks on the extrados and intrados. | 24 segments is still too few at close-up distance. | Use 48 or more segments on rings in the detailed bays, or smooth shading. |
| 7 | P2 | architecture_close, front_corner | The pilaster face strips are thin slot-like strips, slightly off-centre on the pier and corner faces. They do not read as the stepped pilasters with stone caps in the front source. | Unchanged from v001. | Centre the strips and widen them to about 60% of the pier, with a stone band at each step. |
| 8 | P2 | architecture_close | A stray rectangular panel outline shows in each spandrel. | Leftover spandrel panel geometry. | Delete it, or make it a deliberate recessed panel. |
| 9 | P2 | front_corner, aerial, top, rear, rear_side, right_side | Both terraces are single long barns with one unbroken ridge and identical bays. There are no party-wall steps, rear wings or front gables, which the sources show. | Unchanged massing. | Break each terrace into house-width modules with party-wall upstands and rear outriggers. |
| 10 | P2 | aerial (right edge), rear_side (left), right_side (bottom) | The east terrace's rear wall is a blank, windowless tan slab. | No source shows this face, but it breaks the terrace grammar. | Add window and door openings to match the street face. |
| 11 | P2 | facade_close, arch_shopfront, pier_pilasters, glass_close | The shopfront fascia's ends run into the jambs and pass behind the impost blocks. The fascia top overlaps the impost underside. | Fascia width is unchanged and set to the reveal, not to the glazing frame. | Stop the fascia inside the reveal, below the impost soffit, with returned ends. |
| 12 | P2 | front | Only a thin red stripe of the train shows above the parapet. In the source front, the upper half of the cars shows. | Unchanged. | Lower the front camera's pitch slightly, or place the train on the street-side track in the front frame. |
| 13 | P2 | top, front_corner, aerial | The train runs on the arcade-side track; the top and oblique sources put it on the garden-side track. The livery is mostly white with red stripes; the sources show mostly red sides under a light roof. | Track choice and material proportions. | Move the consist to the garden-side track. Make the side red-dominant with a white window band. |
| 14 | P2 | cobbled_street (far), rear_north | Beyond the detailed run, the setts alias into longitudinal stripes that read as ribbing. | The sparse distant course lines plus sub-pixel joints. | Fade the joints to a flat sett tone with distance, rather than thinning the lines. |
| 15 | P2 | glass_close, arch_shopfront | The door leaf sits flush over the glazing grid with no transom or frame. It overlaps the mullion line. | The door is a flat panel placed in front of the glazing. | Frame the door into the mullion grid, with a transom at the head. |
| 16 | P2 | aerial, top, rear, left_side | A wide, empty lawn strip runs between the yard boundary wall and the viaduct. In the top source, the gardens and their trees run up to the viaduct parapet. | The yards were pulled back with the terrace, leaving dead ground. | Extend the yards or gardens to the viaduct face, or plant the strip. |
| 17 | P2 | right_side, rear_north | Composition: about 40% of right_side is dead foreground roof and blank wall. In rear_north, a foreground canopy covers the lower part of the nearest arch. The target stays legible in both. | Camera height and placement. | Raise or tilt right_side, and move rear_north's camera or that tree. |
| 18 | P2 | boards | The phone boards omit the aerial render and show top twice (boards 01 and 04). | Board layout list. | Put aerial in place of the duplicate top. |

## 3. Source conformance checklist

| item | status | view used | note |
|---|---|---|---|
| Plan and proportions | deviates | front_corner, aerial vs oblique; top vs top | The plan is a long straight run with the street, arcade pavement and terraces correctly placed. The run's end is visible in frame (P1 #1). There is a lawn strip on the garden side (P2 #16). |
| Arch count and rhythm | conforms | left_side, right_side, aerial | There is an even rhythm of semicircular arches on tall jambs. The piers are slightly slender against the source (pier/span about 0.25 against about 0.35); acceptable for clay. |
| Piers and pilasters | conforms (with P2) | pier_pilasters, architecture_close, left_side | The piers rise through the parapet as capped piers. The pilaster strips are thin and slot-like (P2 #7). |
| Imposts and arch rings | conforms on the arcade and garden faces; deviates on the end face | facade_close, arch_shopfront, pier_pilasters, left_side, front_corner | Stone imposts stand proud at the springing, with returns, and the ring springs from their tops. There is no impost on the near-end blind arch (P2 #5). The rings are faceted (P2 #6). |
| Shopfront infill (glazing, frames, signs) | conforms | facade_close, glass_close, arch_shopfront, front | The glazing is recessed with visible reveals, has timber mullions and transoms, a fascia band, doors and interior shelving. The first arch has a roller shutter, as in the oblique source. Fascia ends and door framing are P2 (#11, #15). |
| Parapet and coping | conforms | parapet_coping, train_cars, track_ballast | The coped parapet has capped piers at each pier. |
| Track deck (ballast, rails, sleepers) | conforms (with P2) | track_ballast, front_corner, aerial | There are two trapezoidal ballast beds with shoulders, a cess and a six-foot, sleepers and rails. The tracks dead-end at the near-end parapet, as in the oblique source. The bed finish is P2 (#4). |
| Train | conforms (with P2) | aerial, front_corner, rear, track_ballast, rear_north | There are 3 cars mid-run on the rails, a cab windscreen at each end and open track ahead. The track side and livery balance are P2 (#13). |
| Cobbled street and pavement | conforms (with P2) | cobbled_street, front, top | The setts are laid in staggered courses with gutter courses and kerbs. Both pavements are present, with bollards along the arcade kerb. The distant aliasing is P2 (#14). |
| Street trees / landscape | deviates | front_corner vs oblique; top vs top; front | The trees are on the arcade pavement, not the terrace-side pavement (P1 #2). |
| Context terraces | conforms (simplified, with P2) | aerial, top, cobbled_street, rear | There are two-storey terraces with slate roofs and chimney stacks. The west terrace has yards facing the viaduct. They are simplified as barns (P2 #9), and the east terrace's rear wall is blank (P2 #10). |
| Materials hierarchy | conforms | all | The materials read in order: red-brown brick body, pale stone imposts, coping and caps, dark slate, grey setts, pale paving, timber frames with dark glass, and a red-and-white train. The terrace brick is yellow-stock on the east and red on the west, close to the source mix. |

## 4. Camera validity

- No view is invalid, and in every view the target is unoccluded, unclipped and legible.
- **front_corner** and **aerial** are now on the street side and show the near cut end, the arcade, the pavement, the street and the far terrace, as in the oblique source. Both frames include the far cut end of the run (P1 #1).
- **top** is a perspective view on the street side. The run correctly leaves the top edge of the frame.
- **left_side** is clear: the foreground roof takes only the bottom 20% of the frame, and the whole garden elevation is visible.
- **right_side** is legible but about 40% dead foreground (P2 #17).
- **rear** and **rear_side** look toward the near end with the train mid-run and are legible.
- **rear_north** is legible; a foreground canopy covers the lower part of the nearest arch (P2 #17).
- **cobbled_street** is legible, but its vanishing point shows the street ending in a void (P1 #1).
- **pier_pilasters** is legible; a canopy fills the top-right third (P1 #2).
- All close-up views (facade_close, architecture_close, glass_close, arch_shopfront, track_ballast, parapet_coping, train_cars) are legible, with depth and contact readable.
- The phone boards omit aerial (P2 #18).

## 5. Previous-version (v001) findings, checked in the pixels

### v001 P1s

1. **Cobbled street read as a planked deck: resolved.** front and cobbled_street show staggered sett courses with cross joints and longitudinal gutter courses at each kerb. Distant aliasing remains as P2 #14.
2. **No ballast: resolved.** track_ballast shows raised trapezoidal beds with sloped shoulders, a cess and a six-foot, and the sleepers sit on the beds. The finish is P2 #4.
3. **Token impost cubes, ring not springing from them: resolved on the arcade and garden faces.** facade_close, arch_shopfront, pier_pilasters and left_side show a proud stone impost at the springing, returned into the reveal, with the ring rising from its top. The near-end blind arch still lacks an impost (P2 #5).
4. **Canopies cutting the terrace facades: resolved as a clash** (no canopy touches any facade). It was resolved by moving the trees to the arcade pavement, which creates new P1 #2.
5. **Train flush against the far parapet: resolved.** aerial, front_corner and rear show the train mid-run with open track ahead of both cabs, and track_ballast shows it sitting on the rails.
6. **Short closed box with blind ends and dead-ended tracks: partly resolved.** The run is now much longer, and the far end has no end wall. Only the near end has a blind wall, which matches the oblique source. However, the cut end, with the tracks, street and ground stopping in a void, is visible in front_corner, aerial and cobbled_street (P1 #1).
7. **front_corner and top on the lawn side, and phone-01 pairing: resolved.** Both cameras are on the street side, and phone-01 pairs the locked top with the render top.
8. **left_side occluded by the terrace roof: resolved.** The whole garden elevation is visible.

### v001 P2s

- **Faceted arch rings:** improved, but still visible at close range (P2 #6).
- **Off-centre or truncated pilaster strips:** still present (P2 #7).
- **Stray spandrel panel outline:** still present (P2 #8).
- **North terrace facing the viaduct front-on with no yards:** resolved. aerial, top and rear show rear yards with low walls and a boundary wall.
- **Barn-like terraces with unbroken ridges:** still present (P2 #9).
- **Visible ground edge:** not resolved; still visible in front_corner, aerial, rear, rear_side, front and rear_north (P2 #3; related to P1 #1).
- **right_side occlusion by roofs:** resolved; the arcade is fully visible. A composition P2 remains (#17).
- **Fascia ends running into the jambs:** still present (P2 #11).
- **Only a thin stripe of train showing in front:** still present (P2 #12).
