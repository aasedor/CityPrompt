# Native-house move control clarity — 20 September 2026

The fresh Currie student pilot showed that dragging the native model body pans
the 3D camera, while the selected plot's **Move** handle correctly moves the
house. The reshape panel and lower screen hint had told students to drag the
body. Both now name the working Move handle for `native_home_plot` objects;
the general object/park instructions are unchanged.

In the disposable Currie project, selecting the modern infill house showed the
Move handle and both updated instructions in the browser. The prior pilot
already verified a Move-handle edit, Undo/Redo and reload of the same house.
This is a control-language correction, not a new drag mechanism or geometry
change. New native-house variants must verify model selection, the Move handle,
reshape/rotation, Undo/Redo and reload through ordinary controls. Do not label
body dragging as supported unless the actual model input path implements it.

Focused ReshapePanel tests, TypeScript and changed-file lint passed. Browser
evidence is `C:/dev-artifacts/CityPrompt/grounding-batch-a/currie-move-hint-ui.png`.
No project geometry was changed for this check.
