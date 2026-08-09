# Three-building V84 surface-story pilot

Status: **bounded generalization is promising but mixed**. Italian Portici is
a keeper candidate; the courthouse is a surface-method keeper with unresolved
archetype geometry; the warehouse remains provisional and fails the stricter
export-parity gate.

This batch applies the V83 exportable surface workflow to three controlled V78
baselines: Neoclassical Courthouse, Italian Portici and Romanesque Warehouse.
The massing, facade sheets and cameras were held constant so the comparison
isolates material construction role, baked PBR delivery and export behavior.

## Results

| Building | Visual status | Surface audit | GLB foreground parity | Triangles | GLB |
| --- | --- | ---: | ---: | ---: | ---: |
| Neoclassical Courthouse | Surface keeper; archetype provisional | Pass | 95.76% | 31,248 | 3.91 MB |
| Italian Portici | Keeper candidate | Pass | 97.53% | 12,580 | 2.69 MB |
| Romanesque Warehouse | Visual provisional; export parity fail | Fail | 93.26% | 11,984 | 2.79 MB |

All three production preflights and structural GLB validations pass. The
surface audit proves that the three required materials carry albedo,
roughness and normal maps. The parity gate now measures only alpha-masked
building pixels; background pixels can no longer inflate the score.

The 1024 px baked sets keep every assembled GLB below the 8 MB delivery target
without an obvious loss in the reviewed presentation renders. This resolves
the 13.9 MB warning from the V83 2048 px hero pilot.

## What improved

- The courthouse roof now uses a verdigris standing-seam source rather than a
  generic brown copper field. Granite wall and carved-detail zones are quiet
  and materially related.
- The portici roof now reads as overlapping pantiles rather than wall brick.
  Its stone arcade, ochre upper wall and terracotta roof form the strongest
  material hierarchy in this batch.
- The warehouse uses a darker red-brown wall brick, real brownstone source and
  low-contrast built-up membrane instead of recolored near-neighbours.

## What is still missing

- Courthouse likeness is limited by fixed geometry: sculpted pediment relief,
  Corinthian capitals, portico depth and finer cornice hierarchy.
- Portici still needs a proper projecting eave and a deeper, occupied shop
  layer behind the arcade.
- Warehouse loading arches remain too regular and applied-looking compared
  with the exact archetype. Its source-to-GLB facade shift also exceeds the
  new five-percent foreground error limit, so catalogue release stays blocked.

These are not requests for more texture noise. They are fixed identity,
opening-section and export-material tasks.

## New methodology rules

1. A source texture must match construction role and pattern, not just material
   family or colour. Pantile, wall brick, standing seam, ashlar and roof
   membrane are separate source roles.
2. Every required baked material declares that role in the production
   contract; preflight fails when a role is absent.
3. Neutral source-versus-GLB parity is scored on the building foreground with
   a transparent studio render. A shared background cannot hide material loss.
4. Surface approval and archetype-identity approval remain independent.

## Boards

- `01-archetype-baseline-v84.png` - exact reference, V78 baseline and V84.
- `02-roof-baseline-v84.png` - exact aerial evidence and both roof audits.
- `03-neutral-glb-parity-v84.png` - source, re-imported GLB and difference map.

## Next bounded step

Keep the portici as the next catalogue candidate. Add one fixed eave/shop-depth
pass, then diagnose the warehouse facade export shift before changing its
geometry. The courthouse should receive a small classical ornament kit; its
approved granite/copper surface system should remain unchanged.
