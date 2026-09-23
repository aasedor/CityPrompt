# Currie Connections plot guide — browser check

The Connections editor now offers an interactive plot guide for a building
entrance. A student can point to an approximate position or use arrow keys to
adjust the marker; the exact left/right and front/back offsets remain visible
and editable. The guide explicitly says it outlines the plot, not the native
building or its doorway. The author must still inspect the real step foot and
ground connection in 3D.

The browser check used the disposable seven-house Currie project
`54bb844c-1ff4-4d67-bc7f-0c8c36d0030e`, on `Shared street west 2` with
its previously authored native-step anchor. The guide opened with the saved
`0.9 m, -10.35 m` marker. A pointer choice changed both displayed offsets;
Cancel and reopen restored the saved values, so the trial did not modify the
fixture. The dialog remained scrollable to the exact fields and Save button.
Browser page errors were empty.

Evidence is outside Git in
`C:/dev-artifacts/CityPrompt/grounding-batch-a/`:
`currie-anchor-guide-dialog.png` and
`currie-anchor-guide-dialog-bottom.png`. This helps position an anchor; it
does not infer a native doorway, solve the high foundation, or clear the six
other Currie entrance warnings. Full student usability still requires a
novice journey and pilot.

Focused Vitest passed **21 tests across two files**, including pointer and
keyboard adjustment with a saved result. TypeScript type-check and
changed-file ESLint passed. No paid generation or push occurred.
