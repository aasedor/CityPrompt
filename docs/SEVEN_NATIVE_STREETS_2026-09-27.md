# Seven usable native streets

Branch: `codex/seven-native-streets`, starting at park checkpoint `d34a9b9da`.
The eight native parks and Basketball Long remain on `codex/custom-render-prompts`.
No push, merge, publication or paid street render is authorized.

## Scope and milestones

Preserve Main Street (23 m), Market Street (18 m), Calgary Local and saved
fixed fixtures. Implement these exact five, in this order:

1. Quiet Residential, residential-v002, 18 × 48 m reference composition.
2. Planted Shared Lane, shared-v001, 14 × 40 m reference composition.
3. BRT Transit Mall, brt-v004, 40 × 100 m reference; explicit station programs.
4. Amsterdam Canal, canal-v005, 36 × 80 m reference; water/bank ownership.
5. Tied-Arch Gateway Bridge, bridge-v003; measured 84 m structural span,
   24 m endpoint section and 4.3 m deck, within a 36 × 100 m inspection fixture.

Use a shared, immutable native street contract, with specialist capabilities.
Preserve original assets and source recipes. Recover complete authored surfaces,
edging, furnishings and programs; never stretch or repeat whole preview GLBs.
Verify each native reference composition before scaling, then longer/reversed
routes, supported joins, recovery, persistence and exact export. Unsupported
specialist geometry must receive actionable rejection, retaining the saved design.

## Evidence and current state

External evidence and persistent detailed log:
`C:/dev-artifacts/CityPrompt/streets-runtime-2026-09-26/PROGRESS.md`.
The supplied review archive has SHA-256
`1234404b3738bf4c247d0d51968d36455503b12e4684e877712ab4cbfd7f63db`.
Five whole assemblies, 20 target modules and 15 specialist source scripts match
their recorded hashes. Main/Market baseline module bounds and the 44-family
capability catalogue are preserved. These are asset checks, not runtime passes.

First reproduced defect: drawing an 18 m diagonal Market route used a different
buffer from road editing, producing 17.548 m perpendicular width and 2.003 m
end-cap skew. Drawing, editing and street-view line preparation now share the
metric-normal helper. Existing saved polygons are not changed on load.

The shared foundation now also preserves unchanged saved family recipes through
catalogue additions, using finite historical capability locks and canonical
revalidation. It retains all native Main/Market components, removes long-route
cycle thinning, and checks complete module bounds with coupled tree/well clipping.
Repeated meshes use instancing, preserving source materials and transforms.
SHA-verified asset loading and expected-instance capture checks reject absent,
stale, corrupt or incompletely mounted street programs; Retry 3D update recovers
failed loads without accepting late errors for moved/deleted objects.

Verification: 39 focused frontend tests, 98 backend recipe tests, TypeScript and
production build passed. Fresh production browser at localhost:4181 reopened the
disposable eight-park/Market scene and exported its exact current view; no page
errors, only the ordinary elevation log. Evidence: `shared-baseline-top.png` and
`shared-baseline-export.png`. This is a bounded Market regression smoke, not a
pass for the five new streets or every Main/Market workflow. No paid calls.

Next: recover Residential's complete native composition through an explicit source
adapter. Remaining five-street runtime integration and browser checks are pending.
