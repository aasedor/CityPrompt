# District barriers for Add details: Kensington, Inglewood and Fourth Street

## Scope

Add four versions of the 3 m concrete road barrier that carry the logo of a
Calgary business improvement area on both long faces. They extend
`calgary-details-v1` (now 151 objects, IDs prefixed `detail-yyc-`) and sit in
**Traffic & safety**. Searching `district barrier` lists them.

| Item | Artwork | Triangles |
|---|---|---:|
| District barrier · Kensington | Off-white wordmark on burgundy, with the roundel in an orange, blue and green gradient | 2,526 |
| District barrier · Inglewood | Yellow wordmark on red | 858 |
| District barrier · Fourth Street · purple | White 4 and wordmark on a ground that runs from indigo to pink | 2,734 |
| District barrier · Fourth Street · green | White 4 and wordmark on a ground that runs from teal to green | 2,734 |

Every one is 3.0 × 0.6 × 0.8 m, the footprint of the plain barrier and of the
[painted barriers](MURAL_BARRIERS_2026-11-17.md), so they mix in one row.

## Permission is needed before these ship

**These logos are the property of their business improvement areas.** They were
reproduced here on request, for scenes that show barriers in those districts.
Nothing in this repository grants a right to use them. Before this catalogue is
published or merged for general use, each association should agree to its logo
appearing in the product. Until then the four items are easy to leave out: they
are in one commit, and removing their four entries from `SPECS` in
`tools/detail_catalogue/build_calgary_details.py` and re-registering drops them.

This departs from the earlier rule for this kit, which kept all branding and
logos out. That rule still holds for everything else: no item carries City of
Calgary or program branding, and the mural designs remain original.

## Research: logos and colours

Each association's own website was read on 2026-11-17, along with the City of
Calgary's directory of business improvement areas. The directory shows older
logos for two of the three, so the associations' own current artwork was used.

| District | Current logo, from its own site | Colours | On the City's directory |
|---|---|---|---|
| Kensington | A roundel with an italic slab K, and "Kensington" in a bold sans. The site icon shows the roundel in a gradient | Burgundy `#42031a`, off-white `#f8f8f8`, orange `#ff5010`, blue `#7b9cff` and green `#00e3af`, as named in the site's stylesheet | An older "Kensington Village" logo with a blue and green K |
| Inglewood | "INGLEWOOD" in a heavy block face, dated 2026 in its file name | Yellow `#fec93c` on red `#d84d2c`, as the site displays it | An older black monogram of I and N |
| Fourth Street | A rounded 4 built from two bars and a wedge, with "fourth street" in a thin rounded sans | Teal `#0a4f5a` to green `#27a87f` on its site icon; purple `#353192` to pink `#ad5f90` on the City's directory | The same 4, in purple and pink, with a black wordmark |

Fourth Street's own site shows the 4 in white over photographs, and in green as
its site icon; the City's directory shows it in purple. Both colourways were
built, since it is not clear from the sites which the association prefers.

Kensington's site sets off-white text on a burgundy page and uses the orange,
blue and green as accents. Its site icon is the roundel filled with a gradient
from orange at the lower left, through blue, to green at the upper right, with
the K cut out.

### Source files

The files are not kept in the repository. The four the tool reads are recorded
by hash in `tools/detail_catalogue/district_logo_shapes.json` and here. The last
two only supplied the colours of Fourth Street's two gradients, which are now
written into the tool.

| File name used by the tool | Where it came from | SHA-256 |
|---|---|---|
| `kensington-2026.svg` | The logo drawn inline in the menu of `www.kensingtonyyc.com` | `2f9ede7e6b471a6ee66785983e25b3ed607a51bb12bf44a6983b2e4c28614f5d` |
| `kensington-webclip.png` | Site icon of `www.kensingtonyyc.com`, served from `cdn.prod.website-files.com` | `fe99aa9d9f42055089fbc218c9720ca759839ea862e0b92deb6010b8dfda1687` |
| `inglewood-2026-horizontal.jpg` | Header image of `www.inglewoodyyc.ca`, served from `static.wixstatic.com/media/f0ecb7_58a72cbc49594c92aeb96d9675e32aa0~mv2.jpg` | `15d94160a350ae41c1622f8ee7264719ae77c9296b72b4c04dbae5a4d9d78b3c` |
| `fourth-street-header.png` | Header logo of `www.4streetcalgary.com`, `Artboard 1.png` at 1500 px wide | `c4f2ff0dd6f4d8f62e19b2a8c1aea790658f66a7d53deb161e7a60f5fd8e5787` |
| `fourth-favicon.ico` | Site icon of `www.4streetcalgary.com` | `aa54053a978e59c8c763ca79b84ce6ca2176a0092a18676fc53baa356806f604` |
| `4th-street-logo.png` | The City's directory, `www.calgary.ca/for-business/bias-in-calgary.html` | `d82173c6195c075aed0d919a10be02753d49d6b9b0d070402ed37d058c9b6e1b` |

## Method

The kit carries no textures, so a logo is painted the way the murals are: as
flat-colour shapes that tile the barrier's face. `bake_district_logos.py` does
this once, and writes `district_logo_shapes.json`, which the builder reads. The
builder needs none of the tool's dependencies, and rebuilds are deterministic.

- **Kensington** is read from the vector file, so its outlines are exact. The
  roundel is sliced into 24 bands across the direction of the site icon's
  gradient, which is measured from the icon, and each band takes the icon's
  colour there. The K is a hole in the roundel, so the burgundy shows through.
- **Inglewood** is traced from the 3,600 px wide image.
- **Fourth Street's 4** is rebuilt from its geometry, which the artwork makes
  plain: an upright bar and a level bar with round ends, and the wedge joining
  their tips. The artwork is white with soft tints that set the three parts
  apart; here each part keeps its lightness and takes its tint from the ground
  behind it. The wordmark is traced. The ground runs through the gradient in 24
  bands along the barrier.
- The background is cut around the logo, everything is split along the bend in
  the barrier's profile, and the pieces are triangulated so that neighbours
  share their edges point for point. The triangles cover the face exactly once.
  Nothing lies on top of anything else, so nothing can flicker at a distance.
- Each face reads left to right when you stand in front of it. The top of the
  barrier is painted in a colour from the logo; the toe, ends and underside stay
  concrete.

**Layout choices that are mine, not the associations'.** Each barrier is painted
in a ground colour from its district, with the logo large across it. Kensington
and Inglewood are shown whole and centred. Fourth Street's 4 and wordmark are
set side by side, with the wordmark larger than in the association's own lockup,
because at the lockup's proportions the wordmark would be about 4 cm tall on a
barrier. Placing Kensington's gradient roundel beside the off-white wordmark,
and running Fourth Street's gradient along the whole barrier, are my
arrangements of each district's own colours.

**Redesigned after feedback.** The first version set the Kensington and Fourth
Street logos in their own colours on off-white and white barriers, which read
as signs on plain concrete beside the Inglewood barrier. Both were redone the
way the Inglewood one works: a full ground of district colour with the logo
large and light on it. The Inglewood barrier is unchanged.

## Verification

- Every barrier was rendered at eye level, oblique and card size and reviewed
  ([sheet](calgary-details-v1/district-barriers-review.jpg)). The baked artwork
  was also drawn flat and compared with the source logos. Changed after review:
  the parts of the 4 were made to share their edges exactly, which removed a
  hairline gap, and the gradients were given 24 bands in place of 14 and 16 so
  the steps between colours are small. Agent review passed; independent human visual acceptance, and
  the associations' own review of their logos, are open.
- Placed on the test street through the app's own placement code
  ([scene](calgary-details-v1/scene-district-barriers.jpg)). All 236 local
  models passed the datum, size and anchor checks.
- A tools test requires the baked triangles to cover the face exactly, none to
  cross the bend, each barrier to share the plain barrier's dimensions and each
  description to say whose logo it is. A frontend test checks the four names.
- In the real project page with a mocked backend, in a temporary browser trial
  that was not committed: the four are found by searching `district barrier`,
  load from their static card images without requesting a model file, and
  choosing one arms placement
  ([screenshot](calgary-details-v1/app-district-barriers.jpg)).
- The 147 earlier models and their card images are byte-identical, and so is the
  Inglewood barrier after the redesign of the other three.
- The whole CI list was run locally: lint with zero warnings, dead-code and type
  checks; `npx vitest run` with 512 files and 4,542 tests passed; the 135
  catalogue delivery tests; the asset and manifest checks, with 5,981 required
  runtime files; tools, hosted-asset and backend detail tests with 236 local
  rows and 391 extras; and the browser tests, 13 passed plus the startup test.
- Production build with CI settings, then `check-budget`: 8,432.8 KB of
  8,448 KB.

Not done here: placing them on the live map, which needs a real map key, and
the full backend suite, which needs a database.
