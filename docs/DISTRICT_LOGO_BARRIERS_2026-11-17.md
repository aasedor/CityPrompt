# District barriers for Add details: Kensington, Inglewood, Fourth Street and 17th Ave

## Scope

Add six versions of the 3 m concrete road barrier that carry the logo of a
Calgary business improvement area on both long faces. They extend
`calgary-details-v1` (now 153 objects, IDs prefixed `detail-yyc-`) and sit in
**Traffic & safety**. Searching `district barrier` lists them.

| Item | Colours | Artwork | Triangles |
|---|---|---|---:|
| District barrier · Kensington | Burgundy, off-white, orange | Off-white wordmark and orange roundel on burgundy | 2,156 |
| District barrier · Inglewood | Red, yellow | Yellow wordmark on red | 858 |
| District barrier · Fourth Street · purple | Purple, white, pink | The name in two lines between two 4s, on purple | 2,868 |
| District barrier · Fourth Street · green | Teal, white, green | The name in two lines between two 4s, on teal | 2,868 |
| District barrier · 17th Ave | Red, white | The logo four times in white on red | 3,044 |
| District barrier · 17th Ave · single logo | Red, white | One large logo in white at the centre, on red | 824 |

Every one is 3.0 × 0.6 × 0.8 m, the footprint of the plain barrier and of the
[painted barriers](MURAL_BARRIERS_2026-11-17.md), so they mix in one row.

## Design brief

These are meant to be painted on real barriers, so each design follows three
rules, set after the first two versions were reviewed:

1. **Two or three flat colours.** A ground coat, then one or two more colours.
   No gradients and no shading.
2. **Stencil-ready.** Every shape is a solid area of one colour with a clean
   edge, so the logo can go on through a stencil.
3. **Large, with little bare ground.** Bare surface invites graffiti, so the
   artwork runs most of the length and height of the face.

| Barrier | Colours | Artwork spans, of the face's length | Of its height |
|---|---:|---:|---:|
| Kensington | 3 | 95% | 76% |
| Inglewood | 2 | 87% | 37% |
| Fourth Street, both colourways | 3 | 91% | 90% |
| 17th Ave | 2 | 93% | 90% |
| 17th Ave · single logo | 2 | 20% | 90% |

**The single-logo 17th Ave barrier is an exception to the third rule, made on
request.** It carries one logo at the full height of the face and leaves the
rest red: 94% of the face is one unbroken colour. It is closer to how the
district paints its barriers today, with the logo about twice the height,
judging from the photograph.
The four-logo version remains for where bare surface is a concern.

The Inglewood barrier was approved as it is and was not changed. Its wordmark is
as wide as the barrier allows, but it is one line of low, wide letters, so it
leaves more bare ground above and below than the other two. Two rows of the
wordmark would close that if it matters on the street.

## Permission is needed before these ship

**These logos are the property of their business improvement areas.** They were
reproduced here on request, for scenes that show barriers in those districts.
Nothing in this repository grants a right to use them. Before this catalogue is
published or merged for general use, each association should agree to its logo
appearing in the product. Until then the six items are easy to leave out:
removing their six entries from `SPECS` in
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
| 17th Ave | "17" in heavy numerals with "th" on a small flag and "ave" in script, in an open frame, all with a worn, stamped texture | Crimson `#ab0033` for the logo and bright red `#e21a2d` for buttons and fills, on its site. The file name gives the crimson as 207, a Pantone number | The same logo in crimson |
| Fourth Street | A rounded 4 built from two bars and a wedge, with "fourth street" in a thin rounded sans | Teal `#0a4f5a` to green `#27a87f` on its site icon; purple `#353192` to pink `#ad5f90` on the City's directory | The same 4, in purple and pink, with a black wordmark |

Fourth Street's own site shows the 4 in white over photographs, and in green as
its site icon; the City's directory shows it in purple. Both colourways were
built, since it is not clear from the sites which the association prefers.

**17th Ave in the patio guidelines.** The City's seasonal patio guidelines show
the district's own barriers and banners in a photograph on page 16: a bright red
road barrier with the logo in white, small and centred, beside the red
boardwalk railings, and red street banners with the logo in white. So red with
a white logo is how the district already paints its barriers. The model keeps
those two colours and makes the logo much larger, for the reason in the design
brief.

Kensington's site sets off-white text on a burgundy page and uses the orange,
blue and green as accents. Its site icon is the roundel filled with a gradient
from orange at the lower left, through blue, to green at the upper right, with
the K cut out.

### Source files

The files are not kept in the repository. The four the tool reads are recorded
by hash in `tools/detail_catalogue/district_logo_shapes.json` and here. The
other three only supplied colours: Kensington's site icon, and the two files
that show Fourth Street's 4 in green and in purple.

| File name used by the tool | Where it came from | SHA-256 |
|---|---|---|
| `kensington-2026.svg` | The logo drawn inline in the menu of `www.kensingtonyyc.com` | `2f9ede7e6b471a6ee66785983e25b3ed607a51bb12bf44a6983b2e4c28614f5d` |
| `kensington-webclip.png` | Site icon of `www.kensingtonyyc.com`, served from `cdn.prod.website-files.com` | `fe99aa9d9f42055089fbc218c9720ca759839ea862e0b92deb6010b8dfda1687` |
| `seventeenth-ave-2022.svg` | Header logo of `17thave.ca`, `wp-content/uploads/2022/06/17th-AVE_2022_207.svg` | `7f15638d473ef07f1623318ebdb1e8edddfc5a06d784d9ea30a09c2ae3e848c5` |
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
  roundel is orange and the wordmark off-white. The K is a hole in the roundel,
  so the burgundy ground shows through.
- **Inglewood** is traced from the 3,600 px wide image.
- **Fourth Street's 4** is rebuilt from its geometry, which the artwork makes
  plain: an upright bar and a level bar with round ends, and the wedge joining
  their tips. The association's artwork shades these with gradients. Here the
  upright and wedge are white and the level bar, which lies over them, takes
  the second colour, so the 4 still reads as two bars crossing. The name is
  traced and split into its two words.
- **17th Ave** is read from the vector file. The logo is drawn with a worn,
  stamped texture: about a thousand specks and rough edges. A stencil cannot hold
  those, so every speck and speck-sized hole is removed and the edges are
  evened out to within 3 mm at this size. The numerals, flag, script and frame
  are otherwise unchanged. The logo is 0.68 m tall and 0.61 m wide. One version
  sets it four times along the face, 11 cm apart, which is one stencil used four
  times; the other sets it once at the centre, from the same stencil.
- The background is cut around the logo, everything is split along the bend in
  the barrier's profile, and the pieces are triangulated so that neighbours
  share their edges point for point. The triangles cover the face exactly once.
  Nothing lies on top of anything else, so nothing can flicker at a distance.
- Each face reads left to right when you stand in front of it. The top of the
  barrier is painted in a colour from the logo; the toe, ends and underside stay
  concrete.

**Layout choices that are mine, not the associations'.** Each barrier is painted
in a ground colour from its district. Kensington's logo is shown whole, 2.86 m
wide, with the roundel in the district's orange instead of the gradient of its
site icon. Fourth Street's name is stacked in two lines between a 4 at each end,
which is not a lockup the association publishes; it is arranged that way so the
artwork fills the face. The single flat colours stand in for each district's
gradients: purple `#5a3491` and pink `#d08ab4`, or teal `#0f6166` and green
`#3cc494`. The pink and green are lighter than in the artwork so the level bar
stands clear of both the ground and the white.

Repeating the 17th Ave logo four times is also my arrangement: one logo at the
full height of the face is only 0.61 m wide, so a single one would leave most
of the barrier bare. Trial layouts with three logos, with alternating red and
white panels, with the district's two reds, and on crimson were also made and
shown; the row of four on bright red was chosen as closest to the district's
own barriers.

**Redesigned twice after feedback.** The first version set the Kensington and
Fourth Street logos in their own colours on off-white and white barriers, which
read as signs on plain concrete. The second gave both a full ground of colour,
with a gradient roundel for Kensington and a gradient ground for Fourth Street;
that could not be painted with stencils and left bare ground around a small
logo. This third version follows the design brief above. The Inglewood barrier
is unchanged throughout.

## Verification

- Every barrier was rendered at eye level, oblique and card size and reviewed
  ([sheet](calgary-details-v1/district-barriers-review.jpg)). The baked artwork
  was also drawn flat and compared with the source logos. Agent review passed;
  independent human visual acceptance, and the associations' own review of
  their logos, are open.
- Placed on the test street through the app's own placement code
  ([scene](calgary-details-v1/scene-district-barriers.jpg),
  [the two 17th Ave barriers](calgary-details-v1/scene-seventeenth-ave-barriers.jpg)).
  All 238 local models passed the datum, size and anchor checks.
- A tools test requires the baked triangles to cover the face exactly, none to
  cross the bend, each barrier to share the plain barrier's dimensions and each
  description to say whose logo it is. It also holds every design to the brief:
  no more than three colours, and for Kensington, Fourth Street and 17th Ave
  artwork that spans over 90% of the length and 75% of the height. The
  single-logo barrier is held to two colours, a logo centred on the face and
  over 85% of its height. A frontend test checks the six names.
- In the real project page with a mocked backend, in a temporary browser trial
  that was not committed: the six are found by searching `district barrier`,
  load from their static card images without requesting a model file, and
  choosing one arms placement
  ([screenshot](calgary-details-v1/app-district-barriers.jpg)).
- The 147 models from before the district barriers, and their card images, are
  byte-identical. So is the Inglewood barrier after both redesigns of the
  others, and so are the earlier district barriers after each 17th Ave barrier
  was added.
- The whole CI list was run locally: lint with zero warnings, dead-code and type
  checks; `npx vitest run` with 512 files and 4,542 tests passed; the 135
  catalogue delivery tests; the asset and manifest checks, with 5,985 required
  runtime files; tools, hosted-asset and backend detail tests with 238 local
  rows and 393 extras; and the browser tests, 13 passed plus the startup test,
  run one at a time as CI runs them.
- Production build with CI settings, then `check-budget`: 8,433.1 KB of
  8,448 KB.

Not done here: placing them on the live map, which needs a real map key, and
the full backend suite, which needs a database.
