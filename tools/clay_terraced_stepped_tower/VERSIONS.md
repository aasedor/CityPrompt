# Version history

| version | purpose | result |
|---|---|---|
| v001 (1440 px, 32 spp, 18 views + 4 phone boards) | first build from the locked views | builder pass, aperture audit PASS, 77,666 triangles, 4,124,608-byte GLB; VISUAL_REWORK_REQUIRED: 0 P0 / 5 P1 / 10 P2, so v002 follows |
| v002 (1440 px, 32 spp, 18 views + 4 phone boards) | fixes the v001 findings | builder pass, aperture audit PASS, 73,172 triangles, 3,864,088-byte GLB; VISUAL_REWORK_REQUIRED: 1 P0 / 5 P1 / 8 P2 (worse than v001's 0 + 5, so v001 stays the candidate; one more version under the stopping rule) |
