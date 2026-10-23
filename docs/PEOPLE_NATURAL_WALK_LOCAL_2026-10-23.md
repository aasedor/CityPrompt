# People walking — local verification, 2026-10-23

Status: local implementation and measured browser trial. Not pushed, published or paid-AI verified.

Changes: keep immutable Walk/Idle GLBs and their body/arm animation. Correct only excess walking swing-foot height with a two-bone leg solve in the rigid skeleton frame. Rigidly foot-weighted shoe bounds limit lowering; stance, horizontal stepping and foot orientation remain authored. Unknown shoe weighting fails closed. Walking speed varies from 1.116 to 1.284 m/s and phase derives from required saved placement ID; grouping/reordering cannot synchronize or rephase actors. Running remains the existing sped-up Walk approximation. No continuous editing animation or new geometry/materials. Backend saved walking actions ask for natural weight transfer, heel-to-toe steps and opposite arm swing while retaining the captured route/speed; other actions retain their instructions.

Evidence in `C:/dev-artifacts/CityPrompt/people-walk-2026-10-23/`:

- `baseline-motion.json`, `compare-clips.mjs`: source walking versus alternative Formal clip. Same high-step legs; Formal merely reduces arm movement.
- `rejected-first-contact-test.json`: rejected ankle-only correction penetrated up to 102.17 mm. Never published. Shoe contact bounds fixed the cause.
- `contact-aware-results.json`: all 23 actual browser-loaded GLBs, 49 source/candidate times each; worst source and candidate sole penetration both -3.05792 mm. No added penetration at sampled times; source baseline tolerance remains.
- `motion-results.json`: all 23 actual GLBs, 97 times each. Peak ankle height reduced 43.16–50.28 mm. Median CPU pose time across model medians: source 4.8 ms, candidate 4.4 ms, with mixed per-model differences/noise. This is pose work only, not an FPS improvement claim or laptop/mobile/Google-tiles benchmark.
- `walk-comparison.webm`: free local WebGL before/after recording, not an AI-generated result. Actual QA page: `http://127.0.0.1:5184/people-walk-qa.html`.

Verification: 36 Vitest tests in 9 People/catalogue/thumbnail files; 13 backend saved-action tests; full completed `npm run type-check` exit0; scoped ESLint and diff check exit0. Walking action saved through actual local UI in disposable project `b5a05da9-df26-4b40-83be-1ccbaaba2293`; original three actors preserved. Automated capture tests cover absolute timeline, cancellation/restore and replacement rigs.

Independent review found strict type issues in the optional placement-ID type and an untyped fixture array. Both fixed; independent completed type-check exit0, no remaining P0/P1/P2 findings. Additional reviewer sampling: 1,201 times per model across all 23 with no skip/snap; maximum adjacent ankle step <2.73 mm at ~1.1 ms spacing. Nested rotated/nonuniform parents under ECEF matched local joint positions within 3.2e-9 m.

Limits: stylized source motion remains, with a modest correction rather than replacement mocap. No automatic pathfinding, collisions, terrain-following footsteps or running clip. No new paid AI renders, production deployment or student-device benchmark. CPU sampling and source tolerances cannot prove all possible poses or subjective realism. Original source hashes and unrelated hydrated assets unchanged.
