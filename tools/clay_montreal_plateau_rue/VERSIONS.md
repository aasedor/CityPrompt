# Version history

| version | purpose | result |
|---|---|---|
| v001 (1440 px, 32 spp, 18 views + 4 phone boards) | first build of the family | builder pass, aperture audit PASS, 68,728 triangles, 3,466,352-byte GLB; VISUAL_REWORK_REQUIRED, P0 = 0, P1 = 6, P2 = 8 (first candidate) |
| v002 (1440 px, 32 spp, 18 views + 4 phone boards) | Fix the six v001 P1s: stairs land at deck level, continuous curled handrail on joined newels, cornice ends past the party line, framed rear windows, glazed context windows with open railings, reframed corner camera | builder pass, aperture audit PASS, 78,300 triangles, 3,989,084-byte GLB; VISUAL_REWORK_REQUIRED, P0 = 0, P1 = 1, P2 = 12 (five v001 P1s are fixed; open: the wall-side handrail head at each stair top ends free in mid-air and reads as a black bar rising through the gallery deck (the stair-at-deck finding, first targeted fix); lowest so far, v002 becomes the candidate) |
| v003 (1440 px, 32 spp, 18 views + 4 phone boards) | Second targeted fix of the stair-head finding: capped stair-head newels on the landing tread end both handrails; street-side rail pitched into the central newel | builder pass, aperture audit PASS, 78,972 triangles, 4,027,580-byte GLB; PASS_ZERO_P0_P1, P0 = 0, P1 = 0, P2 = 13 (the v002 P1 is fixed and every earlier fix holds; v003 becomes the candidate) |
