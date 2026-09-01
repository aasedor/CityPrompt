# CityPrompt building-conditioning trial — locked prompts

## Experimental controls

- Subject: approved keeper `rlasm-calgary-inner-city-bungalow-v020`.
- Guide camera: `camera_front_corner_60`, 54 mm, 1280 x 960.
- Image 1: the lane-specific guide.
- Image 2: the same locked source board in every lane.
- Batch: exactly one image-generation call per lane; no automatic retries.
- The target brief below is identical. Only the lane interpretation paragraph changes.

## Common target brief

Create one high-end photorealistic architectural visualization in a landscape 4:3 composition. Show the exact source-locked Calgary inner-city bungalow from the same elevated front-right three-quarter camera, with the same orientation, footprint, scale, and front-side visibility as Image 1. Image 2 is the authoritative identity and appearance reference.

The house is a compact 1.5-storey bungalow with an 11.8 m x 13.6 m main body: a low broad hipped roof; a clipped front gable with paired upper sash above a projecting red-brick picture-window bay; a deep gabled timber entrance porch at the right supported by timber columns on brick piers; one right roof-plane gabled dormer; one substantial left brick chimney; deep eaves; divided-light windows; and a planted front setback. Apply warm pale stucco, source-red brick, grey-brown asphalt shingles, warm-white trim, honey-toned porch timber, pale concrete steps, physically plausible glazing, and subtle occupied interior depth. Add restrained hydrangea and lavender planting plus a believable mature Calgary infill-neighbourhood context beyond the parcel. Use natural late-afternoon daylight, realistic lens response, fine material texture, coherent shadows, and documentary architectural-photography realism.

Do not add a storey, garage, second dormer, second chimney, balcony, roof deck, or contemporary redesign. Do not change the roof graph, porch location, window and door cadence, or building orientation. No people, vehicles in the subject parcel, text, labels, watermark, diagram colors, clay surfaces, or coloured overlay may remain in the final image.

## Lane 1 — coloured polygon

Image 1 is a CityPrompt coloured-polygon guide. It is authoritative only for the exact footprint boundary, site position, orientation, and camera. Replace the red polygon completely with the building described in the common target brief. Infer all vertical architecture from Image 2 and the written brief. The red fill and gold border are semantic markers, never material or colour suggestions.

## Lane 2 — architectural clay

Image 1 is an unmaterialed architectural-clay render. It is authoritative for every visible architectural edge and void. Preserve its silhouette, proportions, roof planes and intersections, eaves, front projection, porch, columns, brick-pier shapes, steps, dormer, chimney, openings, frames, and camera exactly. Change only materials, surface detail, glazing response, lighting, planting, and surrounding context. Do not simplify, move, add, or remove geometry.

## Lane 3 — full RLASM

Image 1 is the approved full RLASM render. It is authoritative for geometry and material-role placement. Preserve its silhouette, proportions, roof graph, porch construction, dormer and chimney positions, opening cadence, trim placement, and camera exactly. Increase photorealism, material micro-detail, planting quality, and contextual integration without redesigning or reinterpreting the house.
