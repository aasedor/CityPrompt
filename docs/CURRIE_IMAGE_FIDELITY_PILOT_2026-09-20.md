# Currie mixed-scene image fidelity pilot — 20 September 2026

One bounded, paid image request was made from the disposable UI-authored Currie
project `0320bb4f-395c-41c6-a6c0-ad28bb1572ef`. The protected original
`f5bffc94-def9-4c43-942e-9ae7411872e9` was untouched. The isolated backend
used its local database/storage and only the existing OpenAI and Maps keys;
other provider and production service credentials remained disabled. This
trial did not modify source geometry or retry the paid request.

The exact free export and the paid image used the same 1440 × 836 oblique
camera. The selected style was Photo Realistic, with people/vehicles off and
the default precise fidelity policy. Account discovery selected
`gpt-image-2.5-flare`. The request returned HTTP 200 and consumed 138 local
City Prompt credits (4,260 → 4,122). The server retained both the provider
original and an authoritative clean-3D fallback in the disposable project's
saved renders. The UI explicitly said the AI finish failed design checks,
showed the source beside the fallback, and offered the original only through
an **unverified** inspection/download view. No automatic retry occurred.

Visual comparison: the provider image is a strong aerial illustration. It
keeps one flat-roof house to the left of the linear corridor and the circular
park to its right at approximately the authored scale and position. It adds
photographic context, planting texture and shadows. It also changes the large
flat prepared-ground surface to scrub/grass and makes the red six-metre shared
street read more like a pedestrian path; the exact source already gives this
street ambiguous vehicle semantics at this camera distance. The runtime
contract deliberately defines a Dutch woonerf: 0.3 m flush edges around a
5.4 m red-brown brick lane, with no raised curb or standard lane markings.
Planters and bollards are intentional chicane cues, so a pedestrian character
alone does not establish a rendering defect. The image needs a closer view
to confirm a continuous vehicle-clear route and whether the road reaches a
plausible external connection. This single image
is useful as an illustrative image after human comparison, not proof that
faithful AI imagery is dependable for students yet.

The automated evidence agrees with retaining the caution: all three evaluated
authored instances were present (weakest recall 0.795); macro silhouette-edge
recall was 0.579 against the 0.8 minimum, semantic-edge recall 0.691 against
0.78, and candidate coarse-edge density 4.66 against maximum 3. One small
unsupported structure component was also detected (147 pixels). The returned
strategy was `authoritative_source`, with `review_required` and the provider
original preserved for inspection. Do not relax these shared limits from one
visually attractive image or relabel the unverified original as faithful.

QA evidence, kept outside Git: `C:/dev-artifacts/CityPrompt/grounding-batch-a/image-fidelity-one-call/`
contains `exact-source.png`, `provider-original.png`,
`saved-fallback.png`, UI screenshots, and a scrubbed diagnostics summary.
The full provider response is local-only and may contain generated image data.

The subsequent [street access check](CURRIE_SHARED_STREET_CONNECTION_CHECK_2026-09-20.md)
found a visible shared surface but no authored public-road junction. Complete
the design's off-site link through ordinary controls before using this scene
as a vehicle-access example. A new paid image check is appropriate only after
a source change that warrants it. A future building/street/park
candidate must compare an exact source image with any AI result for count,
outline, location, dimensions, access, material/function and unwanted additions.
Record whether the result passed automatically, needs human review, or falls
back; do not transfer this scene's outcome to a new variant.
