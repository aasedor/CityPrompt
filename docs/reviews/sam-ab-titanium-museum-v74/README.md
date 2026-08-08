# Titanium Museum v74 — controlled SAM 3D A/B

This pilot compares two deterministic Blender/LEGO interpretations of the exact
same `deconstructivist_titanium_pavilion` catalogue archetype. The baseline uses
the three catalogue reference views only. The informed version changes only the
plan/section evidence inferred from an audited SAM 3D Objects pass; compiler,
cameras, renderer, dimensions and construction kit remain controlled.

## Result

The SAM-informed version is the stronger massing model. It changes the inner
cluster from five broad regular pods to seven asymmetric leaning pods, deepens
the gallery cantilever and increases the perimeter ribbon's plan and section
variation. Street silhouette IoU improves from `0.620` to `0.674`, street aspect
error falls from `0.541` to `0.427`, and the paired street/roof evidence contract
changes from `FAIL` to `PASS`.

The baseline's higher roof-outline IoU (`0.951` versus `0.912`) is not evidence
of a better roof. That metric sees only the outer silhouette: the baseline's
simple rounded enclosure fills it efficiently while missing the reference's
internal curvilinear topology. Human review still favours the SAM-informed pod
count, asymmetry and depth variation.

## Biggest remaining weakness

The dominant archetype gap is now the envelope and roof/wall assembly, not the
gross footprint:

1. The reference's outer layer is a luminous, partially transparent perforated
   metal veil. The model renders it as an opaque charcoal wall, hiding the pods
   and eliminating patterned light, self-shadow and layer separation.
2. The inner forms are modeled as closed capped drums. The reference uses
   interlocking curved walls, roof courts, skylights, terraces and non-planar
   metal caps, so the current roof remains diagrammatic.
3. The gallery cantilever is still an orthogonal dark box rather than a tapered,
   curved titanium volume with a deep reflective soffit.
4. Bright silver material response, standing-seam scale, glazing depth and warm
   occupied interiors are underdeveloped.

## Pipeline decision

Keep SAM 3D as optional evidence for ambiguous pod count, occluded depth,
cantilever reach and section variation. Do not use its point/Gaussian output as
the final LEGO mesh. The next high-value compiler work is a double-layer
perforated veil assembly and an open/interlocking curved-wall roof kit, followed
by material and lighting calibration against the archetype.

The successful SAM job used an NVIDIA L40S for `236.9` seconds and produced
`882,976` Gaussians. At the authorized pilot rate of US$1.80 per GPU-hour, the
GPU portion is approximately US$0.12.
