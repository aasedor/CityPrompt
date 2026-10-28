# Building models and ground finish repair — 28 October 2026

## Scope and decisions

The local student catalogue advertises detailed, exact building models. Existing projects must recover from an interrupted model download and from old planned-massing recipes after the matching detailed family becomes available. Large display foundations should blend with prepared-site lawn. Architectural stone, stairs, roofs, uploaded models, source GLBs, saved geometry and unknown source revisions must retain their identity.

Implemented shared recovery in both native and compiled renderers: one automatic cache retry, then the existing Retry 3D update action. Errors follow the same saved revision as the boundary lifetime. Reopen probes a registered model-backed massing proposal once; semantic incompatibility remains explicit and cannot cause a retry loop. No silent substitution of an unsupported family.

Prepared-site ground finishing now covers shallow CLAY_FOUNDATION meshes in registry-resolved RLASM assets, including podiums in repeated-storey assemblies. The complete mesh must remain between grade zero and 0.35 m; elevated or mixed-height architecture is excluded. Generic paving, floors, stone, asphalt and imported user GLBs are excluded. Exact city-hall and railway-hotel contracts preserve measured entrance strips and walks while replacing their baked display streets with site-matched lawn. Hotel dimensions come from family_hotel_baronial.py at 0dea20a092b20ac4055d66f75307827bb364a7cf, verified against the actual GLB. No source asset bytes or catalogue activation changed.

## Evidence

Local evidence: C:/dev-artifacts/CityPrompt/building-repair-20261028.

- Current catalogue: 105/105 default building planning/direct-model routes resolve.
- All 105 building GLB URLs return intact GLBs in the local runtime.
- Production catalogue closure: 578 dependencies, zero failures.
- Model Library: 111/111 storage objects present; 19/19 advertised exact hashes verified.
- Actual model geometry audit: 104 parsed in Node with finite attributes and unchanged complete bounds; 59 received site ground finishing. Charcoal Gable Fourplex requires browser image APIs and was separately placed and visually checked through the ordinary catalogue. Its Node image-decoding limitation is not an app failure.
- Browser: eight-model recovery project opened without proxy blocks; close checks of hotel and city hall preserve steps, planting and roof materials. Textured fourplex placed, automatically saved, Undo removed it, Redo restored it. Vancouver tower with an edited storey programme inspected separately.
- Error injection is covered by deterministic component tests; no browser network interception or provider calls were used.
- Final frontend suite: 3,979 tests across 469 files passed with four workers. The initial default-worker run had one catalogue UI timeout; its focused 55-test rerun and the complete reduced-worker rerun passed. Type checking and lint passed. Vite source bundle passed using the hydrated external runtime public directory and `copyPublicDir:false`; this is not a standalone asset package from the LFS-placeholder source checkout.
- Independent code review found an error/boundary revision mismatch; the final boundary key now follows the same saved revision. Final re-review reported no remaining actionable findings.

## Remaining limitations

The older manually drawn Front Elevation Day zone in Downtown - Lux Modus Demo requests halifax_painted_clapboard_row_variant_0, which has no installed exact family. Its requested shape is irregular and it is not one of the 105 current exact catalogue choices. It must remain honest massing until the user chooses an available replacement or the exact model is authored. Do not substitute the detached clapboard house for a rowhouse silently. No automatic migration of that user project was made.

Natural-ground support, every possible unsupported size, paid AI generation and complete capture acceptance were not re-certified by this repair. Architectural paving intentionally remains grey. A newly placed direct-review model can leave Focus building targeting the previously selected compiled building; recorded as a separate camera-selection follow-up. Existing Google tile refinement may be temporarily soft or absent while navigating. Local-only source changes; no push or deployment.
