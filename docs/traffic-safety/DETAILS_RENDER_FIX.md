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
