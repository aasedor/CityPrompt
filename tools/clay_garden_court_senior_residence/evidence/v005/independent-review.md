# Independent holistic review: garden-court senior residence, v005 (RLASM v6.1 architectural clay)

Reviewer: independent; did not build this candidate. I judged only the pixels. I opened all 18 renders at full resolution, the three locked sources (front.png, oblique.jpg, top.jpg) and the four phone boards. I made zoomed crops into a new folder only: `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indrev-v005-crops-7q3/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: Both v004 P1s are fixed in the pixels and the envelope, plan and identity elements hold. One P1 remains. The octagonal garden room has no door on its court face, which is the focal point of both perspective sources. The court path ends against fixed glazing.

Counts: P0 = 0, P1 = 1, P2 = 8

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | court_view, architecture_close, glass_close (vs sources front.png / oblique.jpg) | The court-facing side of the octagonal garden room is fixed glazing all the way down: a 3-pane transom over 4x2 fixed lites, with one continuous sill at grade. There is no door leaf, no door frame and no step. The court's circular brick path runs straight into this glass wall. Both perspective sources show a white double French door with a transom and a stone step at the centre of this face, and the court path leads to it. That door is the garden room's entrance from the court. | The garden-room glazing module was used on all eight sides. The door variant was never placed on the court face. | On the court-facing side, replace the lower 4x2 fixed lites with a pair of glazed French doors: a thicker stile and rail frame, a visible centre meeting stile, and a recess or return of at least 5 cm. Keep the 3-pane transom above. Add a single brick or stone step where the court path meets the door. Re-render court_view, architecture_close and glass_close. |
| 2 | P2 | loggia_arcade (top edge) | The sill of a window on the wall behind the loggia sits exactly on the loggia roof's top edge. The window is whole, but there is no visible flashing gap. | Window omission or offset is tuned to the edge of the clearance. | Raise that window or the course of windows a little, or add a flashing strip about 0.15 m below the sill. |
| 3 | P2 | court_view (cv_ne_westface crop), front | Where windows were removed beside the abutting loggias, the NE pavilion's west face has blank second-storey bays. The window rhythm breaks there; no source shows this face. | The fix for v004 #1 removed windows rather than moving them. | Optional: place a narrower window or a blind recess in the vacated bays, kept clear of the hip. |
| 4 | P2 | architecture_close, hub_cupola | Where the loggia hips meet the octagonal roof, a small extra triangular hip facet and a step show at the valley. | Two hipped solids overlap without a trimmed valley. | Trim the loggia hip to the octagon roof plane, or add a valley flashing. |
| 5 | P2 | loggia_arcade | A thin white sliver of plinth shows at the base of the left pier, between the arch reveal and the pier face. | The plinth or base strip extends a little past the pier return. | Shorten or clip the plinth at the reveal. |
| 6 | P2 | court_view (SW corner) | The right iron end of the south-west bench stands against the side of the pink rose bed and visually touches it. | The bench is placed without clearance to the bed footprint. | Move the bench about 0.3 to 0.5 m clear of the bed. |
| 7 | P2 | court_view | Rose beds read as raised pink octagonal plinths with a green shrub on top. Pink and green are inverted compared with the source, where green shrubs carry pink flowers on low mulched beds. | Flower colour is put on the bed solid instead of on the planting. | Lower the bed to near grade and use brown or green mulch. Put the pink on the shrub masses. |
| 8 | P2 | court_view, pergola_terrace | The bench seats read as one solid plank with no slat separation. The source has small white pedestals (birdbaths or sundials) on the lawns; the render has none. | The bench seat is one box. Small court ornaments were omitted. | Split the seat into 3 to 4 slats with gaps. Add 2 to 3 white pedestals on the lawns. |
| 9 | P2 | front (front_ne2 crop) vs interior | The ground-floor door under the NE pavilion balcony is rectangular. The interior view shows an arched garden door with a fanlight under a balcony elsewhere. The arched-door grammar is not consistent across the court faces. | There are two door modules. | Use the arched garden door under every court balcony. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Silhouette | conforms | front, front_corner, aerial, rear, rear_side vs front.png / oblique.jpg | Ring of large three-storey blocks with hipped copper roofs, low arcaded links and a central octagonal garden room with a cupola reading above the link roofs. |
| Storey count | conforms | right_side, left_side, rear, dormer_roof, hub_cupola | Three brick storeys plus a dormered roof storey on every block. Loggias are one storey. |
| Plan (ring of blocks, court) | conforms (follows top.jpg as the brief allows) | top vs top.jpg | Two north pavilions with the garden room on the link between them; SW pavilion; long south wing; long east wing offset east, with a link to the NE pavilion; west link from the NW to the SW pavilion; corner links from the south wing to the SW pavilion and to the east wing. The court is enclosed. Link lengths are a little shorter than in the source (P2-level, not logged). |
| Roofs and dormers | conforms | dormer_roof, top, front, front_corner | Pavilions are hipped to a flat top with rooftop units. Wings are hipped to a ridge. Gabled dormers with white double-hung windows sit on every slope, with standing seams. Dormers sit on the slopes with no floating. |
| Loggias and arches | conforms (P2 #2, #4, #5) | loggia_arcade, court_view, front (selink, swlink crops) | Brick round arches with depth, inner vault reveals, impost blocks, and copper standing-seam roofs with white fascia. They link every block. |
| Garden room and cupola | deviates (P1 #1) | architecture_close, glass_close, hub_cupola, court_view | Octagonal white-framed glazing, copper octagonal roof, glazed drum and ribbed glass dome with finial, all seated cleanly. The interior shows tables and chairs. The court-face French door is missing. |
| Window rhythm and balconies | conforms (P2 #3, #9) | facade_close, pergola_terrace, court_view, interior, front | White double-hung windows with projecting sills, lintels and visible inset. Bays are regular. Iron balconies with French doors sit on the court faces of the north pavilions. An arched garden door is visible in interior. |
| Garden elements: paths | conforms | court_view, top | Brick-coloured circular path around the central lawn, cross axes, and a path to the pergola. |
| Garden elements: fountain | conforms | court_view, interior | Tiered fountain in the SW of the court, ringed by rose beds (P2 #7). |
| Garden elements: beds | conforms | garden_beds, court_view | Fenced garden with iron railings, timber raised beds, soil, planting, and paving under them. Contact is clean. |
| Garden elements: pergola | conforms | pergola_terrace, court_view | Timber posts standing on paving, beams and rafters, dining tables with legs, chairs. |
| Benches | conforms (P2 #6, #8) | court_view crops, pergola_terrace | Seat, back, dark iron ends with legs, arms and back posts, standing on paving or lawn. |
| Forecourt | conforms | top, hub_cupola, rear_side | Circular lawn with cross paths, a tiered fountain, and a drive loop with an island to the north. |
| Materials hierarchy | conforms | all | Salmon-red brick body, pale copper roofs, white trim and frames, glass, timber for beds and pergola, dark iron for railings and bench ends. These are clay source-palette colours. |

## 4. Camera validity

- front, front_corner: valid. The whole envelope is in frame from high above the south, and court contents are legible.
- aerial, rear_side: valid. The whole envelope is in frame, with a smaller subject.
- top: valid. Orthographic-like plan, nothing clipped.
- left_side, right_side, rear: valid but distant. The model fills about half the frame width and little of its height. Still legible, with nothing clipped.
- court_view: valid, and matches front.png in composition: garden room top centre, fountain lower left, fenced beds lower centre-right, pergola right.
- facade_close, architecture_close, glass_close, loggia_arcade, dormer_roof, hub_cupola, garden_beds, pergola_terrace, interior: valid. Each target is unoccluded and legible. In loggia_arcade a foreground tree covers the top-left corner, but the arcade remains readable.
- No invalid camera found.

## 5. Status of v004 findings

| v004 finding | status in v005 pixels | evidence |
|---|---|---|
| P1: the NE loggia's hipped end ran over a second-storey window on the NE pavilion's west face | **Resolved** | In court_view (crop cv_ne_westface), the NE loggia's hipped end meets the west face against blank brick. The nearest second-storey window sits clear above and beside the hip, with its sill visible above the roof line. No window is cut by any loggia roof in court_view, architecture_close or hub_cupola. Windows behind roofs are only occluded by perspective. The repair leaves blank bays (P2 #3). |
| P1: court benches were legless slabs floating above the paving | **Resolved** | In court_view crops (centre, east, north and SW benches) and in pergola_terrace, each bench has a seat, a back panel, and dark iron ends with legs, arm rails and back posts, and stands on paving or lawn with a contact shadow. The seat reads as one plank rather than slats (P2 #8). |
