# Desktop and tablet catalogue layout

The place-and-reshape sidebar now has three compact launchers: Buildings, Parks and Streets. A separate catalogue dialog provides large previews, Calgary subcategory filters, search and twelve-item batches. Only its results scroll; filters remain visible. Picking an asset closes the dialog and uses the existing placement callbacks and saved asset identifiers. The map pauses while browsing. Escape closes the dialog and restores launcher focus.

The toolbar separates optional tools from its save/render footer. Project steps and custom-drawing 3D generation are under an expandable section. Updated onboarding describes opening the catalogue first. No catalogue assets, geometry, provider settings or saved project data were changed.

## Verification

- 12 focused Vitest checks passed: palette, registry and toolbar. Includes a simulated 30-item catalogue, filtering, object/street dispatch, close-on-pick, Escape and focus restoration.
- TypeScript check and scoped ESLint passed.
- Browser checked at 1264 x 625 (short desktop), 1024 x 768 (landscape tablet), and 768 x 1024 (portrait tablet). These are viewport simulations, not physical-device tests.
- Confirmed park selection returns to placement; cancelled without creating a new zone. Catalogue dialog fits tablet portrait without outer scrolling. Default desktop launchers, Select, Guide and Render/Video fit without scrolling.
- Screenshots are ignored local output in artifacts/catalogue-cycle/layout-desktop.png, catalogue-desktop.png, catalogue-tablet.png, and catalogue-tablet-portrait.png.
- No paid renders, asset generation, deployment or push performed.

The local catalogue still contains its existing four pilot choices. This change prepares browsing for expansion without approving or publishing additional families.
