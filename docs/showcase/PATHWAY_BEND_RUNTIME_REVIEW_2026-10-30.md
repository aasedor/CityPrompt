# Surface pathway bends — runtime review, 30 October 2026

Scope: shared geometry and editing for the eight existing `narrow-pathway-v1`
designs, using the [runtime review template](../ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md).
No new archetype, source GLB, recipe revision, publication flag or lane width.

- `garden_gravel_path_v1`: 1.5 m
- `concrete_neighbourhood_walk_v1`: 1.8 m
- `brick_courtyard_path_v1`: 2 m
- `timber_garden_walk_v1`: 2 m
- `asphalt_shared_path_v1`: 3 m
- `standalone_narrow_sidewalk_v1`: 1.5 m
- `standalone_neighbourhood_sidewalk_v1`: 2 m
- `standalone_urban_sidewalk_v1`: 3 m

Source implementation: `8c6dd22b05ae917ed6e5249001e2b486b051bd3d`.
Local QA: frontend 5177 / API 8004; original 5174 / 8000 preserved.
Disposable retained project: `fc8a3322-10be-4808-94a1-471877b0077e`.
Prepared level ground, ordinary desktop mouse/keyboard, IAB 1280 × 720.
The user's Macleod project was opened without changing its data.

## Change and source identity

Only these finite, zero-motor-lane designs bypass vehicle turning-envelope
restrictions. They retain their source width, site-boundary checks and existing
2–2000 m total route limits. Consecutive authored controls must remain distinct.
Segment rectangles and full 24-sided interior discs form one unioned surface;
enclosed lawn holes stay unpaved in the rendered mesh. The persisted plot uses
the exterior ring, while route and sparse authored controls retain the design.
The backend attests the same surface and uses actual route length, rather than
inferring length from filled plot area. Legacy bounded miter strips stay readable.
Unrelated plots, false widths, motor lanes and malformed sources fail closed.

The initial development import used a named CommonJS export and prevented the
editor loading in Vite. It now uses the library's default export. The reported
Macleod project was reopened successfully through ordinary browser controls.

## Applicable gates

| Gate | Result | Evidence / limit |
| --- | --- | --- |
| C1 exact identity, S1 metric section | PASS, automated | All eight source IDs and native widths; finite allowlist and contract tests. |
| S2 route geometry | PASS, automated | Switchbacks, hairpins, retraces, crossings, loops, short first/last segments; 48 actual frontend footprints compiled with source unchanged. |
| C2 ground contact | PARTIAL | Shared prepared-ground datum retained; planar mesh rays pass. New sloped/natural-ground walking trials not run. |
| C3 conflicts / S4 limits | PASS, automated | Existing street connection/boundary and native route regression suites; motor-road guards retained. |
| C4 late results | PASS, regression | Existing zone-write hook suite passes; not a new concurrency stress run. |
| C6 edit/history/reopen | PASS, browser pilot | UI drew a roughly 330 m five-control concrete switchback, saved/compiled, changed to brick, added a sixth control, Undo to five, Redo to six, then reopened. |
| C7 recovery | PASS, bounded | Wrong-source backend inputs reject without source mutation; browser module error corrected and project reopened. |
| C8 visual/capture | PARTIAL | Free exact-source capture opened its enlarged preview. Original-file download timed out through the browser's Download render control. Delivered preview evidence is a screenshot, not the source PNG. No new paid image/video. |
| C9 controls | PASS, browser pilot | Tight-bend help text, fixed width, native finish selection and Add bend point. |
| S3 external-road access | NOT TESTED in this change | Surface paths do not auto-connect to public motor roads; no new external-road functionality. |
| B/P-specific gates | N/A | Existing procedural street/path adapter change, no new building/park asset. |

Concrete and brick have the ordinary-browser pilot above. The other six variants
have automated geometry/compiler coverage, not individual new browser trials.
Do not report all catalogue assets or every terrain mode as browser verified.

## Verification

- 221 focused frontend cases; 141 further street/zone-write regression cases.
- 187 backend pathway/public-realm/native-contract cases, plus four vehicle-axis recovery cases.
- 48 exported frontend footprints through the real recipe adapter without source mutation.
- TypeScript, scoped ESLint, Ruff and pinned Black checks pass; bounded independent review approved.
- Fresh code-only production build passes unchanged budgets: 466.4 KiB initial,
  8444.9 KiB total JS, 2441.0 KiB largest chunk, 190.2 KiB CSS.
- Runtime inventory: 5470 asset records unchanged; two new source-input paths.
  This sparse checkout still has 4573 missing/LFS-pointer required payloads.
  This build is not a newly hydrated release asset packet.

Detailed logs, screenshots, readback and delivery receipts are outside source:
`C:/dev-artifacts/CityPrompt/overnight-hardening-20261030/pathway-bends-20261030/`.
No live deployment, guard exception or additional paid generation.
