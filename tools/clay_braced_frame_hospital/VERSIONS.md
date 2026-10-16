# Version history

| version | purpose | result |
|---|---|---|
| v001 (1440 px, 32 spp, 18 views + 4 phone boards) | first build from the locked views | builder pass, aperture audit PASS, 69,178 triangles, 3,663,852-byte GLB; VISUAL_REWORK_REQUIRED: 0 P0 / 6 P1 / 8 P2, so v002 follows |
| v002 (1440 px, 32 spp, 18 views + 4 phone boards) | fixes the v001 findings | builder pass, aperture audit PASS, 77,620 triangles, 4,122,972-byte GLB; VISUAL_REWORK_REQUIRED: 0 P0 / 3 P1 / 9 P2 (down from 0 + 6, so v003 follows) |
| v003 (1440 px, 32 spp, 18 views + 4 phone boards) | fixes the v002 findings | builder pass, aperture audit PASS, 78,760 triangles, 4,184,528-byte GLB; VISUAL_REWORK_REQUIRED: 0 P0 / 1 P1 / 9 P2 (down from 0 + 3, so v004 follows) |
| v004 (1440 px, 32 spp, 18 views + 4 phone boards) | fixes the v003 finding | builder pass, aperture audit PASS, 78,796 triangles, 4,186,784-byte GLB; VISUAL_REWORK_REQUIRED: 0 P0 / 1 P1 / 11 P2 (not lower than v003's 0 + 1, so v003 stays the candidate on a tie; one more version under the stopping rule) |
