# Independent holistic review: clay-market-square v002 (RLASM v6.1 architectural clay)

Reviewer: independent, adversarial. Evidence: the rendered pixels in `renders/` and `boards/`, compared with the locked `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. I ignored the build report, the evidence JSON and the builder's claims as proof. I made zoomed crops into a new folder, `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/review-crops-mktsq-v002-324857106/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the v001 P0 is fixed, because the bowl is now concave to the plaza. Three P1 defects remain:
- the stage pavilion is about 60% of the source's size relative to the bowl, and the bowl does not wrap the stage;
- the seat steps are not legible;
- the plaza does not splay at the bowl foot as it does in the source.

Counts: P0 = 0, P1 = 3, P2 = 7

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top, aerial, front_corner, front, phone-01 | **The pavilion and stage are under-scaled, and the bowl does not wrap the stage.** In the locked top and oblique, the pavilion roof is about 0.62 of the bowl-foot chord and the stage platform about 0.75. The 3 m bollard spacing calibrates the pavilion at 21 m or more. In the render top, the roof is 179 px against a 485 px foot chord (0.37), which is about 13.4 m at the 40 px = 3 m bollard pitch. The stage is about 0.44 of the chord. In the source, the ends of the upper tier sweep north past the stage front and flank the stage at upper-terrace level, with the cheek walls closing them. In the render, all three tiers end well south of the stage front, and the stage sits in a narrow slot between two large rectangular beds. The stage reads as a small kiosk at the end of an oversized bowl, not as the dominant focus of the source. In the front view, the bowl spans the full frame while the pavilion takes 0.30 of the frame width; in the source it takes 0.38 and low bed walls flank the bowl foot. | The pavilion and stage were sized independently of the bowl, or kept from v001 when the bowl was re-radiused to R 40 to 47.4 m. The tier end angle is cut short of the stage line. | Widen the pavilion to about 22 to 24 m overall (roof about 0.6 of the foot chord) and the stage platform to about 0.75 of the chord, keeping the pavilion's height-to-width ratio (the current ratio, about 0.37, is right). Extend the upper tier, or upper two tiers, north so their ends rise beside the stage at upper-terrace level. Seat the cheek walls between those tier ends and the pavilion returns. Re-check against the locked top: the roof should cover about 62% of the foot chord. |
| 2 | P1 | seating_tiers, front, front_corner, aerial, top | **The three steps per tier are not legible; each tier reads as one coursed stone wall or kerb.** In the top view, each tier's stepped band is about 7 px (about 0.55 m) deep against terrace walks of about 35 px (about 2.6 m). That implies a step going of about 0.18 m. In the locked oblique and top, the stepped band is as deep as the terrace walk or deeper. In seating_tiers, the lower tier is a continuous 0.9 m ledgestone face with no tread lines or nosing shadows between the three risers. The upper tiers also read as continuous walls. The treads are the same warm stone as the risers, so the "stacked warm-grey stone risers under pale concrete treads" hierarchy of the source, which shows three pale tread lines per tier in front.png and oblique.jpg, is gone. In front and front_corner, each tier is a single beige band. | The v001 fix made the risers full height and the treads 30 mm warm stone, but the step going was left very short. With a same-colour tread and no nosing, the steps merge visually. | Three steps per tier at about 0.30 m rise and about 0.45 m going, so the stepped band is about 1.35 m. Set the terrace walk at about 1.8 to 2.0 m. Use pale concrete tread slabs of 60 to 80 mm with a 20 to 30 mm nosing overhang that casts a dark line. Keep ledgestone on the riser faces only. Verify that seating_tiers shows three distinct pale tread lines per tier and that the top view shows striped bands about as deep as the walks. |
| 3 | P1 | top, aerial, front_corner, front, phone-01 | **The plaza does not flare at the bowl foot as it does in the source.** In the locked top and oblique, the stone bed walls leave each bowl-foot end at a shallow angle, about 20 to 25° below the foot line, and run outward for most of the plaza width. The plaza opens into a broad fan, and bollard row 1 is already about 1.6x the bowl-foot chord (oblique: 160 to 1060 px against 330 to 890 px). In the render, the plaza edges leave the foot ends nearly parallel to the axis, about 18° off axis, giving a narrow trapezoid: in the aerial, row 1 is only about 1.05x the foot chord. The source's low wedge beds between the plaza and the lawn are replaced by large rectangular raised beds running north to the stage. In the front view, the low bed walls that flank the bowl foot horizontally in the source are absent. | The plaza outline is a simple trapezoid hung off the bowl-foot ends, not the source's splayed bed-wall line. | From each bowl-foot end, run the plaza-edge bed wall outward at about 65 to 70° off the axis for about 12 to 15 m. Then continue the plaza-to-lawn edge south with the gentler flare. Widen bollard rows 1 to 5 to fill the fan, keeping the 3 m grid and the alternate-row offset. Re-trim the beds into the source's wedge shape. |
| 4 | P2 | rear, rear_north, rear_side, left_side, right_side, meadow_beds | The north half of the site sits on a walled plinth 2 to 3 m high with continuous coursed walls on all outer sides. In the source oblique, the meadow behind the stage runs into the lawn and path without a visible wall. This is a coherent teaching assumption but heavy. | The beds are extruded to upper-terrace height, with vertical retaining walls at the perimeter. | Grade the outer meadow down to the lawn, or step the perimeter wall down to a low kerb at the north and outer edges. |
| 5 | P2 | backstage_door | The long face of the cheek wall next to the east return is plain, uncoursed beige with two stray groove lines. Its other faces carry ledgestone. | The stone coursing is applied to selected faces only. | Apply the ledgestone coursing to every exposed cheek-wall face. |
| 6 | P2 | slat_wall, stage_pavilion, front | The slats are continuous full-height boards. The source back wall reads as staggered, fragmented vertical pieces of varying length and projection. | The slats are a single vertical extrusion. | Break the slats into two or three staggered lengths with varied projection. |
| 7 | P2 | top, aerial, front_corner | The shade trees near the plaza flanks are sparse and small; there is one tree per bed near the plaza. The source has broad canopies massing over the tier ends and bed corners. | The tree count and placement are biased toward the back corners. | Move two or three broad canopies over the bed corners beside the bowl ends. |
| 8 | P2 | paving_drain, aerial | The drains are pairs of rectangular slotted plates straddling a joint. The source shows small single square grates. | Drain module choice. | Use a single square slotted grate centred in a slab. |
| 9 | P2 | left_side, right_side, rear | The asset fills only about 45 to 55% of the frame width, with large empty grey bands. The views are legible but carry little information. | Camera distance and FOV. | Tighten the framing so the asset spans about 80% of the width. |
| 10 | P2 | (render set) | The brief's list names facade_close, architecture_close and glass_close. They are not present, but the 18 views present match the brief's count of 18. | Generic building detail roles are not applicable to an open space. | No action needed beyond recording that the roles are not applicable. |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Plan: plaza flare | **deviates**: the plaza flares only gently from the foot ends, with no splayed bed walls (F3) | top, aerial vs top.jpg and oblique.jpg |
| Plan: bowl arcs and chord | conforms in direction (∩, concave to the plaza, tiers lengthening as they rise). The foot chord is about 36 m, consistent with about 38 m. The top-tier ends stop south of the stage line (F1). | top, aerial, front_corner |
| Plan: stage on axis | conforms: the stage and pavilion are centred on the axis | top |
| Proportion: pavilion and stage vs bowl | **deviates**: about 0.6x the source's relative width (F1) | top, aerial, front |
| Paving slabs and joints | conforms: square 1.5 m slabs with a stronger joint every 4 slabs (6 m) | top (zoom), paving_drain, aerial |
| Bollard grid | conforms: 5 rows on a 3 m pitch, alternate rows offset by half a pitch, rows lengthening southward (11 to 15 bollards). Short drums of about 1.4:1. | top (zoom), aerial, bollard_grid, front |
| Floor drains | conforms (flush, slotted). Form differs slightly (F8). | paving_drain, top |
| Seating tiers: count | conforms: 3 tiers | top, aerial, front_corner |
| Seating tiers: 3 steps each | **not legible / deviates** (F2) | seating_tiers, front_corner, aerial |
| Stone risers | conforms: stacked ledgestone in three warm-grey tones with dark joints | seating_tiers, front |
| Concrete treads | **deviates**: the treads are warm stone and visually absent (F2) | seating_tiers, front |
| Terrace walks between tiers | conforms in material (pale concrete) but too deep relative to the steps (F2) | top, aerial |
| Cheek walls | conforms: stacked stone with concrete copings, stepping up at both stage ends | cheek_walls, light_mast, front, top |
| Raised meadow beds, stone retaining walls, copings | conforms in material, with thin pale copings visible. The bed outline deviates (F3), and the perimeter is a heavy plinth (F4). | meadow_beds, aerial, rear_north |
| Upper terrace | conforms: pale concrete. Its back face is coursed stone. | cheek_walls, rear_north |
| Stage platform and curved fascia | conforms: dark, gently convex front edge | stage_pavilion, cheek_walls, top |
| Pavilion: slat cladding | conforms: mixed widths, depths and a wide tone spread (F6 is polish) | slat_wall, stage_pavilion |
| Pavilion: returns | conforms: slatted side returns with depth | stage_pavilion, light_mast, backstage_door |
| Pavilion: roof slab | conforms: deep, flat, dark slab with overhang | stage_pavilion, front, rear_north |
| Pavilion: loudspeakers | conforms: one near each end of the back wall | stage_pavilion, front |
| Pavilion: backstage door | conforms: panelled door in a recessed dark frame in the east return. The threshold is hidden by the cheek wall. | backstage_door |
| Stage side steps | not visible: no legible steps between the cheek walls and the pavilion in any view | top, cheek_walls |
| Floodlight masts and lamp heads | conforms: two slender dark masts just outside the pavilion, six stacked heads each | light_mast, front, rear_north |
| Trees and meadow | conforms in kind (shade trees; meadow abstracted as clumps). The canopy is sparse near the plaza (F7). | aerial, top, meadow_beds |
| Lawn and context | conforms as a teaching assumption: a lawn strip and tree belt at the rear, with a heavy plinth (F4) | rear, rear_side, aerial |
| Materials hierarchy | **deviates** at the bowl: stone riser, concrete tread and concrete terrace collapse to stone riser and terrace (F2). Elsewhere it conforms (pale slabs, grey bollards, warm stone, timber, dark roof and fascia). | seating_tiers, front, aerial |
| Grounding | conforms: no floating or below-grade parts seen. Bollards, mast bases, walls and stage all sit on their surfaces. | bollard_grid, light_mast, cheek_walls, paving_drain |

## 4. Camera validity

- All 18 renders are legible. In none is the target occluded or the asset clipped in a way that invalidates the view.
- front: horizon and pavilion position match the locked front. The bowl still reads as a stacked wall, but that is caused by the step geometry (F2), not by the camera.
- left_side, right_side, rear: valid, but the asset is small in frame (F9, P2).
- meadow_beds: a foreground tree trunk and canopy take about 40% of the frame. The bed wall and meadow are still legible, so the view is valid.
- slat_wall and paving_drain are close-ups and valid. stage_pavilion is valid.
- Generic building roles (facade_close, architecture_close, glass_close) are absent and not applicable (F10).

## 5. Previous-version (v001) findings: resolved in the pixels?

1. **P0, bowl curved the wrong way: RESOLVED.** In top, aerial and front_corner, every tier edge is concave to the plaza (∩), matching top.jpg and oblique.jpg. The plaza pushes into the bowl on the centre line, the tier ends sweep south toward the viewer, the tiers lengthen as they rise (aerial: foot about 960 px to top tier about 1340 px), and the bed walls along the tier ends diverge northward. The stage front stays convex toward the plaza.
2. **P1, risers smooth and low-contrast with no stacked stone: PARTIALLY RESOLVED.** The riser faces now carry legible stacked ledgestone in three warm-grey tones with dark bed and head joints (seating_tiers, front). However, the steps are no longer legible: the treads are the same warm stone, the goings are about 0.18 m, and there are no nosing lines. The tiers now read as coursed stone walls instead of a plain concrete stair, and the stone-and-concrete hierarchy is still wrong. This is carried forward as new P1 F2.
3. **P1, bollards about 3:1: RESOLVED.** The bollards are short drums of about 1.35 to 1.5:1 with a slightly smaller cap (bollard_grid, front, seating_tiers), consistent with the about 1.4:1 in front.png. The 3 m grid, 5 rows and alternate-row offset are kept (top zoom).
4. **P1, cheek walls missing: RESOLVED.** Stacked-stone cheek walls with concrete copings stand at both stage ends and step up toward the back (cheek_walls, light_mast, front, top). The upper terrace is no longer open beside the stage. The stage side steps between the walls and the pavilion are not legible in any view.

Cheap P2 claims:
- Wider slat tone spread: **resolved.** slat_wall shows light, mid and dark timber with depth shadows.
- Flush, slotted floor drains: **resolved.** paving_drain shows flush slotted plates, though they are double rectangles (F8).
- Two stray benches removed: **resolved.** No benches are visible in top, aerial or rear_side.
- Front camera raised and pulled back: **partially resolved.** The framing now matches the source horizon, but the bowl still reads as a wall because of F2.
- Back face of the upper terrace in coursed stone: **resolved.** rear_north and rear show coursed stone.

Elements v001 got right that must still hold:
- Flared, bollard-gridded plaza of square slabs with 6 m joints: holds, but the flare is wrong (F3).
- Three tiers: holds. Three steps per tier: not legible (F2).
- Slatted, open-fronted pavilion under a deep dark roof with loudspeakers: holds, but under-scaled (F1).
- Two floodlight masts with six stacked heads: holds.
- Raised stone-walled meadow beds with shade trees: holds, though the outline deviates (F3) and the plinth is heavy (F4).
- Meadow and lawn beyond: holds.
