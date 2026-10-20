# Independent holistic review: clay-market-square v004 (RLASM v6.1 architectural clay)

Reviewer: independent; not the builder. Judged only rendered pixels against the locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). I opened all 18 renders, the 3 sources and the 4 phone boards at full resolution. Zoomed crops and per-column pixel traces were written only to the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/crops-mktsq-v004-rv26131074/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the plaza flare and the bollard and paving grammar now hold, but the seating bowl still does not read as the source's nested stone seating arcs. The top tier is a shallow W (gull-wing) whose outer ends turn north, and the pale walks now dominate the stone bands, which inverts the source's band-to-walk proportion.

Counts: P0 = 0, P1 = 2, P2 = 6

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top, aerial, front_corner, front, left_side, right_side; phone-01 | **The top tier still reverses its bend, and the wings beside the stage are missing.** In `top` the foot and middle bands are clean concentric arcs (traced band-3 top edge: y = 476 px on the axis, 495 px at x = 500 and 490 px at x = 940). Past about 14 m off the axis the top band turns back north (483 px at x = 980, 472 px at x = 1020, about 467 to 470 px at both bowl-end walls). The band is therefore a shallow W: the centre is north, it dips south at about ±14 m, and the ends are north again. In `aerial` and `front_corner` this reads as an undulating ribbon or gull-wing, not nested arcs. Broad empty pale terrace wedges sit between the curled ends, the diagonal high-bed fronts and the stage. The cheek walls are short north–south walls on a flat terrace, and the stage sits in a rectangular slot between the high beds. In the source (`oblique`, `top`, `front`), every tier line is concave to the plaza, and the outer ends of every line are its southmost points. In front of the stage the source shows only two stepped bands plus terraces; the third tier appears only as stepped seating wings that rise from the outer ends north to the stacked-stone cheek walls on each side of the stage (left wing in `oblique` runs from about (180,393) up to (407,333); in `top` from about (317,340) up to (517,273)). The stage platform occupies the middle of that third tier. In the render's `front`, the source's stepped wings flanking the stage are replaced by flat terrace, low walls and meadow at stage level. | The third band is run as a continuous arc in front of the stage. Because the 73.5 m radius is too flat to wrap beside the stage, a northward "curl" offset was added beyond 14 m, and that offset creates an inflection. The builder's claim that "no line reverses its bend" is false at the curl. | Delete the north curl: every tier line must remain one monotonic arc concave to the plaza, with its outer ends southmost. Make tier 3 concentric wings that start at the stage cheek walls and descend outward to the bowl-end walls, replacing the pale terrace wedges with those stepped wings. Either stop tier 3 at the cheek walls, as in the source, or pass it behind the stage platform. Run the cheek walls diagonally along the inner, upper ends of the wings, stepping down outward. Re-verify in `top` and `aerial` that no traced tier edge has a local southmost point off the axis. |
| 2 | P1 | top, aerial, front_corner, seating_tiers, stage_pavilion; phone-01 | **The walk-to-band proportion is now inverted relative to the source, and the bands are stair-scale rather than seating-scale.** In `top` each warm band is about 9 to 10 px deep (3 steps of 0.45 m) and each pale walk about 38 px, so walks are about 3 to 4 times the band depth. `aerial` and `front_corner` read as a large pale ramp crossed by three thin stone stripes, so pale concrete dominates the bowl. In the source the stone seating bands dominate. At the centre of `top` (3× crop), the foot band is about 120 px deep, the terrace between bands about 35 px, band 2 about 85 px, and the front-of-stage terrace about 35 px. At the centre of `oblique`, the foot band is about 130 px, the terrace about 25 px and band 2 about 95 px. In both, each band is about 2.5 to 4 times the depth of a walk, and each step is a deep seat step (about 3 to 4 per band). The three bands are now distinct, so the v003 "one continuous flight" defect is gone, but the correction overshoots. | The v003 instruction, "terraces wider than each band", was applied literally: walks 2.3 to 2.8 m, steps of 0.45 m treads. The source pixels show deep seat-steps and walks narrower than the bands. | Deepen each band to source seating proportion: 3 seat steps of about 0.40 to 0.45 m rise and 0.8 to 0.9 m tread, so a band about 2.5 m deep. Cut each walk to about 0.9 to 1.2 m, roughly 0.35 to 0.45 of the band depth, and keep the front-of-stage terrace about the same. Keep the strong nosing shadow line and the stone riser so the three bands stay distinct at that proportion. Re-check that `top` reads as wide warm bands separated by narrow pale walks. |
| 3 | P2 | left_side, right_side, rear, rear_side, rear_north, meadow_beds | The high beds and the north edge stand on sheer stacked-stone walls about 2.5 to 3 m high above the outer lawn, so the bowl reads as a raised podium in the side and rear views. In the source, the meadow and lawn beyond the cheek walls and pavilion run at about stage level (`front`, `oblique`). | The upper terrace level is extruded to the site boundary instead of meeting grade. | Grade the outer and north ground up to the upper-terrace level, or batter or step the perimeter walls down. These faces are not shown in the source; coherence only. |
| 4 | P2 | top, meadow_beds | The low beds are small triangles whose front wall ends at the plaza corner. In the source `top`, the bed front wall continues outward past the plaza corner to a far outer corner, with a lawn wedge below it. | The bed polygon is clipped at the plaza edge. | Extend the low-bed front wall outward past the plaza corner, then return it north. |
| 5 | P2 | front | The bowl foot spans almost the full frame width (about 10 to 1430 px of 1440). The raised meadow beds flanking the foot in the source `front` are out of frame, and the pavilion-to-foot apparent ratio is about 0.36 against about 0.55 in the source. | Camera too close or too wide for the matched role. | Pull the front camera back or narrow the lens until the bed walls flanking the foot are in frame, as in the source. |
| 6 | P2 | light_mast | The mast base is hidden behind a wall at the bottom edge, so ground contact cannot be seen in this view (it is visible in `aerial`). | Low camera framing. | Lower the target or raise the camera so the base plate is in frame. |
| 7 | P2 | rear_side | The asset fills only about 40% of the frame width and is small, though legible. | Long framing distance. | Tighten the framing. |
| 8 | P2 | renders folder | The brief's template names `facade_close`, `architecture_close` and `glass_close`, but they are not rendered. There are 18 views in total, as the brief states, and they are not applicable to an open space. | Template carry-over. | None needed; note only. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Plan: plaza flare | conforms | top, aerial, phone-01 | Continuous trapezoid flaring to the south edge, with lawn wedges outside both edges. The left edge runs from about (370,650) to (225,920) in `top`. |
| Plan: bowl arcs and chord | deviates | top, aerial, front_corner | The foot and middle arcs are concentric and concave. Tier 3 has a W inflection and northward ends (P1-1). Foot chord about 36 m (480 px at about 13 px/m). |
| Plan: stage on axis | conforms | top, front | Centred on the axis. |
| Paving: square slabs, stronger 6 m joints | conforms | top, paving_drain, bollard_grid | 1.5 m slabs; stronger joint every fourth line. |
| Bollard grid: rows, spacing, offset, size | conforms | top (crop), bollard_grid, front | 5 rows; about 3.0 m within each row; alternate rows half-offset; rows lengthen southward (about 15, 18, 21, 22 and 23 bollards). Stubby octagonal drums. Rows are about 4.5 m apart, which matches the source's wider row spacing. |
| Floor drains | conforms | paving_drain, top | Single square slotted grates, flush. |
| Seating tiers: count | deviates | front, top, oblique comparison | Three full bands in front of the stage. The source shows two in front of the stage, with the third as wings beside the stage (P1-1). |
| Seating tiers: steps, stone risers, treads | deviates | seating_tiers, front, stage_pavilion | Three steps per band. Coursed ledgestone risers with dark bed and head joints, and pale treads with a nosing line. Steps are stair-scale rather than seat-scale (P1-2). |
| Seating tiers: terraces | deviates | top, aerial | Walks are 3 to 4 times the band depth; the source has walks narrower than the bands (P1-2). |
| Cheek walls | deviates (partial) | cheek_walls, aerial, front | Stacked-stone cheek walls at both stage ends, stepping in height. They stand on a flat terrace instead of stepping up along the seating wings as in the source. |
| Raised meadow beds, stone retaining walls, copings | conforms (P2 notes) | meadow_beds, left_side, right_side, top | Stacked-stone walls with pale copings and shade trees. The low beds are truncated (P2-4); the high-bed perimeter walls are podium-like (P2-3). |
| Upper terrace | deviates | top, aerial | Large pale wedges beside the stage where the source has stepped wings (P1-1). |
| Stage platform and curved fascia | conforms | stage_pavilion, cheek_walls, top | About 27 m, gently curved, with a dark fascia; about 0.75 of the foot chord. |
| Pavilion: slat cladding | conforms | slat_wall, stage_pavilion, rear_north | Vertical slats of mixed widths, depths and three tones. |
| Pavilion: returns | conforms | stage_pavilion, front_corner | Slatted side returns, open front. |
| Pavilion: roof slab | conforms | front, aerial | Flat, dark, overhanging slab; depth proportion is similar to the source. |
| Pavilion: loudspeakers | conforms | stage_pavilion, front | One near each end of the back wall. |
| Pavilion: backstage door | conforms | backstage_door | Panel door in a dark recessed frame with visible jamb depth, in the east return. |
| Floodlight masts and lamp heads | conforms | light_mast, front, aerial | Two slender dark masts, each with 6 stacked heads, just outside the pavilion. |
| Trees and meadow | conforms | aerial, meadow_beds, top | Broad shade trees in the beds; meadow abstracted as clumps. |
| Lawn and context | conforms | top, aerial, rear | Lawn and tree belt beyond (teaching assumption). |
| Materials hierarchy | deviates | aerial, front_corner, top | Pale concrete dominates the bowl over the warm stone seating (P1-2). Elsewhere the source palette is used correctly. |
| Grounding | conforms | all | No floating or below-grade parts. Bollards, beds, masts, pavilion and stage all sit on their surfaces. |

## 4. Camera validity

- No view has its target occluded or illegible, and no asset is clipped in a way that hides identity. No P0 camera defect.
- `front`: valid and legible, but framed too tight for the matched role; the flanking beds are out of frame (P2-5).
- `light_mast`: lamp heads are legible, but the mast base is hidden at the frame edge (P2-6).
- `rear_side`: legible but small in frame (P2-7).
- `slat_wall`: a full-frame close-up of the cladding only. It is valid as a material detail.

## 5. Previous-version findings: resolved in the pixels?

**v003 findings**

1. Bowl not nested concentric arcs (bow-tie; rectangular high beds): **partly resolved, still P1.** The middles are now concave to the plaza, the foot and middle arcs are concentric, and no straight-fronted rectangular bed faces the bowl. The added north curl still gives tier 3 an inflection (W or gull-wing), the ends do not wrap as stepped wings up to the cheek walls, and pale terrace wedges fill the space (P1-1).
2. Three-tier rhythm lost: **resolved as stated, but overcorrected (new P1-2).** Three distinct warm bands separated by pale walks now read clearly in `front`, `top` and `aerial`. The walks are now 3 to 4 times the band depth, the inverse of the source proportion.
3. Plaza not flaring south: **resolved.** The edges flare continuously to the south edge, the lawn wedges are present outside both edges, and the bollard rows lengthen row by row.

**v003 fixes that must hold**

- 27 m curved stage platform with dark fascia, about 0.75 of the foot chord: **holds.**
- 21.6 m slatted pavilion, about 0.6 of the foot chord, with loudspeakers and backstage door: **holds.**
- Legible individual steps with a nosing shadow over each stone riser: **holds** (`seating_tiers`, `front`), though steps are stair-scale (P1-2).
- Bed walls fanning about 22° at the bowl foot: **holds** (`top`).
- Single square drain grates: **holds.**

**v002 fixes**

- Lowest tier concave to the plaza: **holds.**
- Stubby drum bollards on the 3 m grid, five rows, alternate rows offset: **holds.**
- Stacked-stone cheek walls at both stage ends: **holds** (placement deviates per P1-1).

**v001 fix**

- Stacked ledgestone on every riser, with bed and staggered head joints as dark lines: **holds** (`seating_tiers`, `meadow_beds`, `cheek_walls`).

**Earlier-correct items**

- Square slabs with stronger 6 m joints: **holds.**
- Two floodlight masts with stacked lamp heads: **holds.**
- Raised stone-walled meadow beds with shade trees: **holds** (P2 notes).
- Meadow and lawn beyond: **holds.**
