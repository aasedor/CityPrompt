# CityPrompt building-conditioning trial — findings

## Outcome

Architectural clay is a strong default conditioning format for accurate final stills, provided "clay" means the complete identity-bearing architecture rather than primitive massing. In this single-call trial it preserved every critical building system visible from the locked camera and reached nearly the same photographic quality as the full RLASM lane. The coloured polygon produced an attractive image but redesigned the building.

This is a one-building, one-call-per-lane pilot. It is directional evidence, not a statistical benchmark.

## Locked trial

- Approved keeper: `rlasm-calgary-inner-city-bungalow-v020`.
- Same 54 mm `camera_front_corner_60`, site, lighting, 4:3 target, source board, measured brief, and prohibitions.
- Three native image-generation calls total, one per lane, with no retries and no cross-lane result conditioning.
- Critical identity locks: camera side, footprint/massing, broad hip and front roof junction, upper front gable/picture-window bay, porch location and construction, right roof-plane dormer, left chimney, side-window cadence, and source material-role palette.

## Direct comparison

| Criterion | Coloured polygon | Architectural clay | Full RLASM |
|---|---|---|---|
| Photographic finish | Excellent | Excellent | Excellent |
| Camera/orientation | Failed: output moved to the opposite front side and reframed | Strong: same side and closely matched composition, with a modest recrop | Strongest: closest to locked camera and framing |
| Footprint and gross mass | Only loosely inferable; visually plausible rather than provable | Preserved | Preserved |
| Roof graph | Reinterpreted into a more gable-dominant house | Preserved broad hip, front junction, and roof hierarchy | Preserved most exactly |
| Signature dormer/chimney | Right roof-plane dormer omitted; left chimney retained | Both retained in the correct roles | Both retained in the correct roles |
| Porch/opening cadence | Porch idea retained, but facade and side openings were redesigned | Construction and cadence largely retained | Best retention of construction and cadence |
| Material identity | Convincing source-like palette, but freely assigned to invented geometry | Convincing palette; small material-topology drift at the dormer and fine trim | Best material-role placement and least ambiguity |
| Expected video stability | Low: shape and camera can mutate between frames | Medium-high geometry stability; materials still need a persistent appearance lock | Highest: geometry and material roles both have deterministic anchors |

## What the images show

The polygon result is arguably the prettiest isolated photograph, but it is not the approved design. It flips the useful side of the camera, omits the required side dormer, rewrites the roof composition, and invents a new facade/side-opening pattern. The reference board was enough to recover the general Craftsman-bungalow language and palette, but not the exact building.

The clay result keeps the broad hip, both gabled projections, porch on brick piers, steps, right roof dormer, left chimney, and visible side-window rhythm. The model successfully supplied brick, stucco, shingles, timber, glazing, planting, and neighbourhood context. Its main residual risk is material topology: without material-role cues, it may choose the right materials but put them on slightly different components, as seen in the dormer treatment and some fine trim.

The full RLASM result gives the model the fewest architectural decisions to make. It keeps both geometry and the brick/stucco/timber/shingle assignment map, then spends its generative capacity on material micro-detail, foliage, atmosphere, and context. It remains the safest choice for approval views, close-ups, and shots that must match one another.

## Recommendation

Use a three-tier strategy:

1. **Coloured polygons for planning and early concepts.** They are fast and flexible, but should be labelled "conceptual" whenever exact design identity matters.
2. **Architectural clay as the default high-quality render conditioner.** The clay asset must own footprint, height, floor/bay rhythm, roof topology, eaves, dormers/chimneys, physical openings and reveals, porch/balcony structure, stairs, and ground contact. Let the image model own material finish, weathering, glazing response, planting, lighting, and background context.
3. **Full RLASM for locked design and video.** Use it for approval-grade stills, close architectural views, multi-shot sequences, and any video where material placement and temporal continuity matter.

For video, do not independently ask the model to re-materialize raw clay on every frame. Keep the deterministic 3D geometry and camera path, generate or approve one persistent material/appearance target, and condition all frames or keyframes against it. Otherwise the clay lane's remaining material-topology freedom can turn into temporal flicker even when the shape stays stable.

## Important definition

The successful middle lane is **architectural clay**, not generic massing. If windows are decals, roof intersections are approximate, porch members are absent, or dormers/chimneys are only prompt text, the method collapses toward the polygon lane and loses the accuracy advantage demonstrated here.
