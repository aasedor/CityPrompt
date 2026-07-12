"""Master Planner — the design intelligence that composes a whole plan.

One LLM sitting where the hardcoded scenario palettes used to be: it reads the
site's DNA, the scenario philosophy, and the expert parameters, then authors a
MasterPlanSpec — banded building character WITH variety, massing typologies,
open-space program, street character, and landscape planting structure. The
deterministic geometry engine executes the spec; the spec is persisted on the
scenario row so redraws stay reproducible.
"""

from app.services.master_planner.agent import compose_master_plan
from app.services.master_planner.spec import (
    MasterPlanSpec,
    palette_from_spec,
    validate_spec,
)

__all__ = [
    "MasterPlanSpec",
    "compose_master_plan",
    "palette_from_spec",
    "validate_spec",
]
