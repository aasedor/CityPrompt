# Woonerf Shared Street v0 — Sticker Method pilot

This is the evidence-lock wave for applying the Sticker Method to a street. It
does not claim that the existing runtime is release-ready.

The three selected-variant views override the generic Dutch woonerf prose.
They show a continuous brick pedestrian public room organized by repeated
timber pergolas, flowering vines, citrus pots, pale mosaic inlays, wrought-iron
benches and historic lamps. They do not show the current runtime's dominant
vehicle chicanes, play nodes, raised tables or informal parking pockets.

Representation: `connected_corridor_lego`. The 10 m cross-section and graph
connections remain fixed. Longitudinal capacity comes only from complete open
promenade and pergola-social modules at constant material scale. Intersections
and endpoints are graph-owned and may not be filled by cropped modules.

Run the assessment:

```powershell
python tools/public_realm_sticker_method/street/woonerf_shared_street_v0/audit.py
```

The current expected result is `hold`. To use the audit as a release gate:

```powershell
python tools/public_realm_sticker_method/street/woonerf_shared_street_v0/audit.py --require-ready
```

That command intentionally fails until the street section, module kit and
material ownership wave clear every recorded runtime gap.
