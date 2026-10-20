# Independent holistic review: clay-market-square v003 (RLASM v6.1 architectural clay)

Reviewer: independent, adversarial. Evidence used: the locked sources `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`, all 18 renders in `renders/`, and the four phone boards in `boards/`. I did not use metadata, hashes or builder notes as proof. Zoomed crops are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/crops-mktsq-v003-review-3208120334/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: The v002 scale and step-legibility defects are fixed, but the bowl now has reversed curvature on its upper tiers, which gives it a bow-tie plan. The narrowed terrace walks merge the three tiers into one continuous flight, and the plaza becomes a rectangle south of the splayed head. These are three clearly visible P1 fidelity defects.

Counts: P0 = 0, P1 = 3, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top, aerial, front_corner, phone-01 / phone-04 boards | **The bowl no longer reads as nested concentric arcs.** In plan (top) the foot tier is concave to the plaza, but the upper tiers bend the other way. Their middles bulge south toward the plaza and their ends sweep north to the high-bed corners. The bowl becomes a pinched bow-tie or butterfly, about 105 px deep on the axis against about 250 px at the wing ends. It has two triangular "wings" of tier running into diagonal meadow banks. In the source (top, oblique) all three tiers are parallel arcs concave to the plaza at near-constant spacing. Their outer ends curl north beside the stage up to the stacked-stone cheek walls, so the stage sits inside the crescent. In the render the top walk only reaches the stage-front line because the tier bend was reversed. Large rectangular high beds with straight front edges still flank the stage, where the source has curled tiers. | The v003 tier law `y = u + c x^2` with `c` changing sign through the bowl (top tier "bends forward"). This was a stand-in for wrapping the stage instead of keeping concentric arcs and extending them. | Restore one common centre (south of the foot on the axis) for all tier lines, with constant radial spacing. Extend the arc angle of the upper tiers so their ends rise north past the stage front to the cheek walls at stage level. Cut the front of each high bed back along the outermost arc instead of a straight east-west edge. Keep the v003 stage/pavilion widths and the 22 degree low-bed splay. |
| 2 | P1 | front, seating_tiers, bollard_grid, front_corner, aerial | **The three-tier rhythm is lost.** In front and seating_tiers the bowl reads as one uniform flight of about 9 equally spaced pale treads over stone risers (crop `front_tiers_zoom.png`), with no wide terrace walk anywhere. The source front shows three distinct tier bands separated by broad pale terraces that are wider than each stepped band. In front_corner and aerial the walks are narrower than the stepped bands, which inverts the source proportion (oblique: walk about 1.5 to 2 times the band). Because treads are pale and 0.55 m deep, the bowl reads almost entirely white from above. The source tiers read as warm stone bands between pale walks. | Over-correction of v002 P1 #2: the terrace walks were cut to 1.0 m plus the last tread, and treads were deepened, so band and walk became equal and merged. | Keep the pale 6 cm treads and 5 cm nosing shadow line. Reduce the tread depth to about 0.40 to 0.45 m and widen each terrace walk to about 2.0 to 2.5 m, so each walk is clearly wider than its three-step band. That gives three separate stone-and-tread bands in the front view, as in the source front. |
| 3 | P1 | top, aerial, front_corner, left_side, right_side | **The plaza does not flare toward the south.** The head now fans correctly: the bed walls leave the foot about 24 degrees off the foot line. But the bed walls run to the site edge, and from there the plaza edges run almost parallel to the axis, about 4 to 5 degrees in top. Bollard rows 3, 4 and 5 are the same length (crop `top_plaza.png`). In the source (top, oblique) the bed walls stop at an outer corner. The paving edge then keeps flaring outward to the south at a steep angle against open lawn, giving a trapezoidal plaza with lawn wedges outside both edges and each bollard row longer than the one before it. front_corner shows paving running the full frame width with no converging edges, where the source oblique shows a clear trapezoid. | The v003 fix moved all of the flare into the bed-wall splay and kept the southern plaza a rectangle sized to the site. | Stop each low-bed wall at an outer corner, about 1/3 of the way down the plaza, and return it north. From that corner, run the paving/lawn edge outward at roughly 25 to 30 degrees from the axis to the south boundary, with lawn outside it. Extend bollard rows 3 to 5 to the new edges on the same 3 m grid, keeping alternate rows offset. |
| 4 | P2 | stage_pavilion, aerial, cheek_walls | The stage deck is the same dark grey as the curved fascia. In the source the deck is a lighter grey and only the front edge is dark. | Single material on the stage solid. | Give the deck top a mid-grey concrete material and keep the fascia dark. |
| 5 | P2 | front, stage_pavilion | The pavilion is about 15% squatter than the source front: roof-top to stage height over width is about 0.27 against 0.32. | Width increased to 21.6 m with less than proportional height gain. | Raise the clear height to about 6.3 m, or deepen the roof slab slightly. |
| 6 | P2 | slat_wall, stage_pavilion, rear_north | The slats are all full height with varying width and tone only. The source back wall shows a blockier, staggered relief with short slat segments and varied depth steps. | Slats are generated as single full-height boards. | Split some slats into 2 or 3 stacked segments with depth offsets. |
| 7 | P2 | stage_pavilion, front | An untextured dark-grey end-cap strip shows at the east inner corner only (door recess), so the east and west ends are asymmetric from the front. | The backstage door recess panel is visible through the open front. | Clad the recess reveal in the dark slat tone, or set the panel back behind the return slats. |
| 8 | P2 | front, seating_tiers | A clipped bollard cap or shape intrudes at the bottom centre edge of the frame. | A near bollard sits just inside the near clip and frame. | Nudge the camera or crop so no bollard is cut by the frame edge. |
| 9 | P2 | aerial, top | The bowl's side ends finish against a sloping meadow bank with only a thin coping line. The source shows stacked-stone walls stepping with the tiers along the bowl ends. The stage side steps are not legible as steps (teaching assumption). | The diagonal bank is a sloped surface, not a stepped wall. | Step a stacked-stone end wall with the tiers along each bowl end, and give the side steps visible risers. This becomes moot if fix #1 re-shapes the ends. |
| 10 | P2 | rear_side | The site fills only about 45% of the frame width, with large empty ground. | Camera distance not tightened (not one of the three views the builder claims). | Move the camera in by about 35%. |
| 11 | P2 | light_mast | The top lamp heads sit tangent to a tree canopy behind them. There is no intersection, but it reads crowded. | Tree placed close to the mast. | Shift that tree about 2 m away from the mast. |
| 12 | P2 | meadow_beds, left_side, right_side | The low-poly meadow clumps are evenly sprinkled and do not read as a dense meadow field like the source's tall grass mass. | Clump abstraction (allowed by the brief). | Optionally increase clump density near the bed edges. |

(Severity rows: P1 = rows 1 to 3. P2 = rows 4 to 12, 9 rows. P0 = none.)

## 3. Source conformance checklist

| item | status | view used / note |
|---|---|---|
| Plan and proportions: plaza flare | deviates | top, aerial, front_corner: the head fans at about 24 degrees, then the plaza is rectangular (finding 3). |
| Plan: bowl arcs and chord | deviates | top: the foot chord is about 474 px and the top tier about 58 m wide, but the upper tiers reverse curvature and are not concentric (finding 1). |
| Plan: stage on axis | conforms | top, stage_pavilion: stage and pavilion are centred on the axis. |
| Stage / pavilion against foot chord | conforms | top: stage 346/474 = 0.73 (source oblique 0.73); roof 294/474 = 0.62 (source 0.62). |
| Paving slabs and joints | conforms | paving_drain, front, bollard_grid: square slabs, with a stronger joint every 4 slabs, including the axis joint. |
| Bollard grid | conforms | top, bollard_grid, front: stubby octagonal drums on a 3 m grid, five rows, alternate rows offset by half a bay. Row lengths do not grow as the source's do (finding 3). |
| Floor drains | conforms | paving_drain, seating_tiers: one square slotted grate centred in a slab. |
| Seating tiers: count | conforms in plan, deviates in elevation | aerial and front_corner show three groups; front and seating_tiers read as one flight (finding 2). |
| Seating tiers: 3 steps per tier, stone risers, concrete treads | conforms | seat_left crop, seating_tiers: pale treads with a nosing shadow line; coursed ledgestone risers with dark bed and staggered head joints. |
| Seating tiers: terrace walks | deviates | front_corner, aerial, front: the walks are narrower than the stepped bands; the source has wide walks (finding 2). |
| Cheek walls | conforms | cheek_walls, aerial: stacked stone with pale coping, stepping up at both stage ends. |
| Raised meadow beds, stone retaining walls, copings | conforms (form of the high beds deviates) | meadow_beds, left_side, right_side, rear_north: stacked-stone walls with coping. The low wedge beds are correct; the high beds have straight rectangular fronts where the source has arcs (finding 1). |
| Upper terrace | conforms | aerial, cheek_walls: a pale walk in front of the stage, reaching the stage-front line. |
| Stage platform and curved fascia | conforms (P2 deck tone) | stage_pavilion, aerial: dark curved front edge, convex to the plaza. |
| Pavilion slat cladding | conforms (P2 relief) | slat_wall, stage_pavilion, rear_north: mixed widths, three tones, varied depth. |
| Pavilion returns | conforms | stage_pavilion, rear_side: slatted side returns. |
| Pavilion roof slab | conforms | stage_pavilion, aerial: a deep flat dark slab with overhang. |
| Loudspeakers | conforms | stage_pavilion, seating_tiers: one near each end of the back wall. |
| Backstage door | conforms (teaching assumption) | backstage_door: a recessed panelled door in the east return, with a reveal and threshold on the deck. |
| Floodlight masts and lamp heads | conforms | light_mast, front, rear: two slender dark masts, six stacked heads each, just outside the pavilion. |
| Trees and meadow | conforms | top, meadow_beds, front: broad shade trees on the high and low beds; meadow as clumps. |
| Lawn and context | conforms, with the lawn wedges outside the plaza missing | top, rear, rear_north: lawn and tree belt to the north; no lawn wedges flank the southern plaza (finding 3). |
| Materials hierarchy | deviates | front_corner, aerial: the bowl reads pale/white overall where the source reads warm stone bands with pale walks (finding 2). Slats, dark roof and grey paving are correct. |
| Grounding | conforms | all views: no floating or below-grade parts seen. Bollards, trees, masts, walls and the pavilion all sit on their surfaces. |

## 4. Camera validity

- All 18 renders are present and legible. The target is not occluded or clipped in any whole-envelope view.
- front: valid, with the low bed walls visible at both frame edges as in the source front. A clipped bollard cap shows at the bottom centre (P2 #8).
- seating_tiers: valid; same bottom-edge bollard intrusion (P2 #8).
- left_side, right_side: valid and tight on the site. The high bed hides part of the bowl, but the pavilion, tiers and plaza stay legible.
- rear: valid; the site spans the full width.
- rear_side: valid but loose, with the site at about 45% of the frame (P2 #10).
- The brief's generic list also names facade_close, architecture_close and glass_close. They are not among the 18 views produced, and they are not applicable to an open-space archetype. I did not count this as a defect.

## 5. Previous-version (v002) findings: resolved in the pixels?

1. **The pavilion and stage were under-scaled and the bowl did not wrap the stage.** Scale is **resolved**: measured in top, stage/foot chord = 0.73 and roof/foot chord = 0.62, matching the source (0.73 and 0.62). The cheek walls now sit at the stage ends. The wrap is **only partly resolved**. The top walk reaches the stage-front line, but by reversing the upper-tier curvature, not by extending concentric arcs up beside the stage. The stage still sits between two straight-fronted rectangular high beds. This is carried forward as new P1 #1.
2. **The three steps per tier were not legible.** **Resolved** at step level: three pale concrete treads with nosing shadow lines over three coursed ledgestone risers per tier (seating_tiers, seat_left crop). The fix narrowed the terrace walks so far that the tiers merge into one continuous flight in the front views. This is a new P1, #2.
3. **The plaza did not fan out at the bowl foot.** **Resolved at the head**: the bed walls leave each foot end about 24 degrees off the foot line. The low wedge beds carry shade trees, and the low bed walls show at both edges of the front frame. **Not resolved for the plaza as a whole**: south of the beds the plaza edges again run almost parallel to the axis. This is P1 #3.

The builder's claimed P2 fixes:
- Single square slotted grate centred in a slab: **verified** (paving_drain).
- Side and rear views framed tight: **verified** for left_side, right_side and rear. rear_side is still loose.
- Extra shade trees on the low wedge beds: **verified** (top, meadow_beds, left_side, right_side: two trees per wedge).

Regression checks:
- The v002 fixes still hold. The lowest tier is concave to the plaza (top, aerial). The bollards are stubby drums on the 3 m grid, five rows with alternate rows offset. Stacked-stone cheek walls stand at both stage ends.
- The v001 fix holds: stacked ledgestone on every riser, with dark bed and staggered head joints.
- What earlier versions got right still holds: square slabs with stronger 6 m joints; the slatted open-fronted pavilion under a deep dark roof with loudspeakers; two masts with six stacked lamp heads; raised stone-walled meadow beds with shade trees; meadow and lawn beyond.
