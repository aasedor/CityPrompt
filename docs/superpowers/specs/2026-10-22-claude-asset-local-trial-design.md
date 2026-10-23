# Claude asset local trial

User direction: retain the current CityPrompt application, import only reviewed
new RLASM 6.1 assets from Claude's branch, include parks and streets, and test
them locally before any publication. The user confirmed local testing on this
turn: “Once these are verified, please Test them locally.”

Use exact source commit `2e6f4860b75545aebe5a9cccabb845f3943ba8e9`.
The external discovery report inventories 69 source candidates. Thirty-three
have prior passing source reviews; two of those fail runtime framing because
their background geometry spans 4.8–6 km. Preserve those holds. The initial
bounded local trial therefore contains 18 buildings, four parks and nine
fixed street/bridge scenes. Source review findings remain visible. Prior
asset review does not establish classroom runtime readiness.

## Approaches

Keep the current app and use its existing local fixed-model review workflow.
This is the selected approach: it tests exact native geometry and ordinary
catalogue, selection, edit, undo and save systems without enabling unverified
assets in production. A whole-branch merge would replace unrelated app work;
permanent publication would prematurely claim runtime acceptance. Neither
fits the user's request.

## Contract

- Local development only; no production catalogue, database or object-storage
  changes, push, deployment, paid AI calls, provider changes or new resources.
- Original GLBs and source references remain immutable. New trial copies are
  verified by SHA-256 and stored outside Git in the existing local public tree.
- Stable `claude_trial_...` IDs bind the exact candidate revision. Preserve all
  existing catalogue and saved identities.
- Reuse existing fixed-native buildings and public-realm trial rendering.
  Park-only derivatives use screenshots of the actual derivative in the picker,
  rather than reference photographs containing removed buildings. Preserve park-owned geometry,
  native metre scale and +Y-up import, with the existing single conversion to
  ENU. Explicit native centering uses the current clay placement contract.
- Fixed scenes cannot stretch, bend, repeat floors or acquire invented doors,
  route connections, ramp/accessibility claims or operational features.
- Three tree-heavy parks are performance tests, not student-ready imports.
  Experimental GPU instances remain separate until independently reviewed.
- First test one building, one park and one street in a disposable local
  project with prepared level ground. Scale the trial only after that works.
- Record exact-byte loading, visual/ground/capture and edit/persistence results
  separately. Student-laptop/mobile measurements and paid AI output stay
  explicitly untested when unavailable.

## Evidence

External source audit and test evidence:
`C:/dev-artifacts/CityPrompt/claude-model-discovery-2026-10-22`.
Complete per-variant runtime review records before claiming readiness.

## Park-only correction

The user identified that surrounding reference buildings must not accompany a
park placement. Remove off-site building shells and dependent windows, doors,
trim and unsupported climbing plants only in separately hashed runtime copies.
Keep park-owned market chalets, bandstands, pavilions, stairs, terraces, gates,
glass and supported planting. Preserve immutable originals and saved exact IDs;
retire the raw context-heavy rink from new discovery. Existing paving/aprons
are retained and disclosed; this pass does not invent new boundary geometry.
Three corrected parks remain local pilots, not published keepers or laptop-ready
assets. Prince's Island has no off-site building context to remove.
