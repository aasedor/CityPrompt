# Meadow vegetation: Currie integration and two close-up renders

Local initiative: `codex/public-realm-visual-pilot`, base `fcea2259c`.
Delivery revision is the commit containing this report. User authorized trial
integration and exactly two paid close-up images; no publication requested.

## Integration

Only `neighborhood_park_v2` consumes the six vegetation prototypes. Authored
trunk positions, yaw, scale and measured support offsets are retained. Full
canopies must fit the boundary; an edge candidate can use the narrower grove
tree or be omitted. Playground and pavilion reserves also exclude canopies.
Shrubs, flowers and grasses replace whole clumps inside their existing reserved
discs. Legacy asset flags cannot switch the meadow back to old trees. Other
park variants and street trees are unchanged.

Fixture: project `54818ada-581f-4643-900a-78867b076c8c`, park
`8ea3218e-6574-49bb-9940-a957f3c289d8`, 50 x 40 m, prepared vacant Currie site.
Six trees survived boundary selection: two shade, three grove, one ornamental.
Park coordinates and saved update timestamp were unchanged by camera work.
Close views show visible branching and small leaves beside timber/charcoal
furniture. No claim of botanical species fidelity or district performance.

## Two authorized renders

Development camera controls positioned two close views in the live application;
this is camera-assisted visual QA, not evidence of novice camera usability.
Both calls used the normal UI, no people/vehicles, GPT Image 2.5 Flare.

| View | Style | Result |
| --- | --- | --- |
| Picnic table and shade tree | Photo Realistic | Detail reads well, but AI invented water from the pale prepared-site edge. Failed design checks; illustrative only. |
| Bench and meadow beds, facing inward | Documentary | Visually retains the main furniture, planting and path arrangement better. Still failed automated design checks; not approved as faithful. |

Both originals remain accessible in Project Renders with their unverified
warning; source-preserving fallbacks are also saved. Gallery increased from
two to six files. No retries or third paid call. Audit rows at
2026-09-23 00:47:15 and 00:50:39 UTC each charge 94 credits, total 188;
balance 906 -> 718. Local date was September 22.

External evidence root:
`C:/dev-artifacts/CityPrompt/sol-empty-lot-trial-2026-09-22/`.
Browser files: `91-meadow-source-preview.png`, `92-meadow-render-one.png`,
`94-meadow-second-source.png`, `95-meadow-second-render.png`.
First free exact capture downloaded successfully (988,908 bytes), preserved as
`renders/meadow-closeup-1-source.png`. Subsequent download clicks did not yield
verified local files; paid output is retained in the project and screenshots.
Do not count those clicks as a download pass. Evidence is local, not a shared
durable archive. Generated images and diagnostic scripts remain outside Git.

## Checks and limits

36 focused tests pass across meadowVegetationPlacement,
meadowVegetationGeometry and parkMicrodetailFamilies. Type-check and diff check
pass. Browser error log contains eight missing bioswale paver texture errors
(`/park-skins/bioswale-streetside/adaptive-v1/paver/albedo.jpg`); this trial is
not a clean-console pass and that adjacent asset needs a separate follow-up.
Placement tests cover full-boundary
selection, narrow-tree fallback, fixed-program exclusions and clump reserves.
React review: no conditional hooks, no new frame-loop allocation; existing
instanced geometry and deferred resource disposal retained.

Prepared-site close-up appearance: agent-reviewed. Natural terrain, new
edit/Undo/reload matrix, route visibility in all larger variants, district FPS,
independent student usability and human visual acceptance remain untested.
The next bounded follow-up is render-fidelity diagnosis and dependable image
download, not another paid generation batch. Render beauty alone cannot close
the design-fidelity gate.
