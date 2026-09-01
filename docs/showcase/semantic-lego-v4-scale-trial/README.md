# Semantic LEGO v4 scale trial

Date: 2026-08-31

City Prompt project: `dcf919bf-7476-4fff-948b-654c350b541b`

Archetype: `historical-brick-main-street`

Method: canonical RLASM v6.1 with semantic LEGO v4 assembly

## Deterministic model result

The pilot places one source-conditioned building family into three rectangular
site envelopes. The site envelope is a capacity constraint, not an instruction
to stretch the model.

| Site envelope | Occupied frontage | Middle bays | Entrance modules | Module scale | Side margin |
| --- | ---: | ---: | ---: | --- | ---: |
| 15.0 m | 15.0 m | 2 | 1 | 1:1:1 | 0.0 m |
| 19.2 m | 19.2 m | 4 | 1 | 1:1:1 | 0.0 m |
| 30.0 m | 27.6 m | 8 | 1 | 1:1:1 | 1.2 m each side |

All three assemblies retain the locked frontage direction, fixed left and
right end modules, one required entrance, and complete repeatable middle bays.
No module, window, door, roof component, or material is scaled to fill the
site. The exact City Prompt 3D scene is shown in
[`city-prompt-exact-3d.png`](city-prompt-exact-3d.png).

## Image renders

The four authorized image calls are preserved unchanged:

- [`photorealistic.png`](photorealistic.png)
- [`survey.png`](survey.png)
- [`documentary.png`](documentary.png)
- [`development.png`](development.png)

The survey image is the clearest scale-comparison proof. The other three are
illustrative media outputs and may reinterpret storefront panels, landscaping,
or occupied program; they are not deterministic geometry evidence.

## Video comparison

Two and only two authorized provider calls were made. Both used a 2560×1440
high-quality source pass downsampled to 1920×1080, 192 fixed frames, a frozen
Google context, and six depth/normal checkpoints.

1. [`video-01-preview-edit-fidelity-57.mp4`](video-01-preview-edit-fidelity-57.mp4)
   used the deterministic City Prompt route video. City Prompt scored it
   57.3/100 (`review`). It is the better visual result, but it progressively
   invents facade and entrance-like detail.
2. [`video-02-route-keyframes-fidelity-40.mp4`](video-02-route-keyframes-fidelity-40.mp4)
   used six exact ordered City Prompt route images. City Prompt scored it
   40.3/100 (`drift`). It stays closer to the authored material character but
   loses realism and temporal detail, so it is not a keeper.

The first video remains the benchmark only because its measured score is
higher. Neither video is promoted as source-locked architectural proof.

## Process screenshots

- [`video-01-preflight-passed.png`](video-01-preflight-passed.png)
- [`video-01-result-fidelity-57.png`](video-01-result-fidelity-57.png)
- [`video-02-keyframes-preflight-passed.png`](video-02-keyframes-preflight-passed.png)
- [`video-02-result-fidelity-40.png`](video-02-result-fidelity-40.png)

## Review conclusion

The semantic LEGO implementation passes the scale behavior under test: larger
polygons add whole bays while the door-sized entrance module, end conditions,
depth, height, and all module scales remain fixed. The remaining weakness is in
the generative media stage, not the deterministic 3D assembly. The next media
iteration should prefer the deterministic preview-video control path and add a
hard entrance-instance mask or entrance-count visual gate before a provider
output can be called a keeper.
