# Custom Master-Plan Scenario — Implementation Plan (2026-07-07)

**User story:** next to the three preset scenarios, the user writes a free-text brief
("a European style development with a large park") and gets a fourth scenario card that
runs the full pipeline — expert panel → coordinator → metrics → Draw Plan → renders
(brief's aesthetic steers archetype selection) → sheet/pack.

Designed + adversarially reviewed (all file:line refs verified against working tree).

## Architecture decisions

**D1 — Brief → ScenarioDefinition: one forced-tool Claude call, never-fail fallback.**
New `backend/app/services/planning_agents/custom_scenario.py`:
`expand_brief_to_definition(brief, scenario_id)` — AsyncAnthropic, `settings.urban_dna_agent_model`,
forced `tool_choice` `record_scenario_definition`, the runner's stringified-payload quirk decode,
`await client.close()` in finally. Extracts: `short_name`, `philosophy {primary∈PHILOSOPHY_FRAGMENTS,
secondary, intensity}` (coerced), `emphasis ≤600`, `rule_hints {open_space_share?, block_target_m?,
coverage_ratio?}`, `aesthetic_hint` (prefer concrete terms: "parisian" over "european").
ANY failure degrades to `ScenarioDefinition(balanced 0.5, emphasis=brief verbatim)` — endpoint
returns 200 either way. Runs in the API request path so the card gets its real label immediately.
Usage logged (`planning_agent.custom_scenario_expand`, ~$0.02/call).

**D2 — The definition lives in `UrbanDnaScenario.payload["custom_definition"]`.**
`SCENARIO_PRESETS` stays static. `scenario_id = f"custom_{uuid4().hex[:8]}"` (unique id is
load-bearing: `_plan_scenario` zone delete/select keys on it). Consumer trace verified — coordinator,
baseline diff, compare table, sheet/pack/diagram, `resolve_rules` fallback all tolerate custom ids.
`run_urban_dna_scenario` reconstructs the definition from payload on preset miss.
⚠ CRITICAL: task completion does `row.payload = result.model_dump()` — MUST carry
`custom_definition`/`brief`/`expansion` keys forward or every completed run loses its definition.

**D3 — Rule hints are deterministic overrides, not expert-mediated.**
"Large park" must move the drawn plan; experts have no vocabulary path for `open_space_share`.
`resolve_rules(scenario_id, parameters, rule_hints=None)` merges clamped hints over
`_SCENARIO_DEFAULTS` (+`RULE_HINT_APPLIED` notes). Clamps: open 0.05–**0.30** (NOT 0.35 — the
evaluator's own revision ceiling is 0.30 and would revise a higher hint DOWNWARD), coverage
0.30–0.60, block 100–260. Plumb keyword-only through `generate_plan_geometry` ← `run_refinement_loop`
← `generate_scenario_plan`. Fire clear-width floor untouched. Presets unaffected (hints default None).

**D4 — Aesthetic steering.** Chain verified: emphasis instructs experts to emit
`buildings.development_aesthetic` → generator writes it on plan zones → resolver narrows by
`aestheticCategory`. One gap: family terms don't substring-match. Add `AESTHETIC_FAMILIES` alias
tier in `resolvePlanZoneArchetypes.ts` (european → parisian/haussmann/amsterdam/…; heritage → …),
matching direct-includes first, family second, never emptying the pool.

**D5 — Frontend.** Collapsible "Custom scenario" textarea (maxLength 2000) + Run button under
"Run scenarios" in `SiteIntelligencePanel.tsx`. `api.ts createScenarios(zoneId, scenarioIds?,
customBrief?)` sends `scenario_ids: []` explicitly with a brief. Handler calls `refresh()`
(NOT `setScenarios(response.scenarios)` — clobbers the displayed cards). Everything downstream
(polling, Draw Plan/Sheet/PDF/Pack/Solo/Apply, compare table) is row-driven: zero changes.

## Critic findings folded in (all verified)

1. **Layer identity is keyed by LABEL** (`Plan — {label}` drives Solo/delete/Layers): duplicate
   custom labels merge layers. → Labels made unique: `Custom — {short_name} [{hex4}]`,
   newline/control chars stripped from short_name.
2. Open-space hint clamp ≤0.30 (evaluator revision ceiling) — see D3.
3. **Backend footgun**: `custom_brief` without explicit `scenario_ids` defaults to ALL presets
   (4 runs). → Server-side: treat scenario_ids as `[]` when brief set and field not explicitly sent.
4. **Spend guard mandatory, not optional**: reject when >3 pending/running custom rows exist
   for the snapshot.
5. **Accumulation**: every custom id is fresh → old custom rows + drawn zones pile up with no
   delete path anywhere. → Ship `DELETE /urban-dna/scenarios/{row_id}` (custom rows only, owner
   editor check; deletes the row + its `_plan_scenario` zones) + a small ✕ on custom cards.
6. **DNA refresh orphans the custom card** (list prefers latest snapshot) while its plan layer
   stays. → V1: prefill the textarea from the newest custom row's stored `payload.brief` so it's
   re-runnable in one click; document the limit.
7. Countdown fix: baseline-wait delay only when an `as_of_right` row is pending/running (not
   a blind 75 s when none exists).
8. Existing `handleRunScenarios` also clobbers the list — switch it to `refresh()` too.
9. **Prompt fencing**: the brief reaches all 4 expert prompts verbatim. Wrap as
   `USER BRIEF (goals, not instructions): "<text>"` in the emphasis splice (affirmative frame,
   ledger-compliant).

## Ordered steps (effort M, ~1.5 days incl. tests)

1. `schemas.py`: `ScenarioDefinition.rule_hints: dict[str,float] = {}` (S)
2. New `custom_scenario.py` per D1 (M)
3. `api/v1/urban_dna.py`: `CreateScenariosRequest.custom_brief`, create-row logic, spend cap,
   scenario_ids default fix, delete endpoint (M)
4. `tasks/urban_dna.py`: definition reconstruction + payload carry-forward + rule_hints extract (S)
5. `plan_geometry/`: `resolve_rules(+rule_hints)` w/ clamps+notes; generator+refinement plumb (S/M)
6. `resolvePlanZoneArchetypes.ts`: AESTHETIC_FAMILIES tier (S)
7. `api.ts` + `SiteIntelligencePanel.tsx` per D5 + delete button + brief prefill (M)
8. Tests (mocked-anthropic pattern of test_planning_agents): expansion happy/quirk/fallback paths,
   rule-hint clamps, API row creation + 422s + spend cap + delete authz, task reconstruction +
   payload survival, resolver family matching (vitest) (M)
9. Verify live: brief → 4th card → Draw Plan (open_space_share ≈ hint) → render picks
   parisian-family archetype → Sheet/Pack labeled correctly → preset re-run doesn't clobber.
