# Building-only placement implementation plan

User requirement: building placements contain the building, rather than a complete street/site/context illustration. Roads are authored independently. Target: `deployment-version` at `62e31ad621238c6ce1da62934710128831df3b5e`, branch `codex/building-only-20261029`.

Implementation choice: preserve immutable source GLBs and isolate complete source-connected geometry components in an owned runtime clone, using explicit exact-revision architecture bounds. Do not remove meshes by their first object's module tag: source export merges architecture and context by material. Retain building support, podiums, stairs, roofs and architectural glazing. Unknown/uploaded models keep their contents.

- [x] Inventory the 19 exact newly integrated building candidates and their source ownership; record ambiguous models visibly.
- [x] Prove CBE v004 first: failing geometry tests for removal of roads, context and landscape with preservation of main glazing, source bytes and attached steps; implement shared extraction with owned resource disposal.
- [x] Apply the same extracted geometry to native/compiled map placement, preview, ground/inspection/walking and exact capture consumers. Keep unsupported/unknown source identity unchanged.
- [x] Run narrow tests and frontend type check; inspect exact hydrated CBE geometry and its rendered browser placement, rotation, persistence and free source capture.
- [x] Extend only to candidates with source-grounded ownership contracts; retain unimplemented cases as pending rather than applying a material-name heuristic.
- [x] Record source versus runtime transformation, per-candidate review limitations, screenshots and original source captures in the existing private Drive review folder.

No paid generation, source GLB changes, wholesale catalogue JSON rewrite, unrelated source changes, push or live deployment. Native geometry scale is one. Existing plot envelopes remain unchanged unless a separate verified catalogue contract revision is required; occupied bounds and camera/ground checks must use the extracted model, not hidden roads.
