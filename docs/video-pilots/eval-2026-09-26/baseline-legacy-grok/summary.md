# Video Render evaluation · project `b457601f-ab31-42d8-9c0c-c94859abe6d7`

| attempt | provider | model | look | anchor | mode · motion · quality | fidelity | geometry | cost | prompt chars | created |
|---|---|---|---|---|---|---|---|---|---|---|
| `4a136eac` | grok_video | `grok-imagine-video` | golden_hour | no | preview_video · path_follow · high | 45 (min 44) drift | — | $0.64 |  | 2026-09-26T00:17:01 |
| `b6786b93` | grok_video | `grok-imagine-video-1.5` | blue_hour | no | multi_keyframe · path_follow · high | 78 (min 55) review | — | $1.17 |  | 2026-09-26T00:22:56 |
| `cf7674bd` | grok_video | `grok-imagine-video-1.5` | winter_morning | no | single_frame · path_follow · high | — | — | $1.13 |  | 2026-09-26T00:25:53 |
| `832523e3` | grok_video | `grok-imagine-video` | after_rain | no | preview_video · path_follow · high | 48 (min 45) drift | — | $0.64 |  | 2026-09-26T00:29:17 |

Frames sampled at 0 / 2 / 4 / 6 / 8 s. `fidelity` is the legacy appearance score; `geometry` compares depth silhouettes and is lighting-invariant.
