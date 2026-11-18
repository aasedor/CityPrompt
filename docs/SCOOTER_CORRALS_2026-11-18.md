# E-scooter corrals for Add details

## Scope

Add the City of Calgary's e-scooter corral: the galvanized pipe enclosure with
four art panels that the City places on sidewalks and curb extensions for shared
e-scooters. It extends `calgary-details-v1` (now 164 objects, IDs prefixed
`detail-yyc-`).

All scooter items sit in a new category, **Shared micromobility**, with its own
tile: a scooter parked in front of a corral. The category holds the nine corrals
below and the older e-scooter parking corral, which moved there from Street
furniture. Searching `e-scooter corral` lists all ten.

| Item | Panels | Triangles |
|---|---|---:|
| E-scooter corral · plain panels | Blank, ready for art | 1,222 |
| E-scooter corral · Foothills sunrise | Sunrise over peaks, foothills and prairie | 3,060 |
| E-scooter corral · Chinook arch | Chinook arch of sunset cloud over the range | 2,906 |
| E-scooter corral · River ribbons | Flowing bands of river blue and green | 2,606 |
| E-scooter corral · Triangle mosaic | Bright mosaic of irregular triangles | 1,724 |
| E-scooter corral · Chevrons | Bold zigzag chevrons | 1,802 |
| E-scooter corral · Prairie quilt | Quilt blocks of barn red, mustard and denim | 1,606 |
| E-scooter corral · Aspen grove | White aspen trunks under a gold canopy | 1,848 |
| E-scooter corral · Confetti | Bright dots on deep teal | 2,962 |

The older **E-scooter parking corral** (`detail-yyc-scooter-corral`), a painted
on-street bay with a low rail, a sign and four scooters, is a different thing.
Its model is unchanged; only its category moved. Projects save item IDs, not
categories, so placed corrals are unaffected.

## Source

The City's standard drawing **P2023-589-0001A**, "E-scooter corrals assembly",
Fleet Services, initial release 2024-02-21, sheets 1 and 2, supplied with two
photographs of corrals in use. The drawing and photographs are not kept in the
repository.

Read from the drawing, in inches:

- A U of 1-1/2 in schedule 40 galvanized pipe, 1.900 in outside, open on one
  long side. Posts stand 48 in apart, centre to centre: three along the long
  side, 96 in, and one at the open end of each 48 in return. Five posts in all.
- Each post stands in a floor flange. Slip-on rail fittings join the posts and
  rails: a 90° elbow at the top of each open-end post, a three-way corner at the
  two long-side corners, a tee at the top of the middle post, and through-tees
  at the bottom rail.
- Two rails to each of the four bays, 28 in apart centre to centre. The fittings
  top out at 36 in.
- Four identical panels, 40 by 26 in, each held to its rails by four clamps.

## What was built

- Every dimension above, in metres from inches. The model is 2.61 by 1.32 m over
  its flanges and 0.92 m tall. The long side runs along x; the open side faces
  the other way.
- Posts and rails are 8-sided pipes. Each fitting is drawn as one squarish
  block per pipe that enters it, which closes the corner between them as the
  cast fittings do. Each flange is an oval plate with a socket. Each clamp is a
  collar on the rail with a lug over the panel's edge.
- Panels are 6 mm thick, centred in the plane of their rails.

**The artwork is original.** The photographs show corrals wrapped with real
artists' murals. Those belong to their artists and are not reproduced. The
panels carry the eight original designs already painted on the road barriers
([mural barriers](MURAL_BARRIERS_2026-11-17.md)), so a corral can match the
barriers beside a patio. Each design keeps its true proportions: one panel
shows 1.16 m of the 3 m mural at full height. The four outer faces run as one
continuous strip, from the left return round the long side to the right
return, and the inner faces run the other way round, so the picture also reads
continuously from inside. Each face reads left to right when faced. As on the
barriers, a mural replaces the panel's face rather than lying on it, so nothing
can flicker.

The files follow the kit convention: linear vertex colours, flat normals, one
matte mesh, no textures. The nine total 2,260,672 bytes and 19,736 triangles,
each under the kit's limit of 3,500 triangles and 400 KB. The 155 earlier
models are byte-identical.

## Verification

- Every corral was rendered at eye level, oblique and card size, and reviewed:
  [review sheet](calgary-details-v1/scooter-corral-review.jpg),
  [close views](calgary-details-v1/scooter-corral-close.jpg),
  [catalogue cards](calgary-details-v1/scooter-corral-cards.jpg). Agent review
  passed; independent human visual acceptance is open.
- A tools test checks the drawing's dimensions: 96 by 48 in between post
  centres, about 36 in tall, rails 28 in apart, five posts, 40 by 26 in panels.
  It requires each of the eight panel faces to be covered by its artwork exactly
  once, with no gap and nothing past a panel's edge, and each design to carry the
  same name and colour as the road barrier of that name.
- A tools test requires all ten scooter items, and only them, in Shared
  micromobility, and a tile drawing for the category. A frontend test requires
  the category to list exactly these ten, and Street furniture to list none.
- The tools, hosted-asset, frontend park and backend detail tests pass, with 249
  local rows and 404 extras.
- Runtime asset manifest: 6,007 required files (+18). The manifest generator
  needs every referenced file on disk, and the 370 recovered-detail files are
  installed from a separate bundle that this checkout does not have. For that
  one run, size-matched stand-ins were placed in their folder, which holds no
  tracked files, and removed afterwards. The only rows that changed are the 18 new files and the
  totals.

- Lint with zero warnings and the type check pass on the changed files.
- Production build with CI settings, then `check-budget`: all budgets met, with
  7,212.0 KB of JavaScript against 8,512 KB. This was measured before the
  category tile was added; the tile is one small SVG drawing. The build needs the
  recovered details on disk; they were installed from their archive in Git LFS
  with `scripts/hydrate_recovered_details.py`, which checks every file's hash, and
  removed afterwards.

Not done here: placing them on the live map, which needs a real map key.
