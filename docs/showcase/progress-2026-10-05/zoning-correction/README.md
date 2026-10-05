# City Prompt — corrected Calgary zoning codes

Updated 5 October 2026. Actual screenshots and a PNG export from the local classroom trial.

District designations now come from the [City of Calgary Land Use Districts dataset](https://data.calgary.ca/Base-Maps/Land-Use-Districts/qe6k-p9nh), with a link to the [Land Use Bylaw](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html). Codes are separate from student captions and survive saving, reloading and export. Narrow districts use label callouts.

## Existing City districts

The trial site's seven published district areas retain their full codes, including the individual Direct Control designations. The district key includes source descriptions. Colours are editable study colours.

![Existing Calgary districts with full designations and narrow-area label callouts](existing-calgary-districts.jpg)

## Proposed student map

The example proposal uses R-CG and S-SPR, chosen from the City's published district list. “Courtyard housing” and “Neighbourhood park” are separate student captions. These proposed assignments do not describe the site's existing zoning.

![Proposed map showing R-CG and S-SPR separately from editable captions](proposed-calgary-codes.jpg)

## Exported PNG

This is the actual PNG downloaded from City Prompt, with the same district codes, captions and legend.

![PNG exported from the proposed zoning study](proposed-calgary-codes.png)

[Open the full PNG](proposed-calgary-codes.png) · [Earlier progress gallery](../README.md)

The source correction is local checkpoint `b7528e26e`: 28 focused frontend tests, 19 backend tests and TypeScript checks passed, followed by browser save/reload and export verification. This gallery publishes the images only. Cityprompt.ca has not been updated. The wider visual work remains under review.
