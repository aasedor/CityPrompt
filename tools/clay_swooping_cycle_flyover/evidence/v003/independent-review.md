# Independent holistic review — clay swooping cycle flyover, v003 (RLASM v6.1)

Reviewer: independent; judged only rendered pixels against the three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). All 18 renders were opened at full resolution and the four phone boards were checked. Zoomed crops (2x–5x) were written only to the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/flyover-v003-review-crops-f9548bdf/`. Pixel coordinates below are in the 1440x1080 render frame.

## 1. Verdict

**PASS_ZERO_P0_P1** — In the pixels, all three v002 P1s are fixed and every v001 fix still holds. The sinuous orange-parapeted ribbon on round forked Y-columns swooping in S-curves over the boulevard reads correctly in every view. What remains is polish: deck width, orange value and saturation, rail tessellation at the tightest bend, fork crease, context and camera framing.

Counts: P0 = 0, P1 = 0, P2 = 12

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | top, aerial, left_side, right_side, rear_side | The deck is still narrow. In top, the ribbon at its trough measures about 45–48 px outer to outer across a 164 px boulevard (ratio about 0.29). In the source top it measures about 64 px across a 165 px road (about 0.39), so the deck is about 25% narrower than the source. As a result the ribbon reads as a thin orange line in the far views (left_side, right_side, rear_side). | Deck half-width parameter was not scaled up in v003 (carried over from v002). | Widen the deck cross-section by about 1.3x (keep the parapet details), then re-check that the column positions and the ramp feet still clear the lanes and crossings. |
| 2 | P2 | all views (front, facade_close, glass_close, architecture_close) | The orange is darker and over-saturated next to the source. Rendered median orange is about (121–129, 44–48, 3–5) in shade and (149–151, 61–62, 19–20) where lit, at HSV S of about 0.9–0.98. The source parapet is about (165–180, 87–90, 38–49), at S of about 0.7–0.8. The hue matches (about 20°), but it reads as rust-red rather than bright powder-coat orange. | Albedo near-pure in R with almost no B, pushed further by the view transform and the overcast clay lighting. | Raise the albedo value and add blue (for example towards linear-equivalent sRGB 215, 115, 60), then re-sample until lit pixels land around (170–185, 85–95, 35–50). |
| 3 | P2 | front vs source front | The front composition is still mirrored. In the source, the deck with its hairpin S is in the right and foreground, the street runs below on the left, and the brick block is on the right. In the render, the deck is on the left, the street and median are on the right, and the block is on the right. | Camera placed on the opposite side of the ribbon's hairpin. | Move the front camera to the other side of the first hairpin, or flip its azimuth, so the street and the sidewalk with the Y-column sit at lower left as in the source. |
| 4 | P2 | facade_close, street_under, architecture_close, glass_close, deck_surface | The parapet has the right grammar but heavy proportions. Measured from the outside, the smooth fascia is about 0.34–0.42 of the orange depth (facade_close x = 612: screen 108 px, fascia 88 px; street_under x = 700: screen 50 px, fascia 41 px), against about 0.25–0.33 in the source. The bars are flat slats wider than their gaps, so close up they read as a picket fence, while the source has fine, close bars with more open area. The source also shows a light inner handrail line on the inside face, and the render has none. | Fascia 0.6 m against a short screen; bar pitch 9 cm at 16 cm centres; no inner handrail object. | Cut the fascia to about 0.45 m (or lift the top rail), thin the bars to about 5–6 cm at the same pitch, and add a slim pale inner handrail at about 0.9 m. |
| 5 | P2 | parapet_panel (about 560–600, 590–760), glass_close (about 1220–1245, 760–1080) | The rounded top rail and the outer fascia still show chord kinks on the silhouette at the tightest bend: about 5–7 straight segments are visible at 1:1. Shading is smooth, so this is silhouette only. In the overview views (front, ramp_curve) the rails read smooth. The builder's claim of "no chord facets" is false at the silhouette. | Rail and fascia sweep path sampled too coarsely for the bend radius; smooth shading cannot hide the silhouette. | Resample the sweep path at a 2–3 degree turn per segment (or adaptively on curvature) for the rail, the fascia and the bottom rail. |
| 6 | P2 | parapet_panel (about 540–560, 900–1080) | A dotted dark dash pattern runs down overlapping bars at the bend. | Coincident or near-coincident bar faces (z-fighting) where neighbouring bars overlap on the tight radius. | Offset bars radially by a few mm on tight bends, or reduce the bar count where the spacing collapses. |
| 7 | P2 | architecture_close (about 330–400, 670–690), y_column (about 690–760, 640–650), parapet_panel (about 160–240, 720–780) | The arm-to-soffit contact is now clean, but where the two arms join the shaft there is still a hard horizontal crease. The flared heads also show flat facets with a sharp step in parapet_panel. | Arms boolean-unioned onto the shaft with no blend; low segment count on the flare. | Add a smooth fillet or loft at the fork, and raise the segment count on the flared heads. |
| 8 | P2 | front (about 545, 697), ramp_curve (about 767, 635), rear (about 690, 645) | The median and corner column feet sit on the far kerb line of the median, or tight against the corner kerb next to a crossing. In front, the shaft base visibly coincides with the median edge, so the shaft could overhang the lane. | Columns placed at the deck centreline, which sits off-centre over the narrow median. | Snap each median column to the median centreline (or widen the median locally), and give corner columns at least 1 m clearance from the kerb and the crossing. |
| 9 | P2 | landing_ramp (about 775–790, 685–690), left_side (about 1020, 945) | A thin black slit shows under the outer parapet and fascia end where the ramp meets grade. | The fascia foot is offset 0.14 m above the soffit, and the ramp end cap does not close it at grade. | Close the end with a cap face, or run the fascia foot down to the ground where the ramp is within about 0.2 m of grade. |
| 10 | P2 | front, ramp_curve, aerial, top | Context planting is sparse. The medians are flat green strips with a few box hedges, and there are only a handful of low-poly trees. The source has dense shrub-planted lens medians, a continuous hedge and rows of street trees. | Minimal context set. | Add shrub mounds on the medians and a street-tree rhythm along both sidewalks (about 8–10 m spacing). |
| 11 | P2 | top (about 690–760, 380–470 and 700–800, 380–480) | Soft dark and light diagonal smudges lie on the sidewalk near the north-east block, with no clear caster. | Shadow or ambient-occlusion bleed from the deck or the building at a grazing sun. | Re-aim the sun or clamp the AO, or add the missing caster logic so the shadows read as shadows. |
| 12 | P2 | front_corner, rear_side, rear | Framing is weak but the target is still legible. In front_corner, the foreground south-east block hides the east third of the ribbon. In rear_side, the near ramp leaves the bottom of the frame, so neither ramp foot is shown. In rear, the ribbon is small and partly behind the blocks. | Camera positions not re-tuned after the context blocks were set. | Pull front_corner up and left to clear the south-east block, and frame rear_side so the near ramp foot lands inside the frame. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Plan and proportions | deviates (minor) | top vs source top, aerial | The S-wave amplitude (about 2x the road width) and the wavelength (crest over the N-S street, trough south of the boulevard, rising at the east edge) match the source closely. The deck is about 25% too narrow (finding 1). |
| Curve geometry | conforms | top, ramp_curve, left_side, right_side, glass_close | The curves are smooth and continuous, with receding S-curves along the street like the source oblique. There is tessellation at the tightest rail bend only (finding 5). |
| Deck and markings | conforms | deck_surface, glass_close, top | Dark surface with a white dashed centre line. The N-S street centre dashes stop clear of the zebras, and the zebras are clean. |
| Parapets | conforms (P2 proportion) | facade_close, architecture_close, street_under, parapet_panel, deck_surface, glass_close | There are separate fascia and screen elements with a dark reveal line, open vertical bars, a smooth rounded top rail and a clean bottom rail with no sawtooth. There are no black triangles at the cap. The pale soffit edge shows below the fascia. Proportions and coarseness are covered in finding 4. |
| Y-columns | conforms (P2 finish) | y_column, architecture_close, facade_close, front, parapet_panel | The columns are round, tapered and forked. The arms enter the soffit with no ring or disc, and the shafts are smooth. The fork crease remains (finding 7). |
| Ramps and landings | conforms | landing_ramp, left_side, right_side | The ramps descend gently to at-grade cycle paths. Parapets end with a plain end post at grade: no box end, curl-over or horns. There is a tiny slit at the end (finding 9). |
| Street beneath | conforms | street_under, ramp_curve, front, top, rear_north | A 4-lane boulevard with a median and a N-S cross street with zebras. No column stands in a traffic lane or a crossing, but the feet are at the kerb line (finding 8). |
| Context | deviates (minor) | front, aerial, top, ramp_curve | The brick blocks with punched windows are adequate as simplified context. Planting is sparse (finding 10). |
| Materials hierarchy | conforms (P2 tone) | all | Orange parapet, pale concrete soffit and columns, dark deck, brick context and green planting form the right hierarchy. The orange is too dark and saturated (finding 2). |

## 4. Camera validity

No view is invalid: in every view the target is legible and unclipped in its intended role.
- front: valid, but mirrored against the source composition (finding 3).
- front_corner: valid. The foreground south-east block covers about a third of the ribbon's east run (finding 12).
- aerial and top: valid. The ribbon runs off both frame edges, as in the source top.
- left_side and right_side: valid. Both show the receding S and a ramp foot at grade.
- rear: valid but weak. The ribbon is small and partly behind the blocks.
- rear_side: valid but weak. The near ramp is clipped by the bottom frame edge and the far end is hidden behind a block.
- Detail views: facade_close, architecture_close, glass_close, y_column, ramp_curve, parapet_panel, deck_surface, street_under, landing_ramp and rear_north are all valid, each frames its named subject, and there are no near-plane clips.

## 5. Previous findings — resolved in the pixels?

**v002 P1s**
1. Parapet and fascia read as one plain orange slab with no bars or split, like a deep box girder. **Resolved.** facade_close, street_under and architecture_close show a separate smooth fascia, a dark reveal line, a screen of open vertical bars and a rounded top rail. The pale soffit edge is visible below the fascia. The orange depth is now about 0.34–0.42 fascia and the rest screen, so it no longer reads as a solid girder. Remaining heaviness is P2 (finding 4).
2. Dark ring or flat disc where the Y-arms meet the soffit. **Resolved.** In y_column, architecture_close, facade_close, front and parapet_panel, the arms (with flared heads) pass straight into the soffit with no rim, disc or socket.
3. Black triangles at the folded-sheet cap seam, sawtooth bottom edge and faceted curved cap. **Resolved (black triangles and sawtooth); partly open (facets).** The folded sheet is gone and the bottom rail is a clean continuous band (deck_surface, parapet_panel). The rail is smooth-shaded, but its silhouette still shows chord kinks at the tightest bend in parapet_panel and glass_close. This is now P2 (finding 5), and the builder's "no chord facets" claim is not borne out at the silhouette.

**v002 P2s**
- Deck about 25% narrower than the source: **not resolved** (finding 1).
- Orange too amber and dark: **partly resolved.** It is redder now, but still dark and over-saturated (finding 2).
- Front composition mirrored: **not resolved** (finding 3).
- Faceted column shafts and hard fork crease: **shafts resolved** (smooth); **fork crease not resolved** (finding 7).
- Ribbon thin in far views: **not resolved** (follows from finding 1).
- Ground smudges in top: **reduced, faintly present** (finding 11).
- Black mark in each zebra crossing: **resolved.** All zebras are clean in top, front_corner, aerial and rear_north.
- Sparse context planting: **not resolved** (finding 10).
- Median column feet tight against the kerb: **not resolved** (finding 8).

**v001 fixes that must still hold**
- Both ramps descend gently to at-grade cycle paths, with no squared box end, curl-over or parapet horns: **holds** (landing_ramp, left_side, right_side).
- landing_ramp frames a ramp foot on the ground: **holds.**
- No Y-column in a traffic lane or crossing: **holds** (feet sit at the median or kerb edge, P2 finding 8).
- Columns round, tapered and forked: **holds.**

**Builder claims checked**
- Separate fascia with a reveal and the soffit edge showing: confirmed.
- Close vertical bars with open gaps: confirmed.
- Bars sunk into the rails with no seam or bar ends: confirmed.
- Smooth rounded rail with no chord facets: **not confirmed** at the silhouette on the tight bend.
- Arms run into the deck with no rim: confirmed.
- 20-sided smooth shafts: confirmed visually.
- Orange redder: confirmed, but too dark in the render.
- N-S dashes stop clear of the zebras: confirmed.
- Flat road markings and window frames: no artefacts seen.
