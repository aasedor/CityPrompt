# Currie Generate to 3D native recipe repair — 20 September 2026

Scope: disposable seven-house Currie project
`54bb844c-1ff4-4d67-bc7f-0c8c36d0030e`. The protected vacant Currie
reference was not opened for editing. No paid generation or publication.

The legacy **Generate to 3D** button prepared all seven native clay families,
then the atomic `/lego-assembly/place-community` request returned 409:
"The LEGO modules used by this AI Master Plan changed while its 3D recipes
were being prepared." A repeated retry gave the same result. The transaction
saved no partial scene.

The panel's planning request omitted `native_home_plot` and transformed each
authored rectangle using generic footprint axes. The authoritative compiler
replanned the saved native plots with `native_home_plot: true` and preserved
their first-edge frontage. That changed the fit from `fixed_landmark` to
`detached_dwellings`, and changed instances. The conflict was correct; the
panel had prepared the wrong recipe. This could affect every future native
building family, not only the three families on Currie.

`communityCompiler.buildPlanRequestForItem` now supplies one shared request
for the panel and mixed Community 3D compiler. It carries the native-home flag,
authored plot axes, and explicit height, and lets each caller choose its
existing forced-fit policy. It leaves the family's native wing depth to the
planner. The server's independent catalogue and source checks remain strict.

After the change, the same UI button returned 200 and reported **seven detailed
buildings, zero massing fallbacks, two park/street layers, 8,700 m² residual
landscape and 16 trees**. Reloaded project readback had seven building records
with locked LEGO recipes, one road, one park and one boundary. After tile/model
loading, the overhead browser view showed the seven distinct homes on both
sides of the red shared street, the park, and site trees. Browser page errors
and failed HTTP responses were empty. Initial screenshots taken during ground
alignment showed only the street and park; wait for full scene readiness before
judging a candidate or taking a student presentation view. The alignment
status remained visible during this bounded check, so this is not an export or
AI-render fidelity pass.

Verification: 56 focused frontend tests and TypeScript type-check passed.
Browser baseline/request/response/after-reload JSON and screenshot are held
outside Git under `C:/dev-artifacts/CityPrompt/grounding-batch-a/generate-*`.

For each future native or fixed-size archetype, verify the panel's planning
request and the atomic compiler's locked request agree on native mode, first
edge/frontage, metric target, height and fit policy. Test Generate to 3D on a
disposable project, reload, wait for models, then inspect low and overhead
views. A successful recipe save alone does not prove visible placement.
