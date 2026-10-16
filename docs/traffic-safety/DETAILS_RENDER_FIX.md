# Details-only rendering correction — 2026-10-15

The presentation workflow now accepts saved benches, trees, props or paving
without requiring a building, park, street or site boundary. Image, street-image
and video requests bind those details to the saved project revision. Empty or
stale details are rejected before provider spend; existing zone/landscape
freshness checks remain. Capture now classifies authored details as proposal
landscape with a stable project-details instance, retaining geometry instancing.

Preview evidence: 210 backend tests, 81 frontend tests, TypeScript, targeted
ESLint, diff checks and the complete hosted frontend build passed. The build
retains all 156 catalogue choices and passes existing bundle budgets. Local
browser fixture Details-only render acceptance contains no authored zones or
boundary, only RRFB/crossing details. Image and Video entry points are enabled.
Free image source capture passed at 2048 x 742 with 0.6% landscape proposal
coverage and beauty/mask/class/instance previews. A distant view correctly
rejected invisible details. No paid provider calls were made. Video entry and
initial clean capture were checked; completed paid video is not tested here.

Evidence outside Git: C:/dev-artifacts/CityPrompt/details-only-source-check-local-2026-10-15.png;
details-render-final-build-2026-10-15/build-receipt.json and the sibling dist.
Build receipt records the prior HEAD plus source_dirty=true because it validated
the candidate working tree. No generated binaries or credentials are committed.

## Promotion and rollback

Existing pipeline: aasedor/CityPrompt deployment-version, manual Render deploys.
Deploy API and worker first, verify readiness, then frontend. No migrations,
provider changes, settings changes or new resources are required.

Rollback baseline: frontend 349fffc00e046449eccbf5cf02afb39b991c7b28,
dep-db8nuq3l550s73eitv0g (confirmed Live); API ec0b3d0fa878c0a5708bec44d86585450fee8857,
dep-db8n04ei0phs7389ff50; worker 7e41a422c412f8c74ec276cde864ec18add1695a,
dep-db858aavcj2c7388vrkg. Use existing Render deployment history rollback.
Revert frontend first if necessary; retain newer backend support for in-flight
detail requests and all saved data. Old frontend lacks details-only rendering.

Production verification is pending at this source checkpoint.

## Street and video capture follow-up

Street capture classification now recognizes saved details as authored 3D content,
including projects without buildings. The video scene inventory also accepts the
saved details revision and rejects a changed revision or missing detail identity.
The two focused test files passed all 22 tests; TypeScript and targeted ESLint
passed (two existing hook-dependency warnings remain). The production frontend
build and bundle budgets passed using the previously verified asset packet.
The React best-practices review found no new fetching, geometry duplication or
expensive per-frame work in this follow-up.

Actual local street preview succeeded with an RRFB on Google terrain and no
boundary or authored zones. Evidence:
C:/dev-artifacts/CityPrompt/details-only-street-preview-local-2026-10-15.png.
The render action is enabled. No paid provider call was made. Video entry opens,
but the latest narrow-pole overhead test was rejected by the existing minimum
visible-proposal coverage check. A complete video/route is not verified by this
change; the earlier "initial clean capture" wording means attempted, not passed.

API and worker are now Live at 585621949452fbe873be5e71aebaf713c6c39289:
API dep-db8obvbbc2fs73bjtm40; worker dep-db8obq7f3r2c73eqroq0. The public readiness
check passed for database, Redis, storage, image worker and reference worker.
Frontend promotion and hosted capture verification remain pending.

## Hosted checks and preview thumbnail correction

Frontend d9fd4227326bad7015e609d173cbc6902ec8693b became Live in
Render deployment dep-db8oi93l550s73el3n2g. The cache-busted public version endpoint
matches that commit. In the isolated live fixture
https://www.cityprompt.ca/projects/1bb8c4cb-93df-4c88-b1c4-bfa9aaea20f6,
RRFB and continental crossing placement on Google terrain succeeded without an
authored zone or boundary; both persisted through reload. Traffic & safety and
Curb bulbs appear separately. The live street preview includes the RRFB and the
Render action is enabled. No paid call was made. Screenshots:
C:/dev-artifacts/CityPrompt/details-live-save-reload-2026-10-15.png and
C:/dev-artifacts/CityPrompt/details-only-street-preview-live-2026-10-15.png.

A closer local view also passed the initial video source capture (the earlier
narrow-pole failure was minimum proposal coverage, not the scene inventory):
C:/dev-artifacts/CityPrompt/details-only-video-source-local-2026-10-15.png.
No complete video or paid image generation was tested in this correction.

The live aerial source check exposed an existing CSP incompatibility in QA
thumbnail creation: fetch(data:image/png;base64,...) is blocked by connect-src.
The correction decodes the capture PNG into a Blob locally before createImageBitmap;
it preserves the existing CSP, bounded thumbnails and bitmap disposal. A regression
test reproduced the failed fetch before the correction, then passed with no fetch
calls and four decoded/disposed thumbnails. All 31 capture tests and TypeScript
passed; targeted ESLint passed. Hosted verification of this last correction is
pending at this checkpoint. Flat paint may clip uneven photogrammetry; rigid
geometry and the documented minimum visible-proposal coverage remain unchanged.
