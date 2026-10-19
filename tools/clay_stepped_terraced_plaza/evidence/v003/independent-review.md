# Independent holistic review: clay-stepped-terraced-plaza v003 (RLASM v6.1)

Reviewer: independent; not the builder. I judged rendered pixels against the locked sources only (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders and the 4 phone boards at full resolution. I made zoom crops only in a new folder: `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indrev-crops-a72424ec/`. I ignored the builder's metadata, counts and notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: v003 fixes the strip plan, terrace rhythm, stair offset, chapel position, belfry topology and west-parapet contact. It still has three P1 defects. Both bougainvilleas still read as clusters of separate faceted balloons. The foot of the strip does not splay west the way the top source shows. The pergola has moved into the east seating terraces and spans the parapet and the side stair.

Counts: P0 = 0, P1 = 3, P2 = 7

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | architecture_close, front, front_corner, aerial, side_stair, top | **Bougainvillea still reads as balloon clusters, with no drape.**<br>West plant: about 60 separate faceted magenta and green ovoids, each roughly 0.4-0.6 m. They hang as a vertical column on a straight, bare, leaning dowel at the house corner. A loose spray of separate ovoids floats on the house's blank south wall, with wall visible between them. Two blobs float detached near the top left (architecture_close, top-left). Nothing spreads over the roof edge or across the head of the door and windows. In the source, the plant is one dense canopy that drapes over the roof parapet and spreads across the top of the facade before falling down the corner.<br>The dowel's foot lands in front of the door's left jamb and overlaps the opening (architecture_close x≈790-830, y 540-1050).<br>East plant: a heap of the same ovoids straddles the parapet coping across about one terrace (front x 1215-1310, y 600-690; side_stair). The source cascade runs about four terraces down the parapet. | The scatter-sphere foliage primitive was kept and only its placement changed. The spheres are too large and too sparse, and there is no roof-edge canopy mass and no continuous hanging curtain. The trunk is one straight cylinder placed against the door reveal. | Build each plant as one or two continuous canopy masses: a merged or displaced blob shell, or many small clusters (≤0.15 m) packed with no wall showing through.<br>West: a roof-edge canopy spanning about 40% of the east facade above the door and windows, falling down the south-east corner. Remove the free spray from the blank south wall. Move the trunk off the door reveal so it stands clear of the jamb.<br>East: extend the cascade down the parapet over about four terraces. |
| 2 | P1 | top, aerial, front_corner | **The foot of the strip does not splay west.** In the render the low west parapet (pots) runs exactly on the line of the bougainvillea house's east face (top render x≈570; zoom crop: pots at the house-face line). The lowest west terraces are no wider than the upper ones. The diagonal stair is reduced to a short wedge squeezed between a new south-west house and the parapet.<br>In the top source the low west parapet is set about 20-30% of the strip width west of the house face and slants south-west (source top x≈405-440 against the house face x≈495). The lowest three or four west terraces widen accordingly. A long diagonal stair runs outside the parapet from the plaza up to the alley west of the bougainvillea house. | The lower west terraces were built as straight extensions of the house-line strip. A house block was placed where the source's diagonal stair and widened terraces are. | Extend the lowest three or four west terraces about 4-5 m west of the house line. Set the low parapet on that new edge with a slight south-west slant. Run the diagonal stair along the outside of the parapet from the plaza to the alley west of the bougainvillea house. Move or shrink the south-west house so that it sits beyond the diagonal stair. |
| 3 | P1 | front, facade_close, parapet_pots, side_stair, top | **The pergola stands in the east seating terraces.** Its two timber posts stand on the east terrace treads inside the parapet, among the geranium pots: parapet_pots post at x≈930-980; side_stair posts at x≈565 and x≈600 down to the terraces. Its slats span over the parapet and the side stair.<br>A crisp black void sits at the head of a post (side_stair ≈(595,460); front ≈(1070,490)).<br>In the source (oblique x 1020-1190, y 395-440; top x 850-980, y 505-565) the pergola belongs to an east house terrace beyond the side stair. It does not stand in the public stair-plaza. | The pergola was anchored to the strip's east edge instead of the east house. The beam end leaves the post cap open, or a face is missing, at the junction. | Move the pergola onto the upper terrace of the east house, east of the side stair, with posts on that house's terrace. Keep the side stair and the east seating terraces clear. Close or cap the post-beam junction so no black void remains. |
| 4 | P2 | front_corner, aerial, left_side | The belfry now has the right topology: two stages, cut round arches, solid spandrels, a narrower upper stage and a bell in the lower stage (visible in left_side). However, the openings are small punched arches, about 40% of the face width. The source's lower arch spans about 75% of the face. The upper stage is a square box with one arch per face, where the source has an octagonal lantern of tall narrow arches. The tower is a tall freestanding shaft with a ground-floor door, so it reads closer to a campanile than to the compact source bell-gable. | Simplified stage proportions. | Widen the lower arch to about 70-75% of the face. Make the upper stage an octagonal arcade of six to eight narrow arches. Shorten the plain shaft. |
| 5 | P2 | parapet_pots, front, facade_close | Geranium pots are taller than a terrace riser, about 1.5 times the source scale. The flowers are red cubes on a green dome and read like gift bows. Two extra pots stand on the plaza floor at the stair foot; no source shows them. | Pot asset scale and form. | Scale pots to about 0.35-0.4 m. Use smaller, clustered red flower heads. Remove the two plaza pots. |
| 6 | P2 | top, front_corner, chapel_top | The chapel is a small cube with a dome. The source chapel is a larger church body with a nave and side volumes, about twice the plan footprint. The drum has no arched windows. | Simplified chapel massing. | Enlarge the chapel body and add a nave volume. Add four to eight arched drum windows. |
| 7 | P2 | front, seating_terraces, aerial | The material hierarchy is weak. The pale cream platforms are only slightly darker than the white risers. The source stone paving is a clearly warmer, darker tan-grey. | Paving colour too light. | Darken and warm the platform and landing colour to the source stone tone, keeping the risers white. |
| 8 | P2 | interior | The door leaf is narrower than its opening. A sliver of the exterior scene shows along the right jamb (x≈930-940). | Leaf width under the reveal width. | Size the leaf to the opening, or add a stop or frame. |
| 9 | P2 | rear_north | About half the frame is a blank roof/podium volume. The stair-plaza drops out of sight below the edge of the north plaza, so the view shows little of the target. | Camera height and position. | Raise the camera or move it east of the chapel podium so that it looks down the strip. |
| 10 | P2 | glass_close | An unexplained blue rectangle floats behind the lower-right pane. | Interior element visible through the glazing. | Remove it or align it to an interior wall. |

(P2 rows: 4-10 = 7. P1 rows: 1-3 = 3. P0 rows: none.)

## 3. Source conformance checklist

| item | status | view used | note |
|---|---|---|---|
| Plan and proportions | **deviates** | top, aerial | The main strip now conforms: about 1.8-1.9 length to width including the side stair, against the source's about 1.85-2.2. The houses sit tight to both edges, there is a north paved square and a lower plaza. The west foot splay is missing (F2). |
| Central stair: steps, landings, handrails | conforms | central_stair, facade_close, top | The stair is narrow, with flights between landings at each terrace level. A full-width flight leads onto a mid cross-landing, and above it the stair steps east. Two metal handrails with posts break at the landings. |
| Terraces: risers, seats, paving | conforms (P2 tone) | aerial, stair_foot crop, seating_terraces | There are about 11-12 levels, each with a white riser, a seating step and a deep platform. The paving tone is too pale (F7). |
| East parapet and pots | conforms (P2 pot scale) | side_stair, parapet_pots | A continuous stepped white parapet with coping runs along the east terraces. Pots sit on the terraces against its inner face. The pergola intrudes (F3). |
| Side stair | conforms | side_stair, top | A narrow straight flight runs between the parapet and the east houses. The pergola spans over it (F3). |
| West parapet | deviates (position) | aerial, top, front_corner | Low and white, with pots and clean contact; no black voids. It sits on the house line instead of being splayed west (F2). |
| Flanking houses: doors, windows, stepped heights | conforms | front_corner, left_side, right_side, glass_close | White cubes, each spanning about two terraces and stepping up. Blue doors and blue-framed windows have visible reveals and depth. The east houses include a blue-railed balcony. |
| Bougainvillea | **deviates** | architecture_close, front, side_stair | Still balloon clusters with no drape (F1). |
| Chapel and dome | conforms (P2 size) | top, front_corner, front | A blue dome on a drum and podium, west of and behind the upper west houses. The body is undersized (F6). |
| Belfry and cupola | conforms (P2 proportions) | front_corner, aerial, left_side | White, two-stage, with a blue cupola, at the foot on the east. The openings are undersized (F4). |
| Lower plaza | conforms | front, front_corner, top | A level paved plaza with a grid pattern across the foot. Extra pots stand on it (F5). |
| Materials hierarchy | deviates (P2) | front, seating_terraces | The white render, blue trim and terracotta read correctly. The stone paving is too close to the white (F7). |

## 4. Camera validity

- **front, front_corner, aerial, top, left_side, right_side, rear_side:** valid; the whole asset is in frame and legible.
- **rear:** valid as a coherence view, since the north hillside solids are blank by design. Nothing is clipped.
- **facade_close, central_stair, seating_terraces, parapet_pots, side_stair:** valid; each target is unoccluded.
- **architecture_close, glass_close, interior:** valid; the target is legible.
- **chapel_top:** valid. The dome is legible, though about 60% of the frame is blank roof.
- **rear_north:** weak (F9, P2). About half the frame is a blank volume, and the stair-plaza is hidden below the edge of the north plaza.
- No view clips the asset or makes the named target illegible enough to rise to P0.

## 5. Previous-version (v002) findings: resolved in the pixels?

1. **Both bougainvilleas read as balloon clusters with no drape or green; the west one sits over a blank setback wall.** **Not resolved.**
   - Green ovoids have been added.
   - The west plant now has a trunk at the south-east corner beside the door and windows.
   - Both plants are still separate faceted balloons, with no roof-edge canopy and no continuous drape.
   - A loose spray still floats on the blank south wall.
   - The trunk now overlaps the door jamb (F1).
2. **Black voids where the low west parapet meets the terrace riser.** **Resolved.** The parapet face is proud and starts at the riser, with clean contact in aerial and front_corner. A new, unrelated black void appears at the pergola post head (F3).
3. **The belfry stage is a rectangular slot with thin arch shells and open spandrels.** **Resolved.**
   - The two stages have cut round arches in solid walls, with full-depth spandrels.
   - The upper stage is narrower and the bell is in the lower stage.
   - Remaining proportion issues are P2 (F4).
4. **Eight uniform deep levels per side against about twelve shallower ones, no mid cross-landing or stair offset, the strip too narrow and long.** **Resolved.**
   - There are about 11-12 shallower levels.
   - A full-width flight leads onto a mid cross-landing, and the stair steps east above it.
   - The strip's proportion now matches the source.
   - A separate plan deviation at the foot remains (F2, new).
5. **The chapel sits inside the strip on the top landing.** **Resolved.** It now stands on a podium west of and behind the upper west houses (top, front_corner). Its size is P2 (F6).
