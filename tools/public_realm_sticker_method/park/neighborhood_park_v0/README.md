# Neighborhood Park v0 — Sticker Method pilot

This is the first executable park pilot for the Sticker Method. It binds the
selected rustic reference to deterministic skins, five metric GLB object
families and a site-adaptive runtime assembly.

The exact selected image is authoritative. It depicts a rustic timber nature
play territory with gravel circulation, split-rail fencing, wildflower edges,
boulders, a pavilion, a climbing/slide structure and a separate swing frame.
The generic parent description and current `neighborhood-park-v4` runtime
profile are secondary where they conflict with that image.

Representation: `site_adaptive_whole_program`. The parcel and connected ground
fields may adapt, but fixed play and pavilion objects remain whole, metric,
contained and unscaled. This is the public-realm analogue of Sticker Method
LEGO: topology and kit identity are deterministic; stickers own only intrinsic
gravel, timber, meadow, lawn and stone appearance.

Run the assessment:

```powershell
python tools/public_realm_sticker_method/park/neighborhood_park_v0/audit.py
```

Use the fail-closed readiness gate:

```powershell
python tools/public_realm_sticker_method/park/neighborhood_park_v0/audit.py --require-ready
```

The gate verifies the exact reference, source locks, compiled object manifest,
runtime assembly and explicit surface ownership before returning `ready`.
