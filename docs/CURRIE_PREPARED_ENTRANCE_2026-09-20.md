# Prepared-site native entrance continuation — 20 September 2026

## Runtime result

The previously offered Pick entrance step in 3D control assumed a current live
mesh-ground snapshot. Prepared sites render an explicitly authored level and keep
that provider inactive, so the picker could not become ready by waiting. The
shared entrance/foundation path now uses a bounded prepared-ground state derived
from the exact active site boundary and declared level. It checks native pads,
their full footprint, step picks and generated approaches against that displayed
surface. This state is for interactive placement and review only; ordinary
capture still uses its separate prepared-site guard. A mismatch after a site or
model edit cannot pass a fresh contact comparison.

Entrance review now publishes a revision for the same current prepared boundary
and level. A changed level or boundary invalidates the old review. Detailed
contact issues are checked before prepared-site export as well; a disconnected
native entrance no longer slips through just because the measured provider is
inactive. Natural-ground verification remains tied to its two measured passes.

## Live Currie student pilot

Disposable UI-authored project `0320bb4f-395c-41c6-a6c0-ad28bb1572ef` was
switched from its last natural test to an explicit 1102.62 m prepared level via
Review ground. The earlier natural-ground evidence is preserved externally.
The protected original Currie `f5bffc94-def9-4c43-942e-9ae7411872e9` matched
its pre-test zone response after reload.

The native Calgary Modern Infill House remains visible. Review entrances reports
its existing approximate plot-guide anchor at the wrong foundation edge, rather
than saying ground is still updating. Through ordinary Connections controls, a
click on the visible low native step was accepted in prepared mode and returned
an exact anchor draft (`xM=-0.639`, `yM=5.875`), without saving it. The connection
planner then reported **No clear approach within 30 m reaches that sidewalk**.
This is an unresolved route in the fresh authored layout, not a successful
sidewalk-to-door connection. A bounded test of the opposite plot rotation did
not establish a clear route; the pick was canceled and the original 90°
orientation restored through the reshape control. The save rewrote equivalent
plot vertices with small numerical differences. The current disposable project
remains prepared, with its original approximate saved entrance.

After reload, the specific entrance issue appeared without a waiting message.
The ordinary free-export action rejected the scene with the same foundation-edge
message. No render was downloaded or AI generation invoked. No browser page
errors were observed in the reload check. Visual checks were normal 1440×900
headless Chrome/SwiftShader; this is not a passing low-view connection review.

Evidence outside Git: `C:/dev-artifacts/CityPrompt/grounding-batch-a/` contains
`entrance-prepared-evidence-sha256.json` and the cited UI images/readbacks.

## Verification and next work

50 tests in 5 narrow suites passed: native step picker, entrance review,
approach geometry, review panel and building contact. They cover the authored
prepared level, mismatched/stale prepared state, actual generated approach
geometry and prior natural cases. TypeScript check and changed-file lint passed.

Next: give students a usable street-facing starting orientation or a clear
recovery when the only native door faces away from the street. Test a complete
fresh-project sidewalk-to-native-step route at normal pedestrian height. The
park/partial-ground capture gate and real image-generation review remain open.
Apply this shared mode contract to every new building variant; record its own
step location and route direction rather than reusing this house's offsets.
