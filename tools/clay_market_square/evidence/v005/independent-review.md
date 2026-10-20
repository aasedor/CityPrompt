# Independent holistic review: mktsq v005 (RLASM v6.1 architectural clay)

Reviewer: independent; did not build the candidate. Evidence is limited to the pixels of `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, all 18 `renders/*.png` at full resolution, and the four phone boards. Zoomed crops were written only to the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/crops-v005-indrev-1207023018/`. The scale used below comes from the render's own paving: in `top.png` the strong 6 m joints repeat every 77 px, so 12.8 px = 1 m.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** Both v004 findings are fixed in geometry: the tiers no longer reverse, and the band-to-walk depth ratio is now about 2.6:1. However, four P1 defects block production approval:
- The landform is graded as flat plateaus behind sheer stone cliffs.
- The two-band and walk rhythm of the bowl still reads as one continuous flight of pale steps.
- The stage side steps shown in the source are missing.
- The ends of the steps overrun the bed walls.

Counts: P0 = 0, P1 = 4, P2 = 6

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | left_side, right_side, rear, rear_north, rear_side, meadow_beds, front, front_corner, aerial | **Landform is a mesa, not raised meadow beds.**<br>- Each flank above the bowl is a flat meadow plateau at about the wing-top level, roughly 3.6 m above the plaza.<br>- Sheer coursed-stone cliffs bound the plateaus on the outer flanks: the wall is about 210 px tall in left_side against a lawn at plaza level.<br>- A wall runs along the whole north edge, with lawn below it (rear, rear_north).<br>- A second tall stone wall faces south across each bed, above a small triangular lower bed by the plaza. It is visible in front (x 0–115 and 1320–1440, y 495–580), front_corner, aerial and meadow_beds.<br>- In the source, the beds along the flared plaza edges sit behind *low* stacked-stone walls about 0.6–1 m high (oblique, top). The bed is one continuous meadow that rises from the plaza wall to the backs of the wings, with its big shade tree inside it. The source shows no tall south-facing cross wall within the bed.<br>- In the source, the meadow behind the stage runs on to the path, the lawn field and the tree belt without any visible wall (top, oblique).<br>- The render's lower beds are small triangles holding one tree each. The source beds are large. | The upper plateau was extruded as a level block at wing-top height and retained on every side with full-height walls, instead of sloping the bed surface. | Make each side bed one meadow surface that slopes from the low plaza-edge wall (about 0.8 m with coping) up to the backs of the wings. Then:<br>- delete the south-facing cross wall;<br>- lower the outer flank and north walls to bed-wall height, or grade them out to lawn;<br>- bring the far lawn up to meet the meadow behind the stage, as the source top shows;<br>- enlarge the lower bed so it holds the broad shade tree beside the bowl, as the oblique shows. |
| 2 | P1 | aerial, front_corner, top, front | **The bowl still reads as a pale six-step flight, not two stone seating bands with pale walks.**<br>- Measured on the axis in top: terrace (153,154,153), band 2 (154,151,144), walk (160,161,160), band 1 (158,155,148), plaza (157,159,158). The "warm-stone bands" differ from the walks by about 6 to 8 RGB units, so the walk cannot be found at native scale.<br>- front_corner on the axis: treads (155,152,145), walk (160,161,160), risers only (130–145). The deep pale treads take up most of every band, and the stone risers read as thin stripes.<br>- Source oblique: each band is a warm stone stack with thin pale nosing lines. The two neutral pale walks separate the bands clearly (front, oblique, top). | The 0.85 m treads are a light warm stone of almost the same value as the concrete walks. Seen from above or at an angle, tread area dominates and swamps the 0.40 m stone risers. | Keep the geometry (2.55 m band, 1.0 m walk), but separate the materials:<br>- give the seat treads the warm-grey stone value of the risers, or narrow the pale concrete to a nosing strip of about 0.10–0.15 m;<br>- keep the walks and terrace a neutral pale concrete, at least 15 L* lighter than the band average in aerial and top. |
| 3 | P1 | aerial, top, front_corner, left_side, right_side (vs source oblique, top, front) | **Stage side steps are missing.**<br>- In the source oblique and top, a short stair flight rises northward at each pavilion end, between the slatted side wall and the cheek wall, to the meadow behind. The source front also shows step faces behind the right cheek wall.<br>- In the render, flat pale terrace strips run up to a raised meadow edge, with no steps.<br>- The stage deck, about 0.6 m high, has no step access from the terrace anywhere (left_side and right_side show a plain rounded deck end). | The brief's teaching-assumption element was never modelled. | Add one flight of about 4–5 steps in each gap between pavilion return and cheek wall, using the same stone risers and pale treads. It climbs from the upper-terrace level to the back meadow, with the cheek wall as its stringer. Optionally add 2 deck steps at each stage end. |
| 4 | P1 | front_corner (both band ends), aerial (both ends), left_side, meadow_beds | **The ends of the steps overrun the bed walls.**<br>- Dark raw end faces and tread-nosing stubs stick out past the diagonal bed-wall plane at every band and walk end. In front_corner there is a dark L-shaped stub at about x 120–150, y 685–700, and a dark vertical sliver about 40 px tall where the band-2 walk meets the right cross wall (about x 1270–1320, y 680–720).<br>- In left_side a tread slab pokes through the plateau corner, past the wall face (about x 740–790, y 650–670).<br>- In meadow_beds the step end caps hang as a dark strip above the lower-bed meadow. | The step solids were cut by the bed outline but not trimmed to the inner face of the retaining wall, and no end cheek or closure was added. | Clip every tread, riser and walk to the inner face of the bed wall, or add a stacked-stone end cheek with coping that the steps die into. Then confirm in front_corner and aerial that no end face is visible past a wall plane. |
| 5 | P2 | light_mast, front, aerial | The six lamp heads are pale white boxes. The source heads are dark, matching the mast. | Default light material on the heads. | Give the lamp-head housings the dark mast colour, with a pale lens face only. |
| 6 | P2 | left_side, light_mast, right_side | Both pavilion returns carry a dark panel with a door. The brief names the east return only. | Mirrored return module. | Clad the west return in slats only. |
| 7 | P2 | left_side (plateau corner) | The wall return at the plateau corner shows a much finer stone pattern than the adjoining faces. | UV or texel scale not matched on the return face. | Use the same course height and stone length on all faces. |
| 8 | P2 | cheek_walls, aerial, front | The cheek walls are short straight north–south walls. In the source front and oblique, the cheek walls sweep outward and step up along the backs of the wings. | Simplified plan. | Extend each cheek wall as a stepped wall with coping along the back edge of its wing. |
| 9 | P2 | slat_wall, stage_pavilion | The slats are full-height uniform strips. The source reads as shorter, irregular vertical pieces with stronger depth relief. | Slat module only varies width, tone and depth. | Optionally break the slats into staggered vertical lengths. |
| 10 | P2 | rear_side | The model fills only about 35% of the frame width, with a large empty grey field around it. It is still legible. | Camera distance. | Dolly in about 30%. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Plaza flare | conforms | top, aerial | Flares continuously from the bowl foot to the south edge, first between the bed walls and then against lawn wedges. |
| Bowl arcs and chord | conforms | top | All tier lines are arcs of one centre and concave to the plaza. Foot chord is about 36 m (463 px). |
| Stage on axis | conforms | top | Stage is about 27 m wide, about 0.75 of the foot chord, and on the axis. |
| Paving slabs and joints | conforms | paving_drain, top | 1.5 m slabs with heavier joints every 6 m. |
| Bollard grid | conforms | top, front, bollard_grid | 3 m spacing in each row; five rows about 4.5 m apart (matches the source top's foreshortened spacing); alternate rows offset by half a bay; rows lengthen southward; stubby drums. |
| Floor drains | conforms | paving_drain, top | Single square slotted grates on their own grid. |
| Seating tiers, count and steps | conforms | top, front, aerial | Two full bands in front of the stage (3 + 3 risers including the terrace edge), plus three-step wings beside the stage. |
| Seating tiers, stone risers | conforms | seating_tiers | Stacked ledgestone with bed and staggered head joints. |
| Seating tiers, concrete treads and terraces | deviates | aerial, front_corner, top | Treads are a light warm stone almost the same value as the walks, so the band and walk rhythm is not legible (finding 2). |
| Cheek walls | conforms, simplified | cheek_walls, front_corner | Stacked stone with coping, stepped, retaining the inner ends of the wings. Simplified plan (finding 8). |
| Raised meadow beds and stone retaining walls with copings | deviates | left_side, right_side, meadow_beds, front, aerial | Copings are present, but the beds are flat high plateaus with cliff walls instead of low walls and a rising meadow (finding 1). |
| Upper terrace | conforms | top, aerial | Pale terrace about 1.75 m deep on the axis, before the stage. |
| Stage platform and curved fascia | conforms | stage_pavilion, aerial | Gently curved dark fascia. |
| Stage side steps | deviates | aerial, top, left_side, right_side | Absent (finding 3). |
| Pavilion slat cladding | conforms | slat_wall, stage_pavilion | Mixed widths, depths and three tones. |
| Pavilion returns | conforms | stage_pavilion, front_corner | Slatted returns, open front. |
| Pavilion roof slab | conforms | aerial, front | Deep flat dark slab. |
| Loudspeakers | conforms | stage_pavilion | One near each end of the back wall. |
| Backstage door | conforms | backstage_door | Recessed, with a frame return, in the east return. Also duplicated on the west return (finding 6). |
| Floodlight masts and lamp heads | conforms | light_mast, front | Two slender dark masts just outside the pavilion, each with six stacked heads. Head colour P2 (finding 5). |
| Trees and meadow | conforms | aerial, top | Broad shade trees and clumped meadow on the beds, plus a tree belt. |
| Lawn and context | deviates | rear, rear_north, top | Lawn and tree belt are present, but separated from the meadow by a tall north wall, where the source has continuous ground (finding 1). |
| Materials hierarchy | deviates | aerial, front_corner | Stone, timber, dark stage and roof, and pale plaza read correctly. The bowl's stone over concrete hierarchy is weak (finding 2). |
| Grounding | deviates | front_corner, aerial, left_side | Pavilion, masts, bollards and trees are grounded. Step ends protrude through the bed-wall planes (finding 4). |

## 4. Camera validity

All 18 delivered views are valid. None has its target occluded, clipped or illegible.
- rear_side frames the model small, but it is legible (P2, finding 10).
- light_mast shows all six heads against the sky.
- slat_wall is a deliberate full-frame material close-up.

The brief's view list also names `facade_close`, `architecture_close` and `glass_close`. These are generic building names that do not apply to an open space, and the 18 delivered files match the brief's count of 18 views, so they are not counted as missing.

## 5. Previous-version findings: are they resolved in the pixels?

**v004 P1-1: top tier reverses its bend (W shape, gull wing, pale wedges at the ends).** RESOLVED.
- Traced in top: every line is a single arc, highest (furthest north) on the axis and furthest south at the outer ends. None reverses.
- Aerial and front_corner show smooth concentric arcs with no gull-wing and no pale end wedges.
- Only two bands run across in front of the stage. The third tier exists only as three-step wings beside the stage, concentric with the bowl, with their inner ends buried in the cheek walls.

**v004 P1-2: band-to-walk proportion inverted (pale ramp with thin stone stripes).** PARTIALLY RESOLVED.
- Geometry is fixed. Measured in top: band 1 about 33 px (2.6 m), walk about 8 px plus nosing (about 1 m), band 2 about 21 px, terrace about 22 px (1.7 m). That is a ratio of about 2.6:1, inside the 2.5–4 range the source shows.
- The visual reading is not fixed. The deep treads have almost the same value as the walks, so in aerial, front_corner and top the bowl still reads as pale steps with thin stone stripes, and the walks do not register (finding 2, kept at P1).

**v004 plaza flare and lengthening bollard rows.** HOLDS (top, aerial).

**v003: 27 m curved stage, 21.6 m slatted pavilion with loudspeakers and backstage door, legible steps with nosing shadow.** HOLDS.
- Stage about 27 m; pavilion about 22 m between returns.
- seating_tiers shows a nosing shadow line over each stone riser.

**v002: lowest tier concave; stubby drum bollards on the 3 m grid in five offset rows; stacked-stone cheek walls at both stage ends.** HOLDS.

**v001: stacked ledgestone on every riser with dark bed and staggered head joints.** HOLDS (seating_tiers, front).

**Earlier correct items: square slabs with 6 m joints, single square drain grates, two floodlight masts with stacked heads, raised stone-walled meadow beds with shade trees, meadow and lawn beyond.** HOLD, with one exception: the stone-walled beds are now over-raised into cliff-walled plateaus (finding 1).
