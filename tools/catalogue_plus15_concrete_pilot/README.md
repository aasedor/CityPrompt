# Brutalist Concrete Office Slab with a +15 walkway

RLASM 6.1 architectural clay for the exact variant
`calgary_15_connected_tower` / `brutalist_concrete_slab` (variant 0, "Brutalist
Concrete Office Slab"). This is a **local pilot**. It is not in the catalogue,
not seeded, and not activated. Only a person can activate a clay delivery.

Status of candidate **plus15-brutalist-concrete-office-clay-v002**:

| Checkpoint | Status |
|---|---|
| Deterministic delivery checks | Pass, 75 checks. `evidence/delivery-verification.json` |
| Builder pixel review | Pass, with open notes. `evidence/builder-pixel-review.json` |
| Independent architectural-clay review | In progress. No result yet |
| Runtime integration | NOT REVIEWED. No part of it has been run |
| Publication or activation | Not authorized |

## What the building is

A 1970s precast office block of the kind that carries Calgary's +15 network:
five storeys, 45.0 m across the street front and 40.5 m deep, with a 21.9 m
parapet and a concrete plant penthouse to 28.1 m. A 4.5 m wide enclosed walkway
leaves the east flank at the third storey and runs out 9 m.

| Part | Built as |
|---|---|
| Storeys | Ground storey 5.2 m, four office storeys at 3.9 m |
| Bands | Precast, 1.95 m tall on every side, split by a joint at each 9 m structural line. Each has a 0.52 m cap strip that projects 0.10 m and throws a shadow line |
| Ribbon windows | 1.95 m tall, set 0.5 m behind the cap strip, bronze frames at 1.5 m, bronze glass, a corner post at each corner |
| Ground storey | Granite piers 1.3 m square at 9 m. Five glazed bays to the street, the entrance doors in the second bay from the east corner. Granite infill, a service door and plant louvres on the flanks and rear |
| Roof | Ballasted deck inside a 1.1 m parapet with bronze flashing. Penthouse 22.5 m square, centred, in board-formed panels, with a door and louvre on its east face and an open well in its rear east corner |
| Walkway | Concrete tube with a rounded crown and belly, ribbon glazing both sides, a glazed end |
| Inside | Floors, ceilings with light fittings, columns, enclosed rooms, desks, a lobby with timber panelling, a draught lobby and lift doors, three shop units |

The model is 36,612 triangles in 18 flat-coloured parts, with no textures or
images. Nothing sits below grade, and the entrance threshold is 35 mm above it.

## What it was measured from

Three reference images, locked by hash in `prework-manifest.json`:
`variant_0.png` (street), `variant_0_angle_60.jpg` (oblique) and
`variant_0_angle_90.jpg` (roof plan) under
`frontend/public/archetypes/buildings/calgary-15-connected-tower/`. A camera was
fitted to each perspective image from measured building corners, so every
comparison is made from the same viewpoint.

**The references disagree with each other and with the catalogue text in three
places.** Each is recorded in the manifest with the choice made:

- **Walkway level.** The archetype text puts +15 walkways at the second storey.
  Both perspective images show this one at the third, about 9 m up. It is built
  as drawn. Moving it down one storey is one constant, `BRIDGE_STOREY`.
- **Penthouse from the street.** The street image shows about 6 m of penthouse
  above the parapet. The roof plan and the oblique agree with each other and
  cannot produce that view; about 1 m shows. The roof plan governs.
- **Storey count.** The catalogue description says six storeys. Both images
  show five.

**Inferred, because no image shows it:** the west flank, the rear, the interiors
and the structural grid. The walkway runs on to a neighbour in the images. Here
it is a 9 m length with a glazed end, no neighbour, and no support at its free
end.

**Left out on purpose:** trees, pavements, streets and neighbouring buildings,
which belong to the site and not the model; surface texture such as exposed
aggregate and the tie holes in the board-formed concrete.

## Files

| File | Purpose |
|---|---|
| `clay_kit.py` | Pure-Python mesh kit and GLB writer. Names, extras and materials follow the reviewed clay library (`CLAY_<ROLE>`), including the `CLAY_GLASS` material the runtime swaps by name |
| `build.py` | The building. Every dimension is a named constant at the top |
| `cameras.json`, `review.html`, `render.cjs` | Review renders of the exact GLB in headless Chromium |
| `boards.py` | Four 1080 x 1920 phone boards |
| `verify.py` | Delivery checks; writes `delivery-verification.json` |
| `test_build.py` | 11 tests, including that the generator still produces the reviewed bytes |
| `prework-manifest.json`, `candidate.json` | The measured contract and the candidate's hashes |
| `evidence/` | Builder review and delivery verification. The independent review is added when it reports |

The GLB, renders and boards are review material and stay outside Git, under the
ignored `artifacts/` directory. **The GLB is reproducible:** the generator is
deterministic, and `candidate.json` records the SHA-256 it must produce.

## Reproduce

Needs Python 3.11 or later. Renders also need the frontend dependencies
installed and the repository served locally.

```bash
python3 tools/catalogue_plus15_concrete_pilot/build.py --output <new directory> --version <n>
python3 -m http.server 8765 --bind 127.0.0.1 &          # from the repository root
node tools/catalogue_plus15_concrete_pilot/render.cjs <new directory>/<candidate>.glb <new directory>/renders
python3 tools/catalogue_plus15_concrete_pilot/boards.py <new directory>      # needs Pillow
python3 tools/catalogue_plus15_concrete_pilot/verify.py <new directory>
python3 -m pytest tools/catalogue_plus15_concrete_pilot
```

`build.py` refuses to write into an existing directory, and the render and board
scripts refuse to replace a file: RLASM never overwrites a candidate.

## Before this can be offered to students

1. A person looks at the renders and boards and accepts or rejects the model.
2. Local install and student trial, as `docs/BUILDING_CATALOGUE_WORKFLOW.md`
   describes. This needs the local database and storage, which the session that
   built the model did not have.
3. The runtime review from `docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md`, row by
   row, in the running app.
4. A recorded human approval, then `python -m tools.catalogue_promotion prepare`.

Each of those is a separate decision. Passing one does not grant the next.
