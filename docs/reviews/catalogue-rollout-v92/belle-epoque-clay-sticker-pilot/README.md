# Belle Epoque Grand Magasin clay + sticker pilot

Status: **visual catalogue gate rejected (73/100)**. This pilot is published as evidence and methodology work, not as a catalogue keeper.

## Outcome

The two-agent split worked at the geometry boundary:

- the Geometry Agent produced an immutable, audited clay shell;
- the Architect Agent approved that clay shell before any sticker work;
- the Sticker Agent registered 38 native surface carriers and 56 reciprocal seams against the clay lock;
- the compiler attached textures to the audited mesh faces instead of adding shallow facade boxes;
- the final Architect Agent review rejected the integrated result because compound-surface registration is not yet catalogue quality.

The best result is the facade itself: the iron, stone and glazing retain the fidelity of the generated sticker imagery. The failure is at transitions between carriers: roof cornices, rounded pavilion joins, dome drums, dormer returns and the entrance canopy.

## Review images

`comparison-board.jpg` is arranged reference left / render right:

1. street reference and archetype-match render;
2. oblique reference and front-corner render;
3. aerial reference and roof-audit render.

`clay-board.jpg` records the Architect-approved untextured geometry checkpoint. The individual reference, clay and final views are included beside the boards for full-resolution review.

## Audited geometry checkpoint

- Clay SHA-256: `4a0c2c6514d0a546d3a3154b6766d40797c88b8b3ffb7ce4e1523831be73b815`
- Geometry tests: 18/18 passed
- Artifact gates: 27/27 passed
- Roof manifold errors: 0
- Roof crossings/winding failures: 0
- Courtyard cap faces: 0
- Courtyard overlap: 0 m2
- Open courtyard area: 149.237 m2
- Dormer rhythm: 3 front, 3 rear, 2 left, 2 right
- Entrance: 5.4 m wide, 4.2 m deep tunnel, 4.0 m canopy projection

This is a select-and-place landmark with predetermined 36 m x 34 m dimensions. It is intentionally not a polygon-fit LEGO building.

## Final hard stops

1. Pale roof-eave and upper-cornice carriers remain visually exposed.
2. Roofline/corner stickers compress, smear or break registration at compound joins.
3. The oversized canopy and blank support conceal the entrance instead of reading as a glazed, navigable corner portal.
4. Dome glazing is too dark/opaque and dormer side returns remain weak.
5. The assembled GLB is 24,824,520 bytes, above the 8 MB catalogue budget.

The next method revision should not regenerate facade art. It should replace broad compound carriers with topology-aware patches, add seam-safe trim materials, reconstruct the entrance as a dedicated architectural assembly, and package shared atlases/KTX2 before another catalogue gate.

No paid API calls were used for this pilot.
