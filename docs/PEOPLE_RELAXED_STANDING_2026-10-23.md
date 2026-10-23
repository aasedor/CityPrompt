# Relaxed People standing revision — 2026-10-23

User request: replace the broad standing leg pose with a natural, relaxed stance.

## Behavior

The 23 rigged people use actor-owned two-bone standing correction. Ankles sit beneath their own hips with 15 mm lateral clearance per side at 1.75 m body height. Original fore/aft foot stagger, ankle elevation, shoe rotation and rigid bone lengths remain. Walking/running and seated/lying/dancing/stretching poses do not use standing correction.

Six fixed standing people/groups have new immutable v2 GLBs and matching 3D QA thumbnails. The original v1 bytes and both seated wheelchair models remain unchanged. Stable IDs, clothing, realistic picker photographs and supported actions remain intact.

## Exact fixed derivatives

|Stable ID|New GLB SHA-256|Native width × depth × height (m)|
|---|---|---|
|people-inclusive-white-cane|1d327720b4f924faf0d69acd84c8651c7983dfcda6cec5908b5bc7bd7cb8a417|0.592547 × 1.108032 × 1.732741|
|people-inclusive-guide-dog|8cec04b26c883b5a07121fd5728409cb7d2d460764ba52941cf466dfc308bc0f|1.072623 × 1.145055 × 1.746202|
|people-inclusive-older-woman|be5efe6b7208d295711dc5145189a6f1a67acef316002e971136bb79c2837a5d|0.601194 × 0.760944 × 1.702336|
|people-inclusive-older-man-rollator|1e64d65a120c77a896cbc9aacdaa2883aac2951c33aa576f95b97f4186cd99bd|0.676442 × 1.095803 × 1.785409|
|people-inclusive-family-parent-child|414087cf41b196e1cf9c8df2d00750a554ce25606545079e00508b49ec805107|1.098881 × 0.761801 × 1.770492|
|people-inclusive-family-stroller|fa6a8b8ab013a35581bb13ae4d7f616527ce8f9ca3f861c118e59dc34359d581|0.642883 × 1.396669 × 1.855912|

`tools/people_pilot/people_model_delivery.json` records original and derivative URLs, hashes, measurements and intentional files. `build_inclusive.py --relaxed-standing --output-root <new-directory>` refuses overwriting an existing GLB. Raw/editable and generated QA evidence remain external.

## Executed checks

- 33 targeted frontend tests; 8 inclusive shape/wardrobe Python tests; 16 hosted-asset tests passed.
- Six new exact GLBs passed actual Three.js GLTFLoader, finite geometry/index, static-pose and bounds checks.
- All 16 inclusive GLB/thumbnail HTTP responses match exact hashes, including 12 new versioned files.
- Actual Edge GPU review loaded and drew all 31 People models; updated inclusive group, Maya standing and walking inspected.
- Independent review inspected all six new QA images against originals. 23 actual rigged assets preserve bone lengths (maximum change 7.13e-8 m), foot rotation (1.47e-6 rad), grounding (0.089 mm), running joints and deterministic walk-to-stand return. Parent/child hand gap 0.162 mm; aid contacts preserved.

## Release boundary and limits

This record does not claim production deployment or completed post-fix paid image acceptance. Those are recorded separately in the combined People/Claude release evidence. Original foot stagger produces some knee flex; this was inspected in the local browser. Inclusive models remain fixed authored poses; no automatic pathfinding, seat fitting or mobility-device certification is introduced. Physical student-laptop/mobile performance has not been measured for this revision.

External proof root: `C:/dev-artifacts/CityPrompt/people-relaxed-standing-2026-10-23/`.
