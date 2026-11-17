# District barriers for Add details: Kensington, Inglewood and Fourth Street

## Scope

Add four versions of the 3 m concrete road barrier that carry the logo of a
Calgary business improvement area on both long faces. They extend
`calgary-details-v1` (now 151 objects, IDs prefixed `detail-yyc-`) and sit in
**Traffic & safety**. Searching `district barrier` lists them.

| Item | Artwork | Triangles |
|---|---|---:|
| District barrier · Kensington | Burgundy roundel and wordmark on off-white | 2,072 |
| District barrier · Inglewood | Yellow wordmark on red | 858 |
| District barrier · Fourth Street · purple | Purple and pink 4 with the wordmark, on white | 2,312 |
| District barrier · Fourth Street · green | Teal and green 4 with the wordmark, on white | 2,312 |

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
| Kensington | A roundel with an italic slab K, and "Kensington" in a bold sans | Burgundy `#42031a` on off-white `#f8f8f8` | An older "Kensington Village" logo with a blue and green K |
| Inglewood | "INGLEWOOD" in a heavy block face, dated 2026 in its file name | Yellow `#fec93c` on red `#d84d2c`, as the site displays it | An older black monogram of I and N |
| Fourth Street | A rounded 4 built from two bars and a wedge, with "fourth street" in a thin rounded sans | Teal `#0a4f5a` to green `#27a87f` on its site icon; purple `#353192` to pink `#ad5f90` on the City's directory | The same 4, in purple and pink, with a black wordmark |

Fourth Street's own site shows the 4 in white over photographs, and in green as
its site icon; the City's directory shows it in purple. Both colourways were
built, since it is not clear from the sites which the association prefers.

### Source files

The files are not kept in the repository. Their hashes are recorded in
`tools/detail_catalogue/district_logo_shapes.json` and here.

| File name used by the tool | Where it came from | SHA-256 |
|---|---|---|
| `kensington-2026.svg` | The logo drawn inline in the menu of `www.kensingtonyyc.com` | `2f9ede7e6b471a6ee66785983e25b3ed607a51bb12bf44a6983b2e4c28614f5d` |
| `inglewood-2026-horizontal.jpg` | Header image of `www.inglewoodyyc.ca`, served from `static.wixstatic.com/media/f0ecb7_58a72cbc49594c92aeb96d9675e32aa0~mv2.jpg` | `15d94160a350ae41c1622f8ee7264719ae77c9296b72b4c04dbae5a4d9d78b3c` |
| `fourth-street-header.png` | Header logo of `www.4streetcalgary.com`, `Artboard 1.png` at 1500 px wide | `c4f2ff0dd6f4d8f62e19b2a8c1aea790658f66a7d53deb161e7a60f5fd8e5787` |
| `fourth-favicon.ico` | Site icon of `www.4streetcalgary.com` | `aa54053a978e59c8c763ca79b84ce6ca2176a0092a18676fc53baa356806f604` |
| `4th-street-logo.png` | The City's directory, `www.calgary.ca/for-business/bias-in-calgary.html` | `d82173c6195c075aed0d919a10be02753d49d6b9b0d070402ed37d058c9b6e1b` |

## Method

The kit carries no textures, so a logo is painted the way the murals are: as
flat-colour shapes that tile the barrier's face. `bake_district_logos.py` does
this once, and writes `district_logo_shapes.json`, which the builder reads. The
builder needs none of the tool's dependencies, and rebuilds are deterministic.

- **Kensington** is read from the vector file, so its outlines are exact.
- **Inglewood** is traced from the 3,600 px wide image.
- **Fourth Street's 4** is rebuilt from its geometry, which the artwork makes
  plain: an upright bar and a level bar with round ends, and the wedge joining
  their tips. Its gradients become seven, eight and four bands, each in the
  colour sampled from the artwork at that spot. The wordmark is traced.
- The background is cut around the logo, everything is split along the bend in
  the barrier's profile, and the pieces are triangulated so that neighbours
  share their edges point for point. The triangles cover the face exactly once.
  Nothing lies on top of anything else, so nothing can flicker at a distance.
- Each face reads left to right when you stand in front of it. The top of the
  barrier is painted in a colour from the logo; the toe, ends and underside stay
  concrete.

**Layout choices that are mine, not the associations'.** Kensington's and
Inglewood's logos are shown whole and centred. Fourth Street's 4 and wordmark
are set side by side, with the wordmark larger than in the association's own
lockup, because at the lockup's proportions the wordmark would be about 4 cm
tall on a barrier. The backgrounds are off-white, red and white.

## Verification

- Every barrier was rendered at eye level, oblique and card size and reviewed
  ([sheet](calgary-details-v1/district-barriers-review.jpg)). The baked artwork
  was also drawn flat and compared with the source logos. Changed after review:
  the parts of the 4 were made to share their edges exactly, which removed a
  hairline gap, and one band of the purple 4 that had sampled a pale edge pixel
  was resampled. Agent review passed; independent human visual acceptance, and
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
- The 147 earlier models and their card images are byte-identical.
- The whole CI list was run locally: lint with zero warnings, dead-code and type
  checks; `npx vitest run` with 512 files and 4,542 tests passed; the 135
  catalogue delivery tests; the asset and manifest checks, with 5,981 required
  runtime files; tools, hosted-asset and backend detail tests with 236 local
  rows and 391 extras; and the browser tests, 13 passed plus the startup test.
- Production build with CI settings, then `check-budget`: 8,432.8 KB of
  8,448 KB.

Not done here: placing them on the live map, which needs a real map key, and
the full backend suite, which needs a database.
