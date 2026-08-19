# The Design Director — City Prompt's urban design agent

Added 2026-08-19. Lives in `backend/app/services/planning_agents/`.

## The gap this closes

The expert panel runs four disciplines in parallel over the Urban DNA, and
`coordinator.merge_recommendations` resolves **every parameter path
independently** — argmax of `confidence x philosophy affinity`, blended when
positions agree within 15%.

That merge is correct per-parameter and unsound per-plan. Each winning value can
be individually well argued while the *set* is incoherent, because no expert
sees outside its own `parameter_scope` and nothing downstream reads the plan as
a plan. A real run:

| parameter | adopted from | value |
|---|---|---|
| `buildings.height_m` | urban designer | 27.0 m |
| `streets.row_width_m` | mobility planner | 9.0 m |
| `buildings.unit_count` | land use planner | 6,000 |

Two defensible positions produce a **3:1 canyon** nobody proposed and nobody
costed, next to a unit count **20x** what the massing can hold. The drawn-plan
evaluator would later score the result badly without being able to say why, and
the yield number would discredit every honest number beside it.

## The three parts

```
run_expert_panel ──► merge_recommendations ──► [ DESIGN DIRECTOR ] ──► diff ──► metrics
   4 experts,          deterministic,            audit → repair →
   doctrine in         per-path argmax           synthesise → reconcile
   their prompts
```

### 1. `design_doctrine.py` — the canon, as data

25 `Principle` entries (Lynch, Jacobs, Gehl, Alexander, Sitte, Cullen, McHarg,
Calthorpe, Duany transect, Allan Jacobs, Whyte, Newman, Shoup, Pressman, Krier,
Howard, plus Calgary MDP / Complete Streets / Urban Forest). Each carries:

- `statement` — the imperative, in a designer's voice
- `measure` — the testable form, naming thresholds by key
- `source` — the real attribution, shown to users
- `disciplines`, `philosophy_affinity`, `parameter_paths`

`DOCTRINE_THRESHOLDS` holds **every number the doctrine asserts, once**. The
prompt renders from it and the audit computes against it, so tuning the canon
cannot drift the audit away from what experts were told.

Experts now receive their discipline's principles (philosophy-relevant first,
byte-stable for prompt caching) and cite `principle_ids`, which flow through the
merge into `MergedParameter.principle_ids` for the WHY panel.

**Drift tests.** Thresholds annotated `aligns_with` are asserted equal to the
constant they mirror in `plan_evaluator` / `community_rules` / `plan_metrics`.
Without this the panel could advise toward a target the evaluator scores as a
failure. `test_aligns_with_annotations_are_all_asserted` makes the annotation
non-decorative.

### 2. `coherence.py` — eleven deterministic rules. No LLM.

| rule | severity | catches |
|---|---|---|
| `fire_access` | error | right-of-way under the 6 m apparatus clear width |
| `yield_plausibility` | error | unit count outside 2x of what the massing holds |
| `street_enclosure` | warning | canyon (>2:1) or void (<1:6) height-to-width |
| `height_floors_consistency` | warning | storeys and height describing different buildings |
| `mixed_use_ground_floor` | warning | mixed-use labelled, no lettable ground floor |
| `canopy_deliverability` | warning | high planting intensity in a ROW too narrow for soil |
| `context_transition` | warning | >2x prevailing context height with no step-down |
| `philosophy_band` | warning/info | scenario contradicting its own philosophy |
| `paved_canopy_conflict` | info | dense canopy over a fully sealed ground plane |
| `construction_band` | info | one storey past the walk-up cost threshold |
| `row_band` | info | arterial cross-section posing as a local street |

Each finding names the principles it enforces and carries a doctrine-legal
repair plus a **merge mode** (`at_least` / `at_most` / `set`). Modes matter:
life safety and enclosure both raise the same right-of-way, and the *binding*
constraint must win regardless of rule order.

**Repairs iterate to a fixed point.** One pass is not enough — capping storeys
to hold a missing-middle band leaves the previously-consistent height describing
a building that no longer exists, and only the second pass sees it. Bounded at
4 passes; a set still moving at the bound is reported with `converged=False`,
never silently accepted.

### 3. `design_director.py` — the synthesis voice

An LLM pass that reads the merged set, the audit findings, the site facts and
the derived metrics, then writes the organizing idea and resolves each defect.

**Bounded authority — the core contract:**

- **Numeric and enum paths**: it may only select a value an expert already
  proposed (including losing positions — reopening a merge the philosophy
  weighting decided is a legitimate design act) or the repair the audit
  computed. Anything else is discarded with a `DIRECTOR_OUT_OF_BOUNDS` note.
  It cannot author geometry.
- **Narrative paths** (`site.design_brief`, `layout.strategy`): free
  authorship. These are prose the geometry and prompt layers read as guidance,
  they cannot violate a threshold, and writing them is the reason the role
  exists.
- **Critique**: every note must cite a real `principle_id`; unresolvable
  citations are dropped, and the title is resolved from the doctrine rather
  than trusted from the model.

**After an override.** A judgement rule the director overrules stays overruled
and stays visible in `residual_findings`. But `ARITHMETIC_RULE_IDS` —
`fire_access` and `height_floors_consistency` — are reconciled regardless:
raising the storey count without restating the height leaves two numbers
describing different buildings, and the geometry engine can only draw one.

## Worked example

Same inputs as the table above, `city_policy` preset, 2 ha site, 8 m context:

```
MERGED (before)                    REVIEWED (after)
floors            = 8              floors            = 6   ← director, from an expert position
height_m          = 27.0           height_m          = 20.5 ← reconciled to the storey count
row_width_m       = 9.0            row_width_m       = 27.0 ← enclosure, binding over fire + canopy
unit_count        = 6000           unit_count        = 297  ← yield restated to the massing
                                   design_brief      = "Step the massing down to within 16 m
                                                        at edges shared with the existing
                                                        lower-scale context…"

CHARTER: "A single planted spine from the station to the creek; the tallest
frontage faces it and the fabric steps down to the west."
```

## Degradation

Matches the rest of the panel — **a design review never fails a scenario run.**

| failure | behaviour |
|---|---|
| model call fails | deterministic repairs still land; `DESIGN_DIRECTOR_UNAVAILABLE` note; charter falls back to a computed summary that says the repairs were mechanical |
| audit does not converge | `COHERENCE_UNCONVERGED` note; residual findings reported |
| director proposes an invented number | discarded, `DIRECTOR_OUT_OF_BOUNDS` note, audited value kept |
| no site area | `yield_plausibility` switches off rather than guessing |
| no built-form context | `context_transition` switches off — no context is not zero context |

## Configuration

```python
design_director_enabled: bool = True   # off → panel behaves exactly as before
design_director_model: str = ""        # empty falls back to urban_dna_agent_model
```

One extra Claude call per scenario (~8–12k in, ~1k out). Counted in the run's
`estimated_cost_usd` and covered by the existing `planning_agents_max_usd`
guard.

Persisted on the scenario row as `payload.design_review`.

## Extending it

- **New principle** → add to `PRINCIPLES`. Any number in its `measure` goes in
  `DOCTRINE_THRESHOLDS`. If it is genuinely qualitative, add its id to
  `_QUALITATIVE_PRINCIPLES` in the test suite deliberately.
- **New coherence rule** → assert it **both** fires on its defect and stays
  silent on a plan without it. A rule that cannot stay quiet trains users to
  ignore findings. Decide explicitly whether it belongs in
  `ARITHMETIC_RULE_IDS`; almost nothing does.
- **New expert** → still one literal in `registry.py`. Give it doctrine
  (`principles_for(agent_id)` must be non-empty) and a scope inside
  `PARAMETER_VOCABULARY`.

```bash
cd backend && .venv/bin/python -m pytest tests/test_design_director.py tests/test_planning_agents.py -q
```

## Working on this with an agent

`.claude/agents/urban-design-critic.md` defines a subagent that carries this
doctrine and the invariants. Use it to critique a plan's parameters, review a
diff touching `planning_agents/` or `plan_geometry/`, or add principles and
rules without breaking the drift tests.
