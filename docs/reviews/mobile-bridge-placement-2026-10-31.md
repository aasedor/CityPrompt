# Mobile bridge drawing runtime review — 31 October 2026

Scope: ten existing published drawn bridge variants; source geometry, model bytes,
profile ranges and publication locks are unchanged. Runtime source 00edc125055c57daaa58bc36d79711a510081d18.

| Gate | Status | Evidence / limitation |
| --- | --- | --- |
| C1 Identity | PASS | Exact V and timber native recipe variants compiled through actual API; original IDs retained. |
| C2 Dimensions | PASS | Approximate endpoints fit existing source spans; 80 backend minimum/maximum × heading cases. No unrestricted span claim. |
| C3 Ground | PASS bounded | Prepared level QA site; existing ground and containment gates retained. Natural terrain remains unsupported. |
| C4 Freshness | PASS bounded | Shared preview/save geometry, anchor preservation and pointer-leave regressions. |
| C5 Pedestrian continuity | NOT RETESTED | No source/walking geometry changes; prior bridge reviews retain their stated walking limitations. |
| C6 Save/reopen | PASS bounded | V zone ab7bff7a-b77a-4ec1-85dd-9314e165e7fa persisted and remained compiled after reload; new timber zone 754fc0c9-f82b-471b-b957-bc47c876a66a saved/compiled. |
| C7 Recovery | PASS | Earlier short-span failure recovered through ordinary Retry after backend repair. Malformed, shifted, widened and holed sources still reject. |
| C8 Views/capture | PASS screenshots only | Mobile V and timber previews and saved V view in external evidence folder. No AI renders or new walking acceptance. |
| C9 Controls | PASS viewport/unit | 390×844 crosshair, Set end and Finish tested. Actual touch-event injection unsupported by browser; physical iOS/Android gestures NOT TESTED. |
| S1 Section | PASS | Native widths unchanged; bridge validator replaces conflicting generic width/long-axis assumption. |
| S2 Topology | PASS bounded | Two straight endpoints; unsupported automatic road/rail junctions stay unsupported. |
| S3/S4 | PASS bounded | Shared containment/collision checks retained; bridge anchors no longer pulled by kerb snapping. |
| B/P gates | N/A | No building or park variants changed. |

Evidence: C:/dev-artifacts/CityPrompt/mobile-bridge-placement-20261031/
LOCAL_FINAL_ZONE_READBACK.json, LOCAL_V_SAVED_READBACK.json,
MOBILE_V_SNAPPED_PREVIEW_FINAL.png, MOBILE_TIMBER_SNAPPED_PREVIEW.png,
MOBILE_V_SAVED_MODEL.png. These are local browser evidence, not live-site acceptance.

Verification: 247 focused frontend and 246 affected backend tests passed; type-check,
scoped ESLint/Ruff/Black and diff checks passed. Independent reviewer reran 105
frontend and 90 backend cases with no remaining P1/P2 findings. Existing ordinary
street regression coverage retained; unsupported flyover parcels explicitly reject.

User acceptance: “the bridges work great in this version”; requested publishing only
this tested bridge fix to deployment-version. Unrestricted spans remain a separate
unfinished request and are excluded from this release. No new asset/keeper approval
is inferred. CI on the integrated release head must pass before merge.
