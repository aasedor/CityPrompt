# Occlusion render pilot

Status: visibility-conditioning fix implemented and locally verified, 5 September 2026. Paid A/B trials remain pending. Local initiative: `codex/occlusion-render-pilot`.

## Implementation checkpoint

- Reuse depth-tested instance pixel counts from the fresh native capture to filter frontend references before grouping shared archetypes. The backend independently derives visibility from the submitted normalized instance image. Full project inventory, validation and source protection remain intact.
- Replace the whole-project “every instance exactly once” instruction with visible-group/visible-portion guidance. Omit park/street design identity prose that can name hidden facilities.
- Bind reference images to explicit zone IDs. Exclude hidden/unbound references and mixed visible/hidden bindings. Omit park/street catalogue compositions, even for visible zones, until component-specific conditioning is proven. Remove automatic whole-project public-realm context from Direct aerial requests. Classic rendering is unchanged.
- Local browser verification reproduced the previous north-facing street camera. The park had zero visible instance pixels; only two building-family references remained. Four houses across three building plots and the street were visible. Native capture and visibility evidence are ignored under `artifacts/occlusion-pilot/`. The camera was restored after the diagnostic capture. No paid request was made.
- Verification: 173 backend tests, 60 frontend tests and TypeScript checking passed. React review: visibility work reuses capture-time analysis; no new render-loop computation, effects or event listeners. Backend payload tests cover scene, source-anchored and reproject modes, hidden inventory, reference bindings and preservation of full validation inventory. Pixel tests cover partial/disconnected visibility, slivers, missing evidence and a later reveal.
- Remaining: paid visual A/B evaluation, finer park-component/repeated-house identities, and partial-occlusion/reveal trials. This removes a concrete source of contradictory conditioning; it does not certify that an image model will never hallucinate. Existing protected delivery and raw-AI comparison remain necessary.

The implementation below stays local until the subsequent main-branch integration. Generated evidence is not committed; source changes belong to this initiative only.

## Product rule

The student designs one persistent community. A render improves the appearance of the portion visible through the selected camera. An object outside the frame or behind another object must not be relocated, duplicated, revealed through its occluder, or replaced with another object. When the student moves the camera, previously hidden objects should become visible in their original locations. Minor finish variation is acceptable; changing the plan is not.

## Findings that determine the first experiment

The previous student trial already supplies a failure example: the north-facing street image invented park equipment behind the houses even though the designed park was behind the camera. See `STUDENT_RENDER_REVIEW_2026_09_05.md` and its ignored source/provider comparisons.

Code inspection found a contradictory instruction in `backend/app/services/direct_3d_render.py`: `_server_inventory_prompt` summarizes the full validated inventory and says “preserve every instance exactly once.” Both presentation and source-anchored requests include it. Reference collection and public-realm scene descriptions also start from all project zones. Hidden objects can therefore enter the image request through text and catalogue artwork despite being absent from the visible capture. This is a plausible contributor, not a proven sole cause.

The instance capture already keeps off-camera and fully occluded objects in its manifest with zero pixels. Manifest membership is therefore not evidence of visibility. Connected image regions are also not object counts: a foreground building can split a single park into several visible regions. Repeated houses can currently share a plot ID; a whole park ID does not distinguish its playground from its pavilion.

## 1. Prepare a reproducible, free test set

Use the existing Fort Calgary empty-field student project (`9535da89-4b5c-4839-aa7f-ccde56f1eded`) for the first views. If additional geometry is needed to fully hide a target, use a separate local test project and preserve the existing scene. Keep building and park placement fixed within each comparison. Reach views through the student camera and street-view controls, then save their exact camera settings for repetition.

For every case, save a clean native image, class/instance/depth controls, camera and scene revision, ground evidence, target identity, and an annotated expected result. Wait for Google tiles and grounding to settle. Inspect close views for floating or buried geometry before any paid submission.

| Case | Camera arrangement | Required result |
| --- | --- | --- |
| A: park behind camera | Reproduce the previous north-facing street view | No park or playground appears anywhere in the image |
| B: building outside frame | Frame the park and street with one selected house beyond the image edge | That house stays absent; another house does not acquire its identity |
| C: fully blocked building | A nearer building hides a second building completely | The rear building stays hidden; no extra roof or house appears elsewhere |
| D: partly blocked park | A building blocks the playground while another part of the park remains visible | Visible lawn/paths remain; playground is neither moved nor newly revealed |
| E: cropped or partly blocked building | Only a roof or narrow portion of a building is visible | Enhance only that visible portion; do not pull a complete building into view |
| F: reveal control | Move around the occluder or turn toward the previously hidden target | The same target appears at its authored location, with the same identity |

Zero target pixels establishes absence in the capture, not why it is absent. Distinguish off-frame from occluded using camera projection and a diagnostic target-only pass where needed. Transparent foliage, tiny visible slivers and depth-disabled overlays require explicit checks; do not guess from bounding boxes alone. Diagnostic passes must not be sent as appearance references that expose hidden geometry.

## 2. Separate project truth from image conditioning

Keep the full server-validated scene, ownership, revisions, grounding and object inventory intact for validation and audit. Derive a separate camera-specific visibility record from the depth-tested instance pixels of the exact submitted capture. Recompute it after camera or scene changes; do this at capture time rather than on every animation frame.

Use that record throughout provider request assembly:

- Describe visible portions rather than demanding that every project object appear once.
- Exclude references and generated scene descriptions belonging only to invisible objects. Retain full inventory privately for validation.
- Give references explicit target bindings. Unknown or unmapped bindings should omit optional artwork rather than silently introduce unverified objects.
- For partially visible objects, condition finish on the visible source surfaces. Full catalogue scenes can reveal hidden facilities even when their parent park is visible; initially omit these composition-heavy references. Trial cropped material references separately only if needed.
- Preserve camera framing, depth ordering and visible silhouettes. Keep the current source fallback and clearly labelled original AI attempt.

Before case D is scored automatically, introduce stable component identities for at least playground, pavilion and paths within the pilot park. Give repeated houses separate identities where needed. Preserve their parent zone relationships; the student does not need additional controls. Avoid a catalogue-wide ID migration until this one park/building pilot demonstrates the need and approach.

## 3. Run a bounded image experiment

First complete all six native captures without invoking an image/video model. Audit the assembled request to prove that hidden objects are absent from provider-facing inventories, reference attachments and generated context—not just from one prompt paragraph.

The first paid batch is **four single-image calls**:

1. Case A with current conditioning: reproducible baseline.
2. Case A with visibility-aware conditioning: identical camera, scene, style, resolution and provider settings.
3. Case C with current conditioning.
4. Case C with visibility-aware conditioning.

Keep people/vehicles and other optional additions disabled in these diagnostic comparisons. Record the exact request and raw response; do not retry silently. One sample per treatment is a pilot, not statistical proof, especially if the provider cannot hold a seed constant.

Review this checkpoint before another batch. If the intervention helps, trial cases B and D–F with the revised path, emphasizing partial occlusion and a reveal pair. Define that next batch explicitly after review. If the first batch still relocates objects, stop expanding full-scene generation and test finishing one visible object region with the foreground/context held fixed. Restore nearer occluders during composition and inspect boundary seams. Do not proceed by continually lengthening the prompt.

The earlier allowance of two aerial images, one street image and one video was consumed in the prior student review. Preserve that ledger. Reconcile prior usage against the existing US$10 total ceiling before enabling this new bounded batch; reservations are not settled charges. Count failed or uncertain requests conservatively. Use a separate cumulative ledger and a hard request cap. If the remaining allowance cannot cover the batch, complete the native tests and implementation first and report the exact remaining spending question. No new video is needed to diagnose the still-image failure.

## 4. Review fidelity and usefulness independently

For every trial, show the native source, untouched AI output, and actual delivered output side by side, with close crops around the target and occluder. Review the whole frame for relocation, including outside the site boundary.

Hard failures: an absent target appears elsewhere; a hidden feature is revealed; an object is duplicated or changes identity; an occluder disappears or moves; a cropped building expands into frame; park facilities exchange positions; camera or ground contact changes materially.

Separately score appearance: materials, glazing, vegetation, lighting, contact shadows and overall presentation quality. A beautiful but rearranged scene fails. A source fallback is a successful safeguard but an unsuccessful AI enhancement. Pixel/edge similarity scores support review; they cannot certify semantic correctness or detect every plausible replacement.

## 5. Implement regression coverage, then student verification

Add provider-free tests for zero-pixel inventory entries, partial visibility, disconnected regions of one object, repeated houses, hidden park components, reference filtering, shared references, unknown mappings and stale captures. Verify that full server validation still receives the complete scene. Test that a change in camera recomputes visibility and that failures retain both source and AI attempt.

Run focused frontend tests and TypeScript checking for production TS changes, and focused backend tests for request assembly and preservation behavior. Repeat the student flow: place objects, reshape one, move the camera, preview, render, and inspect the saved result. No additional student configuration should be needed to obtain correct occlusion handling.

Deliver the reviewed comparisons, an explicit pass/fail table, the request/cost ledger, and one coherent local implementation checkpoint. Keep heavyweight media in ignored `artifacts/` or external storage. No push, deployment or unrelated asset changes belong to this initiative.

## Subsequent video check

After the image pilot, propose a short deterministic route in which the camera passes a foreground building and reveals the park. Check both hidden frames and the reveal for persistent positions and identity. Native 3D remains the spatial authority; any AI enhancement must pass the same review across time. A video trial requires its own finite batch and remaining-budget check.
