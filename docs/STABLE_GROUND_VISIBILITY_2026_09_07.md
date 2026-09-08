# Keep the community visible during terrain refreshes

Google tile LOD changes invalidated the shared ground snapshot immediately.
Building foundations and street geometry consequently unmounted while new
measurements were collected, although saved park terrain remained visible.
Street tile masks could then expose empty holes where the roads had been.

The provider now retains the last complete, verified snapshot for display
while remeasuring the same source. Display context identity stays stable during
refreshes, avoiding unnecessary rebuilding of assemblies. Only a successful
measurement replaces that surface. Initial loading still requires verification.
A changed boundary or anchor source cannot reuse the old display surface.

Capture verification remains separate: the provider's onChange and verification
context report sampling/unavailable, with no current capture snapshot. The
public-road extension readiness marker uses this verification context too.
Failed refreshes preserve the visible design but remain ineligible for capture.

## Verification

- 54 focused tests passed across provider lifecycle, capture, building grounding,
  shared terrain, road extension and intersection geometry.
- TypeScript checking and changed-file ESLint passed.
- Regression tests cover a failed refresh, stable display identity, replacement
  only after two valid passes, stale capture rejection and boundary changes.
- Separate local QA project: `1a08a941-3391-4422-a598-10a3a6e21c63`, copied from the
  saved Currie pilot with 20 building assemblies, four roads, one park and boundary.
- Switching from oblique to top view, then focusing and panning, triggered
  sampling while all 430 non-tile proposal meshes retained their UUIDs. No
  building-grounding issues were reported after initial alignment.
- No paid renders were requested. Render eligibility was checked by tests.

The user's current Currie project was left unchanged. At inspection it contained
no site-boundary row, so boundary-dependent regression testing used the QA copy.

Screenshots are local QA output, outside Git:
`C:/dev-artifacts/CityPrompt/ground-visibility-homes.png`,
`C:/dev-artifacts/CityPrompt/ground-visibility-top-refresh.png`, and
`C:/dev-artifacts/CityPrompt/ground-visibility-pan.png`.

The site boundary defines the study area, the shared ground sampling domain and
proposal containment. It also distinguishes the redevelopment area from its
surroundings for site preparation and rendering. It is not the camera frame;
students can inspect and render close views without seeing its entire extent.
