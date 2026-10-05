# City Prompt — land-use map in Google 3D

Updated 5 October 2026. Six actual browser screenshots from the Currie / Richmond pilot in Calgary. Click an image to inspect it at full size.

The overlay retains the City's district boundaries and full designations, including separate Direct Control references. This site contains 32 district pieces with 21 distinct designations. The presentation palette groups district families; it does not infer permitted uses within Direct Control districts.

## Transparent colour — 40%

The angled view shows the land-use colours over the existing Google 3D buildings. Fill opacity is adjustable from 0% to 100%; boundaries and labels have separate controls.

![Calgary land-use overlay at 40 percent opacity in Google 3D](pilot-translucent-3d.png)

## Solid colour — overhead

At 100%, the polygons read as a conventional land-use plan. Fine boundaries and full City codes remain visible.

![Overhead land-use map with solid colour fills](pilot-solid-top.png)

## Solid colour — angled

The same solid map viewed within the Google 3D environment.

![Solid land-use colours in an angled Google 3D view](pilot-solid-3d.png)

## Boundaries and labels — 0% fill

Setting opacity to zero removes the colour fill while retaining district delineations and labels.

![District boundaries and labels over imagery with zero fill opacity](pilot-outlines-top.png)

## Entire overlay switched off

The master switch hides the colours, boundaries and district labels together. Switching it back on restores the selected appearance.

![Google 3D scene with the land-use map switched off](pilot-off-3d.png)

## Controls at tablet size

A 1024 × 768 browser viewport with the left panel scrolled to the opacity control and district legend. This is a desktop browser size check; physical iPad testing remains outstanding.

![Opacity control and district legend in a tablet-sized viewport](pilot-tablet-controls.png)

## Pilot status

These are unchanged application captures with their map attribution retained. The existing ground-alignment warning remains visible in both the overlay-on and overlay-off views and is still unresolved. The overlay uses a reference height; terrain alignment remains part of the pilot review.

The local application checkpoint is `271eb6268`. Its focused frontend suite passed 75 tests, followed by TypeScript checks and browser verification of opacity, visibility and saved appearance. These images publish the visual review only; the application code has not been deployed to Cityprompt.ca.

[Earlier corrected zoning-map screenshots](../zoning-correction/README.md) · [Full progress gallery](../README.md)
