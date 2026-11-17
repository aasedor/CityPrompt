# Painted road barriers for Add details: eight original murals

## Scope

Add eight versions of the 3 m concrete road barrier with a mural painted on
both long faces, for scenes that show painted barriers protecting a patio, a
bike lane or a work zone. They extend `calgary-details-v1` (now 113 objects,
IDs prefixed `detail-yyc-`) and sit in **Traffic & safety** beside the plain
[concrete barrier](LOCAL_DETAILS_BATCH3_2026-11-16.md). Searching `mural` lists
them.

**The designs are original.** They are flat-colour compositions made for this
catalogue on local themes. None reproduces a real mural or an artist's work,
and none carries a program name, logo or wording. Real murals belong to their
artists; adding one would need the artwork and the artist's permission, and
image textures, which this kit does not use.

## New choices

| Item | Design | Triangles |
|---|---|---:|
| Mural barrier · Foothills sunrise | Sun rising behind snow-capped peaks, green foothills and gold prairie | 2,730 |
| Mural barrier · Chinook arch | An arch of sunset cloud over a dark range, with a low sun | 2,436 |
| Mural barrier · River ribbons | Seven flowing bands of river blue, white and green | 1,996 |
| Mural barrier · Triangle mosaic | A bright mosaic of irregular triangles | 1,000 |
| Mural barrier · Chevrons | Bold zigzag bands in navy, white, pink and yellow | 1,036 |
| Mural barrier · Prairie quilt | Patchwork blocks in barn red, mustard, cream, denim and sage | 900 |
| Mural barrier · Aspen grove | White aspen trunks against blue sky under a gold canopy | 1,182 |
| Mural barrier · Confetti | Bright dots on deep teal | 1,460 |

Every one is 3.0 × 0.6 × 0.8 m, exactly the footprint of the plain barrier, so
painted and plain sections can be mixed in one row. The scenic designs repeat
every 3 m, so the skyline of one section meets the next.

## Method

A mural is described in flat coordinates: 0 to 3 m along the barrier and 0 to
0.76 m up the face, measured from the top of the unpainted toe. Shapes are
convex polygons that **tile the face without overlapping**: stacked colour
bands split by curves, triangles on a shared grid, or quilt blocks. Each shape
is then clipped at the bend in the barrier's profile and folded onto the lower
and upper slopes. Because the mural replaces the concrete face rather than
sitting on it, no painted surface lies on top of another and nothing can
flicker at a distance. Only a few accents sit 4 mm proud: the suns, the aspen
bark marks and the confetti dots, which are placed so they never overlap each
other.

Each face reads left to right when you stand in front of it. The top is painted
in one colour from the mural; the toe, ends and underside stay concrete, and
the lifting slots are kept.

The files follow the kit convention: linear vertex colours, flat normals, one
matte mesh, no textures. The eight total 1,461,888 bytes and 12,740 triangles.
The 105 earlier models are byte-identical.

## Verification

- Every mural was rendered at eye level, oblique, close up and at card size and
  reviewed: [eye level](calgary-details-v1/mural-barriers-eye-level.jpg),
  [oblique](calgary-details-v1/mural-barriers-oblique.jpg),
  [close up](calgary-details-v1/mural-barriers-close.jpg),
  [catalogue cards](calgary-details-v1/mural-barriers-cards.jpg). Edges are
  crisp and the fold at the bend is clean. Agent review passed; independent
  human visual acceptance is open.
- Tools pytest: the Calgary kit rebuilds all 113 objects to byte-identical
  registry rows with a hash-locked card each.
- A frontend test requires all eight murals to share the plain barrier's
  dimensions exactly and to state that the design is original.
- `npx vitest run`: 512 files and 4,542 tests passed. Hosted-asset tests pass
  for all 198 local rows. Backend detail tests pass with 353 extras.
- Runtime asset manifest regenerated: 5,905 required files (+16).
- Production build with CI settings, then `check-budget`: 8,440.8 KB of
  8,448 KB.

Not done here: placing them on the live map, which needs a real map key.
