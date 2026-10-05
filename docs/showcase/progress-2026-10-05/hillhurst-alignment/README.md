# Hillhurst — residential boundary alignment check

5 October 2026. Actual City Prompt browser captures around 14 Street NW in Hillhurst, with the existing Google 3D buildings retained. Click an image to inspect it at full size.

**Finding:** the rendered boundary coordinates match the City source geometry. The overhead views let you inspect the relationship to residential blocks and lanes. Precise alignment with the 3D terrain remains unverified: the existing ground-alignment warning is visible, and the overlay still uses one reference elevation.

## Neighbourhood overview — 40% colour

The test site contains 20 district pieces and 19 distinct designations, including R-CG, R-C2, M-CGd72, commercial districts and individual Direct Control references.

![Hillhurst residential blocks with transparent land-use colours](hillhurst-overhead-40.png)

## Residential close-up — boundaries only

Zero fill opacity makes the small R-CG district, nearby C-N1 district and surrounding lanes easier to inspect. These are zoning district outlines, not individual property lines. The large rectangular outer edge is the test site boundary, where the City polygons are clipped.

![Close overhead view of Hillhurst zoning boundaries over houses and lanes](hillhurst-residential-close.png)

## Same close-up — 40% colour

![The same residential close-up with transparent district colours](hillhurst-residential-close-40.png)

## Angled Google 3D view

The overlay uses a single reference height, so sloping ground and raised roofs can produce apparent displacement in perspective. This view remains a pilot, with the unresolved terrain warning preserved.

![Hillhurst land-use map in the angled Google 3D environment](hillhurst-oblique-40.png)

## Coordinate check

The check fetched the [City of Calgary Land Use Districts source](https://data.calgary.ca/Base-Maps/Land-Use-Districts/qe6k-p9nh) again and compared it against the line geometry actually mounted in the 3D scene. It transformed the rendered line endpoints back to geographic coordinates and measured their distance from the source polygon edges or the site's clipping edge.

- 20 source rows, 20 displayed district pieces.
- 128 rendered boundary segments, with 111 unique vertices.
- Maximum horizontal difference from source/clipping edges: less than 1 mm of numerical conversion error.
- No browser application errors were recorded.

This verifies preservation of the input coordinates; it does not establish survey accuracy or exact agreement with Google's terrain and buildings. See the [recorded check](alignment-audit.json).

Application checkpoint: `271eb6268`, unchanged for this test. A separate disposable local project was created for Hillhurst; the Currie trial was preserved. Only screenshots and this review record are published here. Cityprompt.ca has not been redeployed.

[Currie / Richmond pilot](../globe-land-use-pilot/README.md) · [Full progress gallery](../README.md)
