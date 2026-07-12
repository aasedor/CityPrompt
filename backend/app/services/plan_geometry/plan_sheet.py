"""Plan sheet — the council-ready deliverable, as self-contained printable HTML.

The drawing is real SVG linework in site-local metres (measurable, not a
render), followed by the derived statistics with their derivations, the
evaluation scores and refinement history, ceiling reconciliation, trade-offs,
policy citations, disclosed assumptions and provenance. Every number on the
sheet traces to an input; the "illustrative" posture and confidence
disclosures follow docs/MUNICIPAL_POLICY_SPATIAL_AI_RESEARCH_2026_06_25.md.
"""

from __future__ import annotations

import html
import logging
from typing import Any

from shapely.geometry import Polygon
from shapely.validation import make_valid

from app.services.site_engine import (
    build_transformer,
    local_metric_crs_for_polygon,
    project_geometry,
)

logger = logging.getLogger(__name__)

SHEET_COLORS = {
    "street": "#9aa0a8",
    "open_space": "#79c079",
    "courtyard": "#79c079",
    "building": "#8b5cf6",
    "boundary": "#151515",
}


def _svg_ring(poly, to_metric, origin_x: float, origin_y: float) -> str:
    metric = project_geometry(poly, to_metric)
    points = " ".join(
        f"{x - origin_x:.1f},{origin_y - y:.1f}"  # flip y: SVG grows downward
        for x, y in metric.exterior.coords
    )
    return points


def _drawing_svg(
    boundary_wgs84: Polygon,
    plan_zones: list[dict[str, Any]],
) -> str:
    """Top-down plan drawing in metres. viewBox units ARE metres."""
    boundary = make_valid(boundary_wgs84)
    crs = local_metric_crs_for_polygon(boundary)
    to_metric = build_transformer("EPSG:4326", crs)
    boundary_m = project_geometry(boundary, to_metric)
    minx, miny, maxx, maxy = boundary_m.bounds
    pad = 20.0
    width = (maxx - minx) + 2 * pad
    height = (maxy - miny) + 2 * pad
    ox, oy = minx - pad, maxy + pad  # origin: top-left, y flipped

    parts: list[str] = []
    order = {"street": 0, "open_space": 1, "courtyard": 2, "building": 3}
    drawable = [z for z in plan_zones if z.get("role") in order]
    drawable.sort(key=lambda z: order[z["role"]])
    for zone in drawable:
        try:
            poly = Polygon(zone["coordinates"])
        except Exception:  # noqa: BLE001
            continue
        points = _svg_ring(poly, to_metric, ox, oy)
        color = SHEET_COLORS[zone["role"]]
        opacity = "0.9" if zone["role"] == "building" else "0.8"
        parts.append(
            f'<polygon points="{points}" fill="{color}" fill-opacity="{opacity}" '
            f'stroke="#151515" stroke-width="0.8"/>'
        )
        floors_value = zone.get("floors")
        try:
            floors_value = float(floors_value) if floors_value is not None else None
        except (TypeError, ValueError):
            floors_value = None  # user-edited zone property — never 500 the sheet
        if zone["role"] == "building" and floors_value:
            centroid = project_geometry(poly, to_metric).centroid
            parts.append(
                f'<text x="{centroid.x - ox:.1f}" y="{oy - centroid.y:.1f}" font-size="9" '
                f'text-anchor="middle" fill="#ffffff" font-family="sans-serif">'
                f'{floors_value:g}F</text>'
            )

    boundary_points = " ".join(
        f"{x - ox:.1f},{oy - y:.1f}" for x, y in boundary_m.exterior.coords
    )
    parts.append(
        f'<polygon points="{boundary_points}" fill="none" stroke="{SHEET_COLORS["boundary"]}" '
        'stroke-width="2" stroke-dasharray="8 4"/>'
    )
    # Scale bar (100 m) + north arrow.
    bar_y = height - 12
    parts.append(
        f'<line x1="12" y1="{bar_y}" x2="112" y2="{bar_y}" stroke="#151515" stroke-width="2"/>'
        f'<text x="62" y="{bar_y - 4}" font-size="10" text-anchor="middle" '
        'font-family="sans-serif">100 m</text>'
        f'<text x="{width - 18}" y="20" font-size="14" font-family="sans-serif">N ↑</text>'
    )
    return (
        f'<svg viewBox="0 0 {width:.0f} {height:.0f}" xmlns="http://www.w3.org/2000/svg" '
        'style="width:100%;max-width:820px;background:#f6f4ee;border:2px solid #151515">'
        + "".join(parts) + "</svg>"
    )


def _citation_ref(citation: dict[str, Any]) -> str:
    """Citation label, linked to the official document when the corpus knows
    its URL (#page=N deep-links into PDFs)."""
    label = f"{_esc(citation.get('doc'))} p.{_esc(citation.get('page'))}"
    url = citation.get("url")
    if not url or not str(url).startswith(("http://", "https://")):
        return label
    href = _esc(str(url) + (f"#page={citation.get('page')}" if str(url).lower().endswith(".pdf") else ""))
    return f"<a href='{href}' target='_blank' rel='noopener'>{label}</a>"


def _esc(value: Any) -> str:
    return html.escape(str(value if value is not None else "—"))


def build_plan_sheet(
    *,
    scenario_label: str,
    scenario_id: str,
    payload: dict[str, Any],
    boundary_wgs84: Polygon,
    plan_zones: list[dict[str, Any]],
    dna: dict[str, Any] | None,
    snapshot_meta: dict[str, Any],
) -> str:
    plan = payload.get("plan") or {}
    metrics = payload.get("metrics") or {}
    metric_rows = ""
    for key in ("site_area_m2", "net_developable_m2", "open_space_m2", "building_footprint_m2",
                "gfa_m2", "far_achieved", "units", "population", "parking_stalls"):
        metric = (metrics.get("metrics") or {}).get(key)
        if not metric or metric.get("value") is None:
            continue
        metric_rows += (
            f"<tr><td>{_esc(metric['label'])}</td>"
            f"<td class='num'>{metric['value']:,} {_esc(metric.get('unit', ''))}</td>"
            f"<td class='derivation'>{_esc(metric.get('derivation'))}</td></tr>"
        )

    ceiling_rows = ""
    for entry in metrics.get("ceiling_reconciliation") or []:
        badge = {"within": "✓ within", "exceeds": "⚠ exceeds", "unknown": "— unknown"}.get(entry.get("status"), "")
        ceiling_rows += (
            f"<tr><td>{_esc(entry.get('district'))}</td><td class='num'>{_esc(entry.get('area_pct_of_site'))}%</td>"
            f"<td class='num'>{_esc(entry.get('ceiling_floors'))}</td><td>{badge}</td>"
            f"<td class='derivation'>{_esc(entry.get('source'))}</td></tr>"
        )

    iteration_rows = ""
    for step in plan.get("iterations") or []:
        revisions = "; ".join(
            f"{r['parameter']} {r['from']:g}→{r['to']:g} ({r['reason'].split(':')[0]})"
            for r in step.get("revisions", [])
        ) or "converged"
        worst = min((step.get("scores") or {}).items(),
                    key=lambda kv: kv[1].get("score", 1.0), default=(None, {}))
        iteration_rows += (
            f"<tr><td class='num'>{step['iteration']}</td>"
            f"<td class='num'>{step['overall_score']:.3f}</td>"
            f"<td>{_esc(worst[0])} = {worst[1].get('score', 0):.2f}</td>"
            f"<td class='derivation'>{_esc(revisions)}</td></tr>"
        )

    trade_off_items = "".join(
        f"<li>{_esc(t.get('message'))}</li>" for t in (payload.get("trade_offs") or [])[:8]
    ) or "<li>No unresolved inter-disciplinary conflicts recorded.</li>"

    policy_items = ""
    insight = ((((dna or {}).get("policy") or {}).get("fields") or {}).get("insight") or {}).get("value") or {}
    for group, prefix in (("conformance_considerations", ""), ("opportunities", "Opportunity — ")):
        for item in insight.get(group) or []:
            cites = "; ".join(_citation_ref(c) for c in item.get("citations") or [])
            policy_items += (
                f"<li><b>{prefix}{_esc(item.get('topic'))}:</b> {_esc(item.get('detail'))}"
                + (f" <span class='cite'>[{cites}]</span>" if cites else "")
                + "</li>"
            )
    policy_items = policy_items or "<li>No policy corpus findings for this site.</li>"

    assumption_items = "".join(
        f"<li><b>{_esc(key)}</b> = {_esc(info.get('value'))} {_esc(info.get('unit'))} — {_esc(info.get('note'))}</li>"
        for key, info in (metrics.get("assumptions_used") or {}).items()
        if key != "lap_storeys_by_category"
    )

    notes_items = "".join(
        f"<li class='{_esc(n.get('severity'))}'>{_esc(n.get('code'))}: {_esc(n.get('message'))}</li>"
        for n in (plan.get("notes") or [])
    )

    svg = _drawing_svg(boundary_wgs84, plan_zones)
    gi = plan.get("geometry_inputs") or {}

    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>Plan sheet — {_esc(scenario_label)}</title>
<style>
 body {{ font-family: Georgia, 'Times New Roman', serif; color: #151515; margin: 28px auto; max-width: 860px; }}
 h1 {{ font-size: 26px; margin-bottom: 2px; }}
 h2 {{ font-size: 15px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 2px solid #151515; padding-bottom: 3px; margin-top: 26px; }}
 .banner {{ background: #fff3cd; border: 2px solid #151515; padding: 8px 12px; font-size: 13px; margin: 12px 0; }}
 table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
 td, th {{ border-bottom: 1px solid #ccc; padding: 4px 6px; text-align: left; vertical-align: top; }}
 td.num {{ text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }}
 td.derivation, .cite {{ color: #555; font-size: 11.5px; }}
 ul {{ font-size: 12.5px; padding-left: 18px; }}
 li.warning {{ color: #92400e; }} li.error {{ color: #b91c1c; }}
 .meta {{ font-size: 11.5px; color: #555; }}
 .sheet-footer {{ margin-top: 30px; padding-top: 8px; border-top: 1px solid #999;
   font-size: 10.5px; color: #555; display: flex; justify-content: space-between; gap: 12px; }}
 @page {{ size: A4 portrait; margin: 12mm; }}
 @media print {{
   body {{ margin: 0; max-width: none; }}
   h2 {{ break-after: avoid; }}
   table, svg, .banner {{ break-inside: avoid; }}
 }}
</style></head><body>
<h1>{_esc(scenario_label)} — Concept Plan</h1>
<p class="meta">Scenario <code>{_esc(scenario_id)}</code> · generated {_esc(plan.get('generated_at'))} ·
plan score {_esc(plan.get('final_score'))} · DNA snapshot {_esc(snapshot_meta.get('snapshot_id'))}
({_esc(snapshot_meta.get('city_id'))}, overall confidence {_esc(snapshot_meta.get('overall_confidence'))})</p>
<div class="banner"><b>ILLUSTRATIVE — NOT AN APPROVED DESIGN.</b> Machine-generated concept for internal
deliberation. Statistics are derived from open data and disclosed assumptions; policy notes are
trade-off framings with verifiable citations, not conformance determinations.</div>

<h2>Plan drawing (metres)</h2>
{svg}
<p class="meta">Streets {gi.get('row_area_m2', 0):,.0f} m² · open space {gi.get('open_space_area_m2', 0):,.0f} m² ·
blocks {gi.get('net_block_area_m2', 0):,.0f} m² · {_esc(plan.get('block_count'))} blocks ·
{_esc(plan.get('parcel_count'))} parcels · {_esc(plan.get('intersection_density_per_km2'))} intersections/km² ·
internal ROW {_esc((plan.get('rules') or {}).get('row_width_m'))} m
(clear {_esc((plan.get('rules') or {}).get('clear_width_m'))} m ≥ CSPS033 6 m)</p>

<h2>Derived statistics</h2>
<table><tr><th>Measure</th><th>Value</th><th>Derivation</th></tr>{metric_rows}</table>

<h2>Zoning ceiling reconciliation</h2>
<table><tr><th>District</th><th>Site share</th><th>Ceiling (storeys)</th><th>Status</th><th>Basis</th></tr>
{ceiling_rows or '<tr><td colspan="5">No district data.</td></tr>'}</table>

<h2>Evaluation &amp; refinement history</h2>
<table><tr><th>Iteration</th><th>Score</th><th>Weakest dimension</th><th>Revisions applied for next iteration</th></tr>
{iteration_rows}</table>

<h2>Trade-offs surfaced by the expert panel</h2>
<ul>{trade_off_items}</ul>

<h2>Policy considerations (with citations)</h2>
<ul>{policy_items}</ul>

<h2>Validation notes</h2>
<ul>{notes_items or '<li>None.</li>'}</ul>

<h2>Disclosed assumptions</h2>
<ul>{assumption_items}</ul>

<p class="meta">Produced by City Prompt Urban Intelligence. Data: City of Calgary Open Data
(datasets per the Site Intelligence capabilities list) and the seeded policy corpus. Missing datasets
and low-confidence fields are disclosed in the Site Intelligence panel; this sheet inherits those limits.</p>
<div class="sheet-footer">
  <span>ILLUSTRATIVE — NOT AN APPROVED DESIGN · City Prompt</span>
  <span>Scenario {_esc(scenario_id)} · generated {_esc(plan.get('generated_at'))}</span>
</div>
</body></html>"""
