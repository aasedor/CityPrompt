# Independent neighbourhood park v2 — final scoped addendum

Reviewer: park_reference_review, independent of implementation. Date: 2026-09-05.

**Result: functional pilot supported for the inspected cases; source-quality keeper not approved.** Review scope is `category_closure_only`. The candidate remains local and requires further visual refinement; this grants no production/catalogue promotion.

This addendum follows `independent-review-v2.md` without changing its failed-evidence decision. The earlier frames are preserved in `review-v2-before-depth-fix`. I opened all nine regenerated canvas frames, their nine verified UI frames, the Google beauty/top captures, and the AI presentation preview directly. `review-evidence.json` and selected camera, terrain-quality and access fields of `google-capture.json` were inspected as supporting evidence. Exact hashes are below.

## Closed findings and visible functional result

- **The P0 overhead surface breakup is closed in the regenerated evidence.** All four overhead cases now show continuous lawn, loop, approaches and pads. Code confirms logarithmic depth buffering matches the live globe; the pixel result, not that setting alone, closes this category.
- The irregular test is now visibly a rotated L-shaped site; code applies 0.38 radians. All supplied modules remain within the useful site area.
- 40 x 35 m gives one tower and pavilion, with explicit swing omission. The 70 x 55 m and 105 x 75 m cases retain two towers, pavilion and swing. Lawn and paths grow; equipment retains its proportions. The rotated L retains two towers and pavilion and reports the omitted swing.
- The pavilion has a central-high gabled roof and visible picnic table. Flat and synthetic-slope details show equipment on level pads and approaches meeting pad edges. Code now seats tower rails on the module pad datum; visible rail contacts are improved. This is not an every-post survey or safety certification.
- The source's dominant lawn, enclosing circulation and rustic timber activity character remain recognisable across cases. The aerial source pair still owns topology; equipment differences in the ground source remain an explicitly inferred interpretation.

## Google context evidence

`top-live.png` visibly shows a diagonal park entrance from the northern sidewalk to the internal loop, passing between the activity pads. It does not cut through a pavilion or play pad. The access snapshot records one 2.2 m sidewalk connection and agrees with this visible route.

`beautyImageBase64.png` shows the proposed park on an open site among nearby planned streets/buildings and retained Google context. At this aerial scale it has no obvious floating slab or large broken ground surfaces. Ground metadata records 1,190 samples, two stable passes and zero maximum pass delta; these describe capture stability, not surveyed ground accuracy. Maximum recorded local residual is about 0.165 m.

The cold pedestrian-camera Google tile-loading limitation remains open. No actual Google pedestrian/contact close was supplied. Synthetic slope detail cannot close that provider/terrain scope, nor prove every sidewalk-height transition in the real site.

## AI appearance trial

`ai-presentation-preview-v1.png` makes foliage, lawn, lighting and surroundings substantially more convincing. It preserves the broad park concept, but reframes/enlarges the park, alters apparent camera/composition, changes visible building/equipment detail and increases canopy occlusion. The result cannot be registered as the same verified scene merely because the general layout is recognisable.

**Classification: useful illustrative appearance experiment; rejected as a geometry-faithful final-render proof.** It came from a separate built-in image-edit trial, not a validated run through the application render backend. Do not use it to claim the application's consistency problem is solved. Keep the deterministic 3D capture as design authority and test bounded, camera-registered polishing with depth/identity guidance separately.

## Remaining source-quality work

**P1 finish findings remain open for keeper quality:** repetitive crown heights/shapes and angular branch fans; isolated flower clumps instead of coherent layered meadow/shrub beds; simplified gravel/material transitions and activity-edge construction. The Google view also reads darker/flatter than the isolated lab, so lighting/material response should be compared in the target renderer. These are finite refinements to this pilot, not a reason to discard the adaptive layout.

The complete keeper evidence package, including source-matched opposite views, close ground transitions, phone comparison and faithful final-render validation, has not been supplied. Consequently this is a reviewed functional pilot with remaining visual work, **not** `keeper_approved` or broadly validated arbitrary-shape/terrain support.

Only this ignored addendum was written. No source edits, commits or pushes were performed by this reviewer.

## Exact reviewed evidence (SHA-256)

The following hashes were computed after direct inspection of the regenerated files.

| File | SHA-256 |
| --- | --- |
| ai-presentation-preview-v1.png | F6722E5A06B4D9828F82D8AD5C3570957313272B29CBCAD8E53BCB959CF37ACA |
| beautyImageBase64.png | 2EA183BFCDCA5FF61D94DC04C93937E8910AA4C52A01626322AA820CAD696BD0 |
| canvas-compact-aerial-slope.png | 5FEAE0D94E8B4A62AD617A1594FC3D2CB5D653FC5EE9E2031E95242DDEA7A8B5 |
| canvas-compact-overhead-flat.png | 75E5EA89DD9FB1738D4B4103025A1C7F9976519E8F018215375F5BD400E39F6B |
| canvas-irregular-overhead-flat.png | 6985A1590D6BC790E665AF9A35999A493A68D62A1BF65F9F1C856A7B2453C0E8 |
| canvas-large-overhead-flat.png | 1377263EE764F117013F01F0C24F390F8DC6469B1302A9BED074386E3445E27C |
| canvas-standard-aerial-flat.png | CE575BFD04AE895E0EB2532429C0DE9F70EECD766AD9B584FF79088716A58E11 |
| canvas-standard-detail-flat.png | 9E19BC2B94F09CC4E691FB957AA0B6B5A0D53ED1EA013F168A0F143357EF78FE |
| canvas-standard-detail-slope.png | 920C13791A34E04A13CAE26562790719E60C1B3F08B56DCB8506B3A5DC9C90AF |
| canvas-standard-overhead-flat.png | 45C01B408725E826AA1F902F6F167DE4B7C7BDE91D204D32D10BFCFAD7A8D214 |
| canvas-standard-pedestrian-view-flat.png | 44893B0A80760694FC08F55527BC5B661F9B262316F18360ED3DF2E11C11DC96 |
| google-capture.json | AC6098CD787E1CCDDEF6F64FCD0E6BA8D5041704B1746C6CBFFBFFC6CC5B0AAD |
| review-evidence.json | 01DC8B9B8E5F31CA3544B1D10897F6ABADFD82C8B36D84BEB2EC95F563C69264 |
| top-live.png | 8864B07B913588DB70AC37A929387F9C3459216ADD9D7AF37925B8BC31CD6D0A |
| verified-compact-aerial-slope.png | FD341D8EAED2174AE7A049CB5544B8E047119B3B235A9064AE6B44AEA48DF353 |
| verified-compact-overhead-flat.png | 72D2C5B65E4E94234A08CF6FC5DCB0EDA61753435C6F57D38D4D6B49CF5BA3EC |
| verified-irregular-overhead-flat.png | 07C480BB46020679234BF436DFAA463703BF5E647FCF02295D779A6BE28FA7FF |
| verified-large-overhead-flat.png | 6ECB72D3D762ED710EC318753DF55E0EE289C4F0B57C27464E06B83DBCEDB58A |
| verified-standard-aerial-flat.png | 46477E8833A41942196EE11E16D2A0C0D7C51F06433D32971C20356823956BCE |
| verified-standard-detail-flat.png | B5E2AE7DB520CFE5C5AC82DCA948DF1DA23AADE9527049C43BF494C29CA15C84 |
| verified-standard-detail-slope.png | C932B43F365880B31C05757B1F7B729B626426A951B163BEC737732E3A2905A0 |
| verified-standard-overhead-flat.png | 53EAB4119EE4E3293F2E5D96BB79EBC3FF82070CF3C2FC32E71B5A3C33A425BA |
| verified-standard-pedestrian-view-flat.png | 69FD3B0FEA712A0546CC097827972C5EF59AB9F0716DA0AF37BB83389D3DE6D3 |
