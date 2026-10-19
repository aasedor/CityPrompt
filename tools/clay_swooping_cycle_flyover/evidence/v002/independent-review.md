# Independent holistic review: elevated cycle flyover, v002 (RLASM v6.1 clay)

Reviewer: independent, adversarial. I judged only the rendered pixels (18 renders at 1440x1080, 4 phone boards) against the three locked sources (front.png, oblique.jpg, top.jpg). I did not use the builder's notes, metadata, counts or hashes as proof. Zoomed crops for this review are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/review-crops-v002-37554457/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: both v001 P0s and most v001 P1s are fixed in the pixels. The ribbon now lands at grade at both ends, and the columns are round, tapered Y-forks standing clear of the lanes. Three P1 finish and contact defects still block approval: the parapet's outer elevation is a plain slab, the column-arm-to-soffit junctions show hollow sockets, and the folded-sheet seams leak black notches and a sawtooth hem.

Counts: P0 = 0, P1 = 3, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | facade_close, y_column, street_under, architecture_close, glass_close, landing_ramp | The parapet and fascia show only a plain, featureless orange slab from the outside, from cap to soffit. It has no vertical bar rhythm and nothing separates the screen from the fascia. At street level it reads as a deep box girder (in street_under and facade_close the orange band is about 0.45 of the clear height under the deck; in source front it is about 0.35). The source's outer face is a dense vertical bar screen with a rounded top rail over a separate smooth fascia band that wraps the deck edge (source front, left curve; oblique, near parapet). | The slats were modelled only as a folded sheet on the inner face. The outer skin is one continuous extrusion running down over the fascia. | Carry the slat or bar relief (or a dense bar array) onto the outer face of the screen zone. Put a distinct smooth fascia band below it, about 0.4 to 0.5 m, set back or rounded, with a small reveal between screen and fascia. Reduce the total orange depth to about 0.35 of the clear height. |
| 2 | P1 | y_column (most visible), facade_close, street_under | Where each Y-arm meets the soffit there is a crisp dark lens-shaped ring: both the near and the far rim of the arm's top ellipse are visible from below. The arm reads as an open, cut tube poking into a socket rather than seated in the deck. The second arm ends in a visible light flat-disc rim. The source arms widen and blend smoothly into the soffit with no rim. | The arm cylinders are uncapped, or they end below or at a curved soffit edge, leaving a gap. There is no flared head or blend. | Cap each arm and extend it 0.2 to 0.3 m into the deck solid. Add a short flared head (cone or fillet) that is coincident with the soffit. Check that the arm tops sit fully inside the deck footprint and not at the fascia edge. Re-render y_column. |
| 3 | P1 | parapet_panel, front, deck_surface | parapet_panel shows a row of black triangular holes along the seam between the slim cap and the folded slat sheet. They are also legible on phone board 02. Where the folded sheet meets the deck, its lower edge is a serrated sawtooth hem (front near parapet; deck_surface near parapet foot). The curved cap shows chord facets. | The folded-sheet profile does not close against the cap and deck. The sheet's fold vertices stick out past, or fall short of, the cap underside and deck plane. The curve is too coarse. | Clip the folded sheet between two planes (the cap underside and the deck top) and close it with a continuous flat strip at top and bottom. Raise the curve subdivision on the cap and sheet, or shade them smooth. |
| 4 | P2 | top, aerial | The deck is still narrower than the source. In plan, deck/carriageway is about 0.29 (render) vs about 0.38 (source top), and about 1.2 to 1.45 lanes vs about 1.8. | The deck is set to 6.2 m against wide model lanes. | Widen it to about 7.5 to 8 m, or narrow the modelled lanes. |
| 5 | P2 | all orange views | The orange is still more amber and darker than the source: median hue about 27 to 28 degrees, value about 0.55, against about 19 degrees and 0.65 for the source front parapet. | Material base colour. | Shift the base toward a red-orange, roughly sRGB (200, 95, 45), and raise its value. |
| 6 | P2 | front (and ramp_curve) | The front composition is still mirrored against source front. The source has the deck on the right and the street below-left; the render has the deck on the left and the street on the right. | Camera placed on the wrong side of the S. | Mirror the camera across the ribbon tangent, or pick the matching bend. |
| 7 | P2 | glass_close, y_column, street_under | The column shafts and arms show visible polygon facets at close range, and the fork crotch is a hard crease. | Low radial segment count, flat shading. | Use 32 or more segments with smooth shading and a filleted crotch. |
| 8 | P2 | aerial, rear, top | The ribbon still reads as a thin band from far views. The parapets read as hairline edges in plan (about 2 to 4 px against a clearly visible orange rim in source top), and the ribbon fills a small part of the rear frame. | Narrow deck and thin cap in plan; rear framing. | Follows from #1 and #4; tighten the rear framing. |
| 9 | P2 | top | Soft dark smudges remain on the ground, for example near (905, 520) and (1150, 640). | Contact or AO shadows under the ribbon and trees with a low sample count. | Raise samples or bake the shadows, or clean up the ground shadow catcher. |
| 10 | P2 | front_corner, aerial, rear_north, street_under | A small black mark sits in the middle of each zebra crossing. | The centreline object z-fights or overlaps the zebra stripes. | Stop the centreline before the crossing, or lift the stripes. |
| 11 | P2 | front, aerial, ramp_curve | The context planting is still sparse: a flat green median strip with a few cube shrubs and isolated lollipop trees. The source has a lush planted median and dense street trees. | Minimal context set. | Add more low shrub masses in the median and more street trees on the footways, all clear of the deck. |
| 12 | P2 | front, ramp_curve, rear_side | Median column feet sit tight against the far kerb of a narrow median. From low angles the foot appears to touch the lane edge. They are in the median, not in a lane (confirmed in front_corner, rear_side and right_side crops). | The median is barely wider than the column foot. | Centre the feet in the median, or widen the median locally at each pier. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Plan and proportions | conforms (width deviates, P2) | top vs source top; aerial | Same one-wave-plus-S plan crossing the main street, with the north bulge over the north side-street junction. Deck is about 25% narrow relative to the street (#4). |
| Curve geometry | conforms | top, ramp_curve, left_side, right_side, rear_side | Smooth sinuous S-curves with no kinks. Ends run out on long straight approaches. No curl-over and no horn tips. |
| Deck and markings | conforms | deck_surface, top, glass_close | Dark surface with a white dashed centreline. No stripe banding. |
| Parapets | deviates (P1 #1, #3) | architecture_close, facade_close, parapet_panel, deck_surface vs source front and oblique | The inner face is now a dense, near-solid slatted orange screen (the v001 picket fence is gone). The outer face is a plain slab with no screen/fascia distinction, and the seams leak. |
| Y-columns | deviates (P1 #2) | y_column, architecture_close, front, ramp_curve | Round tapered shafts with a clear Y fork (best in architecture_close and front). The arm-to-soffit junctions show hollow socket rings, and the shafts are faceted. |
| Ramps and landings | conforms (not visible in sources; judged for coherence) | left_side, right_side, landing_ramp | Both ends descend gradually to at-grade kerbed cycle paths on the footways. The parapets run down with the deck and end in square caps at the foot. |
| Street beneath | conforms | street_under, top, rear_north, front_corner | Main street with lanes and a planted median, north-south side street with zebras. Clearance under the deck is legible. |
| Context | conforms (simplified; planting sparse, P2) | front, aerial, rear, rear_north | Brick blocks with window grids and pitched or flat roofs, low-poly trees. |
| Materials hierarchy | deviates (P1 #1; P2 #5) | front, architecture_close, street_under | Orange screen over grey concrete soffit and columns is right in principle. The orange is too amber and dark, and the screen/fascia layer is missing on the outer face. |

## 4. Camera validity

No view is invalid. All 18 views show the target legibly, and none is clipped so badly that its subject is lost.

- **rear:** the ribbon spans only about a third of the frame width and both ends disappear behind the north blocks. It is legible but weak (P2 #8).
- **rear_side:** a nearer block hides the middle of the ribbon. The east and west portions both read.
- **top:** the ribbon leaves the frame at both sides, so neither ramp foot shows. This matches the cropping of source top, and the ramps are covered by left_side, right_side and landing_ramp.
- **glass_close:** the name is a template role with no glass on this asset. The view shows the deck and the outer face of the parapet from just outside the ribbon, and it is legible.

## 5. Previous-version (v001) findings: resolved in the pixels?

| v001 finding | status in v002 pixels | evidence |
|---|---|---|
| P0: no view showed the deck reaching the ground (left_side far end a squared box at full height on Y-columns) | **Resolved** | left_side: the west ramp descends along the south footway to an at-grade path. right_side: the east ramp descends to grade on the north footway. Both have parapets with square end caps at the foot. |
| P0: landing_ramp missed its subject | **Resolved** | landing_ramp stands on the at-grade path with the ramp foot and the full rise up to the elevated ribbon in frame. No large empty foreground remains. |
| P1: deck about half the source width (about 0.6 lane vs 1.4) | **Largely resolved, downgraded to P2 #4** | Now about 1.2 to 1.45 lanes; deck/carriageway about 0.29 vs about 0.38 in the source. |
| P1: parapets an open picket fence with a chunky separate top rail | **Resolved on the inner face; new outer-face defect (P1 #1, #3)** | deck_surface and parapet_panel show a dense near-solid slatted screen with a slim cap. The outer face is a plain slab, and the folded-sheet seams leak. |
| P1: Y-columns in traffic lanes, one in a zebra crossing | **Resolved** | front_corner, rear_side, right_side and aerial crops show feet in the median or on the footways. None is on a crossing. Feet sit tight to the median kerb (P2 #12). |
| P1: Y-columns square boxes with arm blocks notching the shaft | **Resolved; new junction defect (P1 #2)** | architecture_close and y_column show round tapered shafts with a fork. The arm tops show socket rings at the soffit, and the shafts are faceted (P2 #7). |
| P1: other end curled over and dropped almost vertically within one deck width | **Resolved** | right_side and rear_side show a long, gentle descent with no fold-back. |
| P1: at the far end both parapets swept up into horn tips with no deck | **Resolved** | No horns in left_side, right_side or landing_ramp. The parapets end at the ramp foot with square caps and deck beneath. |
| P2: browner orange than the source's red-orange | **Not resolved (P2 #5)** | Hue about 27 to 28 degrees, value about 0.55, against about 19 degrees and 0.65. |
| P2: faceting on curved rail and fascia | **Not resolved (folded into P1 #3)** | The cap shows chord facets in glass_close and parapet_panel. |
| P2: mirrored front handedness | **Not resolved (P2 #6)** | front still mirrors source front. |
| P2: ribbon a thin band in front_corner, aerial, rear | **Partly resolved (P2 #8)** | Better in front_corner. Still thin in aerial and rear. |
| P2: ground-plane smudges in top | **Partly resolved (P2 #9)** | Softer, but dark patches remain. |
| P2: sparse context planting | **Partly resolved (P2 #11)** | Median shrub blocks were added; the scene is still sparse. |
| P2: stripe banding on the deck | **Resolved** | No banding in deck_surface or top. |
