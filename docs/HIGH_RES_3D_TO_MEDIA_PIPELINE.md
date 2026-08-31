# High-Resolution 3D-to-Media Pipeline

Status: bounded implementation pilot

This pipeline intentionally has two stages:

1. CityPrompt produces a high-quality, source-locked 3D control scene in the Google Tiles environment.
2. An image or video model improves finish and atmosphere while CityPrompt retains geometry and identity authority.

The second stage is not allowed to compensate for missing massing, roof topology, openings, contacts, or source materials. Those must exist in the RLASM model before enhancement.

## Control scene

RLASM buildings keep their authored PBR material state in the globe. Direct 3D capture-pinned buildings use LOD0 even when that temporarily exceeds the normal navigation detail budget. During ordinary navigation, available GLB assets are selected by distance:

- LOD0 through 260 m
- LOD1 through 650 m
- LOD2 through 1,400 m
- LOD3 beyond 1,400 m

If the desired level is absent, CityPrompt selects the nearest authored level. It never generates a substitute material or geometry asset.

## Control bundle v2

Every high-resolution still capture now supplies a same-camera bundle:

- beauty image
- proposal mask
- semantic class-ID image and manifest
- exact instance-ID image and manifest
- renderer depth image
- renderer view-normal image
- source-material ID image and manifest
- camera projection matrix, world matrix, position, quaternion, and lens values
- capture fingerprint

All machine passes are lossless PNGs. The API verifies matching dimensions, manifest ownership, proposal coverage, and finite camera data before provider submission. Version 1 requests remain accepted for saved legacy work; new UI requests use version 2.

The material manifest identifies the source material boundaries visible in the control scene. RLASM clone materials are explicitly tagged as source-specific, and their authored PBR maps and settings remain the beauty authority. Material-ID colors are metadata and must never appear in output.

## Still-image acceptance

The provider receives beauty, semantic ownership, instance ownership, depth, normals, material boundaries, and a deterministic structural-edge guide in a single request. The prompt identifies the role and attachment order of every guide.

Server-certified source-locked RLASM instances retain the existing strict safety path:

- register the provider result to the source camera;
- evaluate structural and instance presence gates;
- restore exact source pixels for protected RLASM instances in same-camera scene output;
- mark source-locked scene and reproject results `review_required` until calibrated visual evidence supports automatic promotion;
- return a safe source-authoritative fallback when provider drift exceeds the accepted envelope.

This deliberately favors trustworthy architecture over an impressive but invented result.

## Video checkpoints

High-quality non-near-field routes capture up to six ordered checkpoints. Each checkpoint persists the same v2 geometry controls and camera data beside the deterministic 192-frame, 24 fps, eight-second preview. The provider remains conditioned by the deterministic preview video; the checkpoint controls are immutable audit and fidelity evidence.

Video fidelity now measures:

- whole-frame structural similarity at five time positions;
- the weakest score inside protected instance-ID regions;
- temporal consistency relative to the deterministic route, which detects motion pumping and unstable scene changes.

A strong average score cannot hide one missing building or a temporally unstable segment. Saved controls can be re-scored without another provider call.

## Pilot gates

Before scale-up:

1. Run the exact-source RLASM model gate and retain its independent visual review.
2. Verify the browser capture preview before any paid still render.
3. Use one still and one eight-second route as the provider pilot.
4. Inspect the source/control/output set at full resolution.
5. Keep every RLASM-protected still in review until the holistic source-locked review has zero P0 and zero P1 blockers.
6. Keep video in review if protected-instance or temporal scores fall below the stable thresholds.
7. Promote a provider/style combination only after a finite, versioned comparison set demonstrates repeatable geometry retention.

## Current constraints

- Near-field street routes currently prioritize a deterministic beauty source when close-facade semantic capture cannot satisfy proposal-coverage rules. They therefore do not yet claim geometry checkpoints.
- Geometry maps are persisted and used by the fidelity gate. The current video-provider interface accepts the deterministic route video rather than separate depth/normal channels.
- This implementation does not make a provider call during automated verification and does not consume render credits.

The next calibration unit is a source-locked RLASM pilot with one aerial still, one street still, and one high-quality route. Provider output is evidence, not acceptance; the RLASM holistic review remains the keeper authority.
