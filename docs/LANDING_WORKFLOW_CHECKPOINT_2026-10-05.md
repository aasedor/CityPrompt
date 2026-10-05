# Landing workflow checkpoint — 2026-10-05

Initiative: `codex/landing-classroom-workflow-2026-10-05`, based on the catalogue
browsing checkpoint `9b8ca2846`. Local-only source change; no publication.

The landing page introduces the actual Site → Design → Present workflow:
real site boundaries, Calgary district/assessment context, separate existing
and proposed land-use studies, catalogue purpose/size/style discovery, 3D
exploration and still-image presentation. It retains the cream, dark ink and
bright accent identity, with a static labelled zoning illustration. The
illustration is explicitly an illustrative plan, not a fabricated screenshot.

Anonymous visitors see the existing sign-in form; returning users see their
project entry without a misleading Sign in heading. The main heading is unique,
the loading state is labelled, a skip link is available and theme colours use
the existing shared variables. Mobile Sign in navigates directly to the form.

The old 7,805,575-byte opening collage is no longer requested by this page.
Existing site and AI image examples total 3,902,998 bytes and use native lazy
loading below the workflow explanation. This reduces referenced raster data
from about 10.35 MiB to 3.72 MiB, excluding the unchanged logo. Native lazy
loading can prefetch images near the viewport; this is not a measured hosted
loading-time guarantee. No image was generated or edited. The landing page no
longer subscribes to the decorative pointer trail.

Verification:

- Existing LoginPage tests: **7 passed**; TypeScript and touched-file ESLint passed.
- Map-enabled production build, catalogue JSON and model-contract checks passed.
- Bundle budget passed: initial JS **460.0 KiB**, total JS **8,067.4 KiB**, CSS
  **168.4 KiB**. Initial JS adds about 4.8 KiB to the previous checkpoint.
- Development browser: anonymous form, successful sign-in to projects,
  returning-user Open projects navigation, one h1, labelled illustration and
  loaded example images verified.
- Responsive browser: 820 × 1,180 dark mode and 390 × 844 anonymous/mobile
  Sign in anchor checked. Neither viewport had horizontal overflow. Temporary
  theme and viewport overrides were restored.
- Production browser on 5179: revised landing and returning-user entry verified;
  console error capture empty. The external proxy uses the isolated backend on
  8009. No paid rendering calls were made.

Only `LandingPage.tsx` and this checkpoint are source deliverables. Build output,
Vite cache and dependency junction remain ignored. Browser screenshots are
outside Git at `C:/dev-artifacts/CityPrompt/overnight-2026-10-04/`:
`landing-production.jpg`, `landing-tablet-dark.jpg`, `landing-mobile-signin.jpg`.

This checkpoint does not certify forty concurrent hosted users, fine terrain
alignment, new archetype acceptance, video quality or new render-style samples.
The primary OneDrive checkout and pending catalogue waves remain untouched.
