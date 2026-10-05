# Render style guide checkpoint — 2026-10-05

Initiative: `codex/render-style-guide-2026-10-05`, based on the landing checkpoint
`2b2a9fbb6`. Local source and intentional example assets; no publication.

The globe and street image controls now open a shared guide. All established
styles have descriptions of their medium and useful presentation contexts.
Existing style IDs, street aliases, availability gates and render pipelines
are preserved. Browsing examples does not select a style or capture, generate
or save an image. **Use this style** applies the explicit selection and closes
the guide. Projection-changing styles explain that they change the view.

Three real saved City Prompt studies illustrate Photomontage, Watercolour and
Charcoal, with an optional view of each original 3D source. Photomontage and
Watercolour can be compared together. They show the same community and street
direction with different source captures; Charcoal uses a closer building view.
The guide states these differences and identifies the images as historical
examples rather than previews of the current project. Styles without saved
examples show their description without borrowing another style's image.

Evidence comes from the September pilot documented in
[RENDER_STYLE_DETAIL_PILOT_2026-09-08.md](RENDER_STYLE_DETAIL_PILOT_2026-09-08.md).
The Photomontage is the recorded human-approved visual benchmark. Watercolour
uses the improved source-conditioned study rather than the earlier material
drift example. This checkpoint changes neither provider prompts nor building
geometry and makes **zero provider calls**. It does not assert that all styles
have been visually validated or that generative design drift is solved.

## Delivery and verification

- The dialog code is loaded on demand. No gallery image mounts while closed;
  one mounts initially, two only when street comparison or source comparison
  is requested. Images use native lazy loading and asynchronous decoding.
- Six byte-identical PNG deliverables total **12,245,580 bytes**. Each source,
  output, original filename, audit ID, byte count and SHA-256 is recorded in
  `frontend/public/render-style-examples/manifest.json`. Their original footer
  notices remain. They use a narrow Git LFS rule, not ordinary binary blobs.
- `npm run check:render-style-examples` verifies integrity before every build,
  including detection of unhydrated LFS pointers. This is a local integrity
  check, not a measured hosted network or forty-student load result.
- **28 Vitest tests passed** across the guide, globe controls, street panel
  and existing Direct 3D path. The street integration verifies that browsing
  makes no renderer/capture/save calls and that explicit application forwards
  the chosen style. Existing street tests now clear only their own per-project
  session preference between cases.
- **1 Node integrity test passed**, covering all six PNGs and the manifest.
  TypeScript, touched-file ESLint, catalogue JSON/model contract, production
  build and bundle budget checks passed.
- Initial JS stays **460.0 KiB**; total JS **8,078.9 KiB**, CSS **168.5 KiB**.
  The guide's separate chunk is about **5.95 KiB** raw / **2.27 KiB** gzip.
  These build metrics do not include on-demand image bytes.
- Production browser on 5179 verified loaded comparison images, correct
  Watercolour/Charcoal sources, explicit selection, focus restoration,
  projection guidance and Escape dismissal. 820 × 1,180 and 390 × 844 layouts
  had no horizontal overflow; the narrow dialog scrolls vertically. Temporary
  viewport overrides were reset. Browser error capture was empty.
- The isolated classroom project now contains a saved five-corner flexible
  pocket park. Its first save correctly required a level site; after applying
  the existing ground preparation control, Save again completed and 3D saved
  was visible after production reload. This tests the existing park workflow,
  not new park geometry or measured terrain accuracy. Credits remain 1,000 and
  saved project renders remain zero.

Build output, dependency junctions and Vite caches remain ignored. Browser QA
and the dedicated local preview launcher remain outside Git at
`C:/dev-artifacts/CityPrompt/overnight-2026-10-04/`:
`render-style-comparison-production.png`, `render-style-source-tablet.png`.
  The external 5178 launcher serves only manifest-verified guide PNGs because its
catalogue public directory comes from an older recovery worktree. Production
5179 uses the normal built public assets.

Restarting the development preview exposed a pre-existing stale catalogue
packet after the browsing checkpoint changed catalogue code. The existing
delivery audit rebuilt an external packet from verified assets and current
source bindings: **95 choices, 335 distinct dependencies, zero failures**.
The old packet remains preserved. Both the restarted preview and final
production build use the new packet; no catalogue choices were activated.

The primary OneDrive checkout and pending catalogue waves remain untouched.
New matched-camera style samples (including Risograph), further art direction,
forty-user hosting tests, new archetype acceptance and video work remain ahead.
