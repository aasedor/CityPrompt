# Currie park ground-mode recovery — 20 September 2026

## Bounded student check

The disposable UI-authored project `0320bb4f-395c-41c6-a6c0-ad28bb1572ef`
was switched through Review ground from its 1102.62 m prepared level to Follow
existing terrain. The previously reproduced local residual remained 0.623 m;
the shared provider marked eight cells unavailable while retaining usable
natural-ground coverage. The house and street remained visible, but the
neighbourhood park disappeared. The saved front entrance became
`entrance_terrain_intersection` in natural mode. Review ground could measure
zero of one park profiles, so Use measured park terrain was disabled. This is
not an acceptable natural-ground park or exact capture.

The capture guard remains strict: a partial snapshot, hidden park, or failed
entrance cannot be exported as a complete design. We did not relax it merely
because much of the site is supported. Per-proposal proof would need to cover
the park's entire draped surface and every rendered object and route, through
capture completion and subsequent terrain refinement. That work remains open.

The existing explicit prepared-level control restored the house, street, park
and saved front entrance without editing their geometry. Review entrances
again reported one generated step and a 0.05 m sidewalk-to-base fall. Free
exact 3D preview succeeded. The first prepared preview exposed a bright strip
along the near site edge. Applying the UI's measured retaining-edge option at
the same 1102.62 m level replaced that strip with a dark edge in the focused
scene and exact preview. These are **concept retaining faces**, not reviewed
structural, grading or accessible-route design; the review measured up to
3.3 m of fill and 1.1 m of cut against visible Google samples. The disposable
project is now prepared with that edge profile saved. The protected original
Currie project was not edited.

## Shared recovery contract

When a park cannot obtain repeatable terrain measurements, Review ground now
warns before Follow existing terrain that the park may be hidden. It directs
the student to move or resize onto clear measured ground and review again, or
intentionally choose a prepared redevelopment level. A focused component test
checks the disabled park-terrain action and visible recovery message. New park
variants must exercise this missing-measurement path and the prepared alternative
in their own runtime review; neither mode inherits another park's approval.

Evidence outside Git is under
`C:/dev-artifacts/CityPrompt/grounding-batch-a/`, including
`currie-park-natural-zones.json`, `currie-park-natural-start.png`,
`currie-park-restored-prepared-zones.json`, `currie-park-restored-prepared.png`,
`currie-park-restored-export-preview.png`, `currie-park-edges-applied.png`,
`currie-park-edges-focused.png`, and `currie-park-edges-export-preview.png`.
`currie-park-evidence-sha256.json` records hashes for that finite set.
This check did not use paid image generation.
