"""Master Planner — the design intelligence that composes a whole plan.

One LLM sitting where the hardcoded scenario palettes used to be: it reads the
site's DNA, the scenario philosophy, and the expert parameters, then authors a
MasterPlanSpec — banded building character WITH variety, massing typologies,
open-space program, street character, and landscape planting structure. The
deterministic geometry engine executes the spec; the spec is persisted on the
scenario row so redraws stay reproducible.
"""

from app.services.master_planner.agent import compose_master_plan
from app.services.master_planner.lego_catalog import (
    LegoArchetypeCapability,
    LegoPlanningCatalog,
    build_lego_planning_catalog,
)
from app.services.master_planner.lego_geometry import (
    LegoGeometryBindingReport,
    LegoGeometryCompatibilityError,
    bind_building_zones_to_lego,
)
from app.services.master_planner.spec import (
    MasterPlanSpec,
    PlanDiversity,
    PublicRealmPlan,
    diversity_plan_for_site,
    lego_fallback_spec,
    palette_from_spec,
    validate_spec,
)

__all__ = [
    "LegoArchetypeCapability",
    "LegoGeometryBindingReport",
    "LegoGeometryCompatibilityError",
    "LegoPlanningCatalog",
    "MasterPlanSpec",
    "PlanDiversity",
    "PublicRealmPlan",
    "build_lego_planning_catalog",
    "bind_building_zones_to_lego",
    "compose_master_plan",
    "diversity_plan_for_site",
    "lego_fallback_spec",
    "palette_from_spec",
    "validate_spec",
]
