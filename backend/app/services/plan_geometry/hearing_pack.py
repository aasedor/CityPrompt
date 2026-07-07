"""Hearing pack: the one-document municipal deliverable for a drawn scenario.

Pairs every AI render with the to-scale plan drawing, the conditioning
diagram, and the derived numbers it was generated from — the designed
safeguard posture for AI planning imagery (photoreal images never travel
alone). Print-ready self-contained HTML; images ride as data URIs.
"""

from __future__ import annotations

import base64
from datetime import datetime, timezone
from typing import Any

from shapely.geometry import Polygon

from app.services.plan_geometry.plan_sheet import _drawing_svg, _esc

COMPARE_KEYS = ("units", "gfa_m2", "far_achieved", "population", "open_space_m2")


def _data_uri(png_bytes: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(png_bytes).decode("ascii")


def _compare_table(scenarios: list[dict[str, Any]]) -> str:
    """scenarios: [{label, scenario_id, payload}] — complete ones only."""
    with_metrics = [s for s in scenarios if ((s.get("payload") or {}).get("metrics") or {}).get("metrics")]
    if len(with_metrics) < 2:
        return ""

    def value(scenario: dict[str, Any], key: str):
        metric = scenario["payload"]["metrics"]["metrics"].get(key) or {}
        return metric.get("value")

    def label_for(key: str) -> str:
        for scenario in with_metrics:
            metric = scenario["payload"]["metrics"]["metrics"].get(key)
            if metric and metric.get("label"):
                return metric["label"]
        return key

    header = "".join(f"<th class='num'>{_esc(s['label'])}</th>" for s in with_metrics)
    rows = ""
    for key in COMPARE_KEYS:
        if not any(value(s, key) is not None for s in with_metrics):
            continue
        cells = "".join(
            f"<td class='num'>{value(s, key):,}</td>" if value(s, key) is not None else "<td class='num'>—</td>"
            for s in with_metrics
        )
        rows += f"<tr><td>{_esc(label_for(key))}</td>{cells}</tr>"
    score_cells = "".join(
        (lambda score: f"<td class='num'>{score:.3f}</td>" if isinstance(score, (int, float)) else "<td class='num'>—</td>")(
            ((s.get("payload") or {}).get("plan") or {}).get("final_score")
        )
        for s in with_metrics
    )
    rows += f"<tr><td>Plan score</td>{score_cells}</tr>"
    return (
        "<h2>Scenario comparison</h2>"
        f"<table><tr><th>Measure</th>{header}</tr>{rows}</table>"
    )


def build_hearing_pack(
    *,
    scenario_label: str,
    scenario_id: str,
    payload: dict[str, Any],
    boundary_wgs84: Polygon,
    plan_zones: list[dict[str, Any]],
    dna: dict[str, Any] | None,
    snapshot_meta: dict[str, Any],
    diagram_png: bytes,
    renders: list[dict[str, Any]],
    sibling_scenarios: list[dict[str, Any]],
) -> str:
    plan = payload.get("plan") or {}
    metrics = payload.get("metrics") or {}

    trade_off_items = "".join(
        f"<li>{_esc(t.get('message'))}</li>" for t in (payload.get("trade_offs") or [])[:8]
    ) or "<li>No unresolved inter-disciplinary conflicts recorded.</li>"

    policy_items = ""
    insight = ((((dna or {}).get("policy") or {}).get("fields") or {}).get("insight") or {}).get("value") or {}
    for group, prefix in (("conformance_considerations", ""), ("opportunities", "Opportunity — ")):
        for item in insight.get(group) or []:
            cites = "; ".join(f"{c.get('doc')} p.{c.get('page')}" for c in item.get("citations") or [])
            policy_items += (
                f"<li><b>{prefix}{_esc(item.get('topic'))}:</b> {_esc(item.get('detail'))}"
                + (f" <span class='cite'>[{_esc(cites)}]</span>" if cites else "")
                + "</li>"
            )
    policy_items = policy_items or "<li>No policy corpus findings for this site.</li>"

    assumption_items = "".join(
        f"<li><b>{_esc(key)}</b> = {_esc(info.get('value'))} {_esc(info.get('unit'))} — {_esc(info.get('note'))}</li>"
        for key, info in (metrics.get("assumptions_used") or {}).items()
        if key != "lap_storeys_by_category"
    )

    render_figures = "".join(
        "<figure>"
        f"<img src='{_data_uri(r['png'])}' alt='AI render'>"
        f"<figcaption>{_esc(r.get('style') or 'AI render')} · saved {_esc((r.get('created_at') or '')[:10])} — "
        "illustrative AI-generated concept, watermarked and provenance-tagged.</figcaption>"
        "</figure>"
        for r in renders
    ) or "<p class='meta'>No saved renders for this project yet — generate renders and save them to include imagery.</p>"

    svg = _drawing_svg(boundary_wgs84, plan_zones)
    gi = plan.get("geometry_inputs") or {}
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>Hearing pack — {_esc(scenario_label)}</title>
<style>
 body {{ font-family: Georgia, 'Times New Roman', serif; color: #151515; margin: 28px auto; max-width: 860px; }}
 h1 {{ font-size: 28px; margin-bottom: 2px; }}
 h2 {{ font-size: 15px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 2px solid #151515; padding-bottom: 3px; margin-top: 26px; }}
 .banner {{ background: #fff3cd; border: 2px solid #151515; padding: 10px 14px; font-size: 13px; margin: 14px 0; }}
 table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
 td, th {{ border-bottom: 1px solid #ccc; padding: 4px 6px; text-align: left; vertical-align: top; }}
 td.num, th.num {{ text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }}
 .cite {{ color: #555; font-size: 11.5px; }}
 ul {{ font-size: 12.5px; padding-left: 18px; }}
 .meta {{ font-size: 11.5px; color: #555; }}
 figure {{ margin: 12px 0; }}
 figure img {{ width: 100%; border: 1px solid #151515; }}
 figcaption {{ font-size: 11px; color: #555; margin-top: 3px; }}
 .pair {{ display: flex; gap: 12px; align-items: flex-start; }}
 .pair > div {{ flex: 1; min-width: 0; }}
 .pair img {{ width: 100%; border: 1px solid #999; }}
 .sheet-footer {{ margin-top: 30px; padding-top: 8px; border-top: 1px solid #999;
   font-size: 10.5px; color: #555; display: flex; justify-content: space-between; gap: 12px; }}
 @page {{ size: A4 portrait; margin: 12mm; }}
 @media print {{
   body {{ margin: 0; max-width: none; }}
   h2 {{ break-after: avoid; }}
   table, figure, svg, .banner, .pair {{ break-inside: avoid; }}
 }}
</style></head><body>
<h1>{_esc(scenario_label)}</h1>
<p class="meta">Hearing pack · scenario <code>{_esc(scenario_id)}</code> · assembled {generated} ·
DNA snapshot {_esc(snapshot_meta.get('snapshot_id'))} ({_esc(snapshot_meta.get('city_id'))},
overall confidence {_esc(snapshot_meta.get('overall_confidence'))}) · plan score {_esc(plan.get('final_score'))}</p>
<div class="banner"><b>ILLUSTRATIVE — NOT AN APPROVED DESIGN.</b> Machine-generated concept for
deliberation and engagement. Every image in this pack is paired with the to-scale drawing and the
derived statistics it was generated from; statistics carry their derivations and disclosed
assumptions; policy notes are trade-off framings with verifiable citations, not conformance
determinations.</div>

<h2>The plan — to scale, and as rendered</h2>
<div class="pair">
  <div>{svg}<p class="meta">Measurable drawing (site-local metres).</p></div>
  <div><img src="{_data_uri(diagram_png)}" alt="Plan diagram">
  <p class="meta">Conditioning diagram: the exact layout given to the image model —
  gray streets · green parks · dark-red building footprints.</p></div>
</div>
<p class="meta">Streets {gi.get('row_area_m2', 0):,.0f} m² · open space {gi.get('open_space_area_m2', 0):,.0f} m² ·
blocks {gi.get('net_block_area_m2', 0):,.0f} m² · {_esc(plan.get('block_count'))} blocks ·
{_esc(plan.get('parcel_count'))} parcels · internal ROW {_esc((plan.get('rules') or {}).get('row_width_m'))} m
(clear {_esc((plan.get('rules') or {}).get('clear_width_m'))} m ≥ CSPS033 6 m)</p>

<h2>Renders — illustrative concepts</h2>
{render_figures}

{_compare_table(sibling_scenarios)}

<h2>Expert trade-offs</h2>
<ul>{trade_off_items}</ul>

<h2>Policy considerations (cited)</h2>
<ul>{policy_items}</ul>

<h2>Disclosed assumptions</h2>
<ul>{assumption_items or '<li>None recorded.</li>'}</ul>

<div class="sheet-footer">
  <span>ILLUSTRATIVE — NOT AN APPROVED DESIGN · City Prompt</span>
  <span>Scenario {_esc(scenario_id)} · assembled {generated}</span>
</div>
</body></html>"""
