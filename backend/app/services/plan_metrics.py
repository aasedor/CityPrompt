"""Yield & Metrics Engine — every planning number DERIVED, never estimated.

Pure arithmetic over Urban DNA facts + scenario PlanParameters. Each metric is
a DerivedMetric carrying its formula with the actual numbers substituted, the
input names it consumed, the stated assumptions, and a confidence that reflects
both input confidence and how many assumptions stand between data and number.

Two modes:
- parameter mode (P1): massing derived from site area x shares x coverage —
  used before a plan is drawn;
- geometry mode (P2+): the same metrics recomputed from drawn plan geometry
  (real block/parcel/building areas), which supersedes parameter mode.

LLM experts never touch this module; the coordinator's PlanParameters are the
only scenario-dependent inputs.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# --- Documented assumptions (each cited in the metrics that use it) ----------
# Values are deliberately conservative and Calgary-flavoured; each carries a
# label so the UI/export can disclose it. Changing one changes derivations
# everywhere consistently.
ASSUMPTIONS: dict[str, dict[str, Any]] = {
    "internal_row_share": {
        "value": 0.22, "unit": "ratio",
        "note": "internal streets/lanes consume ~22% of gross site area (typical inner-city grid)",
    },
    "open_space_share_default": {
        "value": 0.10, "unit": "ratio",
        "note": "minimum public open space share of gross area (MDP open-space direction)",
    },
    "coverage_ratio_default": {
        "value": 0.50, "unit": "ratio",
        "note": "building footprint coverage of net developable block area (perimeter-block form)",
    },
    "residential_efficiency": {
        "value": 0.82, "unit": "ratio",
        "note": "net sellable/rentable residential area per gross floor area",
    },
    "avg_unit_area_m2": {
        "value": 75.0, "unit": "m2",
        "note": "blended average unit size (mix of studios-3bd, inner-city)",
    },
    "persons_per_unit": {
        "value": 1.7, "unit": "persons",
        "note": "average household size, Calgary inner-city (census-informed)",
    },
    "nonresidential_share_mixed_use": {
        "value": 0.15, "unit": "ratio",
        "note": "ground-floor commercial share of GFA when development_type=mixed_use",
    },
    "parking_ratio_default": {
        "value": 0.50, "unit": "stalls/unit",
        "note": "structured parking ratio, transit-rich inner city",
    },
    "parking_ratio_climate": {
        "value": 0.25, "unit": "stalls/unit",
        "note": "reduced ratio under climate-first/TOD scenarios",
    },
    "floor_height_m": {
        "value": 3.2, "unit": "m",
        "note": "storey-to-storey height used to convert heights <-> floors",
    },
    # LAP Building Scale categories -> storey ceilings (Guidebook for Great
    # Communities Map categories). Used ONLY when the land-use district carries
    # no numeric ceiling — the derivation says so explicitly.
    "lap_storeys_by_category": {
        "value": {"limited": 3, "low-modified": 4, "low": 6, "mid": 12, "high": 26, "highest": 40},
        "unit": "storeys",
        "note": "LAP Building Scale Map storey ceilings; 'highest' capped at 40 for math",
    },
}


class DerivedMetric(BaseModel):
    key: str
    label: str
    value: Optional[float] = None
    unit: str = ""
    derivation: str = ""                 # formula with the actual numbers substituted
    inputs: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)   # ASSUMPTIONS keys used
    confidence: float = 0.5
    mode: Literal["parameter", "geometry"] = "parameter"

    def rounded(self) -> "DerivedMetric":
        if self.value is not None:
            if abs(self.value) < 10:        # FAR-scale ratios need 2 decimals
                self.value = round(self.value, 2)
            elif abs(self.value) < 100:
                self.value = round(self.value, 1)
            else:
                self.value = round(self.value)
        return self


class MetricsReport(BaseModel):
    scenario_id: str
    mode: Literal["parameter", "geometry"] = "parameter"
    metrics: dict[str, DerivedMetric] = Field(default_factory=dict)
    ceiling_reconciliation: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    assumptions_used: dict[str, dict[str, Any]] = Field(default_factory=dict)

    def add(self, metric: DerivedMetric) -> DerivedMetric:
        self.metrics[metric.key] = metric.rounded()
        return metric


# --- Input extraction ---------------------------------------------------------

def _dna_field(dna: dict[str, Any], section: str, field: str) -> tuple[Any, float]:
    """(value, confidence) of a DNA field from a serialized UrbanDNA dict."""
    node = (((dna.get(section) or {}).get("fields") or {}).get(field)) or {}
    return node.get("value"), float(node.get("confidence") or 0.0)


_FLOORS_RE = re.compile(r"(\d+)\s*(?:-\s*(\d+))?")


def coerce_floors(value: Any, floor_height_m: float) -> tuple[Optional[float], str]:
    """PlanParameters floors/height can be numeric or expert prose ('6-16 storeys,
    stepped'). Derive a single working number honestly: the MIDPOINT of a range.
    Returns (floors, how)."""
    if isinstance(value, (int, float)):
        return float(value), f"floors parameter = {value}"
    if isinstance(value, str):
        match = _FLOORS_RE.search(value)
        if match:
            low = float(match.group(1))
            high = float(match.group(2)) if match.group(2) else low
            mid = (low + high) / 2
            how = f"floors parameter '{value}' -> midpoint of {low:g}-{high:g} = {mid:g}"
            return mid, how
    return None, f"floors parameter {value!r} not interpretable"


def _scenario_param(parameters: dict[str, Any], path: str) -> Any:
    merged = parameters.get(path)
    if isinstance(merged, dict) and "value" in merged:
        return merged["value"]
    return merged


# --- Ceiling reconciliation ---------------------------------------------------

def reconcile_ceilings(
    districts: list[dict[str, Any]] | None,
    lap_building_scale: Any,
    proposed_floors: Optional[float],
    floor_height_m: float,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Per-district ceiling check. Where the district has numeric far/height use
    it; else fall back to the LAP building-scale category and SAY SO."""
    reconciliation: list[dict[str, Any]] = []
    warnings: list[str] = []
    lap_map = ASSUMPTIONS["lap_storeys_by_category"]["value"]

    lap_storeys = None
    if isinstance(lap_building_scale, str):
        lap_storeys = lap_map.get(lap_building_scale.strip().lower())

    for district in districts or []:
        code = district.get("code")
        pct = district.get("area_pct_of_site")
        height_m = district.get("height_m")
        far = district.get("far")

        ceiling_floors = None
        source = None
        if height_m:
            ceiling_floors = float(height_m) / floor_height_m
            source = f"district height ceiling {height_m}m / {floor_height_m}m per storey"
        elif lap_storeys:
            ceiling_floors = float(lap_storeys)
            source = f"no numeric ceiling in district {code}; LAP building-scale '{lap_building_scale}' allows ~{lap_storeys} storeys"
        else:
            source = f"no numeric FAR/height in district {code} and no LAP building-scale available"
            warnings.append(f"{code}: ceiling unknown — conformance not assessable from data")

        status = "unknown"
        if ceiling_floors is not None and proposed_floors is not None:
            status = "within" if proposed_floors <= ceiling_floors + 0.01 else "exceeds"

        reconciliation.append({
            "district": code,
            "area_pct_of_site": pct,
            "far_ceiling": far,
            "height_ceiling_m": height_m,
            "ceiling_floors": round(ceiling_floors, 1) if ceiling_floors else None,
            "proposed_floors": proposed_floors,
            "status": status,
            "source": source,
        })

        if status == "exceeds":
            warnings.append(
                f"{code} ({pct}% of site): proposed ~{proposed_floors:g} storeys exceeds "
                f"~{ceiling_floors:g}-storey ceiling ({source}) — would require relaxation/amendment"
            )
    return reconciliation, warnings


# --- Main entry ----------------------------------------------------------------

def compute_metrics(
    *,
    scenario_id: str,
    dna: dict[str, Any],
    parameters: dict[str, Any],
    geometry_inputs: dict[str, float] | None = None,
) -> MetricsReport:
    """Derive the scenario's statistics table.

    geometry_inputs (P2+, geometry mode) overrides the parameter-mode shares:
      {"net_block_area_m2", "open_space_area_m2", "row_area_m2",
       "building_footprint_m2", "gfa_m2"?}
    Passing only {"site_area_m2": ...} keeps parameter mode (the site area is a
    required input either way; UrbanDNA v1 does not persist it).
    """
    is_geometry = bool(geometry_inputs) and any(
        key in geometry_inputs
        for key in ("net_block_area_m2", "building_footprint_m2", "row_area_m2", "gfa_m2")
    )
    report = MetricsReport(scenario_id=scenario_id,
                           mode="geometry" if is_geometry else "parameter")

    floor_height = ASSUMPTIONS["floor_height_m"]["value"]

    site_area, site_conf = _dna_field(dna, "site", "parcel_count")  # confidence anchor only
    # Site area from the DNA site section is stored via zone geometry at build
    # time; derive from districts coverage if absent.
    area_value, area_conf = _dna_field(dna, "site", "area_m2")
    if not area_value:
        # UrbanDNA v1 doesn't persist site.area_m2 — callers must pass it via
        # geometry_inputs or the DNA site_boundary polygon area computed upstream.
        area_value = (geometry_inputs or {}).get("site_area_m2")
        area_conf = 1.0 if area_value else 0.0
    if not area_value:
        report.warnings.append("site area unavailable — metrics cannot be derived")
        return report

    gross = float(area_value)
    report.add(DerivedMetric(
        key="site_area_m2", label="Gross site area", value=gross, unit="m2",
        derivation="site boundary polygon area (UTM)", inputs=["site_boundary"],
        confidence=area_conf or 1.0, mode=report.mode,
    ))

    districts, districts_conf = _dna_field(dna, "land_use", "districts")
    lap_scale, _ = _dna_field(dna, "land_use", "lap_building_scale")

    floors_param = _scenario_param(parameters, "buildings.floors")
    floors, floors_how = coerce_floors(floors_param, floor_height)
    if floors is None:
        height_param = _scenario_param(parameters, "buildings.height_m")
        height_value, height_how = coerce_floors(height_param, floor_height)
        if height_value:
            floors = float(height_value) / floor_height
            floors_how = f"{height_how}; /{floor_height} m per storey"
    if floors is None:
        floors = 4.0
        floors_how = "no interpretable floors/height parameter; conservative default 4 storeys"
        report.warnings.append(floors_how)

    development_type = str(_scenario_param(parameters, "buildings.development_type") or "mixed_use")

    # --- land budget -----------------------------------------------------------
    if is_geometry:
        row_area = geometry_inputs.get("row_area_m2", 0.0)
        open_area = geometry_inputs.get("open_space_area_m2", 0.0)
        net = geometry_inputs.get("net_block_area_m2", max(gross - row_area - open_area, 0.0))
        footprint = geometry_inputs.get("building_footprint_m2", 0.0)
        land_inputs = ["drawn plan geometry"]
        land_assumptions: list[str] = []
        land_derivation = (
            f"drawn plan: gross {gross:,.0f} − streets {row_area:,.0f} − open space "
            f"{open_area:,.0f} = net blocks {net:,.0f} m²"
        )
        footprint_derivation = f"sum of drawn building footprints = {footprint:,.0f} m²"
        land_conf = 0.9
    else:
        row_share = ASSUMPTIONS["internal_row_share"]["value"]
        open_share = ASSUMPTIONS["open_space_share_default"]["value"]
        coverage = ASSUMPTIONS["coverage_ratio_default"]["value"]
        row_area = gross * row_share
        open_area = gross * open_share
        net = gross * (1 - row_share - open_share)
        footprint = net * coverage
        land_inputs = ["site_area_m2"]
        land_assumptions = ["internal_row_share", "open_space_share_default", "coverage_ratio_default"]
        land_derivation = (
            f"{gross:,.0f} × (1 − {row_share} streets − {open_share} open space) = {net:,.0f} m²"
        )
        footprint_derivation = f"net {net:,.0f} × coverage {coverage} = {footprint:,.0f} m²"
        land_conf = 0.6  # parameter mode carries assumption risk

    report.add(DerivedMetric(
        key="net_developable_m2", label="Net developable block area", value=net, unit="m2",
        derivation=land_derivation, inputs=land_inputs, assumptions=land_assumptions,
        confidence=land_conf, mode=report.mode,
    ))
    report.add(DerivedMetric(
        key="open_space_m2", label="Public open space", value=open_area, unit="m2",
        derivation=("sum of drawn open-space polygons" if is_geometry
                    else f"gross × {ASSUMPTIONS['open_space_share_default']['value']}"),
        inputs=land_inputs,
        assumptions=[] if is_geometry else ["open_space_share_default"],
        confidence=land_conf, mode=report.mode,
    ))
    report.add(DerivedMetric(
        key="building_footprint_m2", label="Building footprint", value=footprint, unit="m2",
        derivation=footprint_derivation, inputs=land_inputs,
        assumptions=[] if is_geometry else ["coverage_ratio_default"],
        confidence=land_conf, mode=report.mode,
    ))

    # --- GFA / FAR ---------------------------------------------------------------
    gfa = (geometry_inputs or {}).get("gfa_m2") or footprint * floors
    gfa_derivation = (
        f"footprint {footprint:,.0f} × {floors:g} storeys ({floors_how}) = {gfa:,.0f} m²"
        if not (geometry_inputs or {}).get("gfa_m2")
        else "sum of drawn building footprints × their storeys"
    )
    report.add(DerivedMetric(
        key="gfa_m2", label="Gross floor area", value=gfa, unit="m2",
        derivation=gfa_derivation, inputs=land_inputs + ["buildings.floors"],
        assumptions=[] if is_geometry else ["coverage_ratio_default"],
        confidence=min(land_conf, 0.8), mode=report.mode,
    ))
    far = gfa / gross if gross else None
    report.add(DerivedMetric(
        key="far_achieved", label="Site FAR achieved", value=far, unit="FAR",
        derivation=f"GFA {gfa:,.0f} / gross {gross:,.0f} = {far:.2f}",
        inputs=["gfa_m2", "site_area_m2"], confidence=min(land_conf, 0.8), mode=report.mode,
    ))

    # --- residential program -------------------------------------------------------
    nonres_share = ASSUMPTIONS["nonresidential_share_mixed_use"]["value"] if development_type == "mixed_use" else 0.0
    res_gfa = gfa * (1 - nonres_share)
    efficiency = ASSUMPTIONS["residential_efficiency"]["value"]
    unit_area = ASSUMPTIONS["avg_unit_area_m2"]["value"]
    units = res_gfa * efficiency / unit_area
    report.add(DerivedMetric(
        key="units", label="Dwelling units", value=units, unit="units",
        derivation=(f"GFA {gfa:,.0f} × (1 − {nonres_share} non-res) × {efficiency} efficiency "
                    f"/ {unit_area} m² per unit = {units:,.0f}"),
        inputs=["gfa_m2", "buildings.development_type"],
        assumptions=["residential_efficiency", "avg_unit_area_m2"]
        + (["nonresidential_share_mixed_use"] if nonres_share else []),
        confidence=min(land_conf, 0.7), mode=report.mode,
    ))

    persons = ASSUMPTIONS["persons_per_unit"]["value"]
    report.add(DerivedMetric(
        key="population", label="Population at build-out", value=units * persons, unit="people",
        derivation=f"{units:,.0f} units × {persons} persons/unit",
        inputs=["units"], assumptions=["persons_per_unit"],
        confidence=min(land_conf, 0.65), mode=report.mode,
    ))

    parking_key = "parking_ratio_climate" if scenario_id == "climate_first" else "parking_ratio_default"
    ratio = ASSUMPTIONS[parking_key]["value"]
    report.add(DerivedMetric(
        key="parking_stalls", label="Parking stalls", value=units * ratio, unit="stalls",
        derivation=f"{units:,.0f} units × {ratio} stalls/unit ({parking_key})",
        inputs=["units"], assumptions=[parking_key],
        confidence=min(land_conf, 0.6), mode=report.mode,
    ))

    # --- ceiling reconciliation ------------------------------------------------------
    reconciliation, ceiling_warnings = reconcile_ceilings(
        districts if isinstance(districts, list) else [],
        lap_scale, floors, floor_height,
    )
    report.ceiling_reconciliation = reconciliation
    report.warnings.extend(ceiling_warnings)
    if not districts:
        report.warnings.append("no district data — ceiling reconciliation skipped")

    used = {key for metric in report.metrics.values() for key in metric.assumptions}
    used.add("lap_storeys_by_category")
    report.assumptions_used = {key: ASSUMPTIONS[key] for key in sorted(used) if key in ASSUMPTIONS}
    return report
