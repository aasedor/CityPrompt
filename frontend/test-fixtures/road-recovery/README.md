# Bounded road-readiness recovery

Open `/test-fixtures/road-recovery/index.html` on the local Vite server. This
mounts the real `GlobeStreetDetailLayer` and `assertStreetGroundReady`; only tile
ray hits are synthetic. It writes no project and makes no provider/tile calls.
It is outside the production entry graph and the packaged Vite output.

1. Initial measurements exhaust three passes: unavailable, four missing stations,
   zero retries. Try exact export: refused.
2. Replace with complete tiles; allow measurement to settle. Ready, zero missing
   stations, one retry. Try exact export: allowed.
3. Reload. After unavailable, replace with incomplete tiles twice, allowing each
   measurement to settle. Unavailable with two retries.
4. Replace with complete tiles a third time: no further retry. Export remains
   refused with the saved-design/reload guidance.

All four steps were observed in the in-app browser on 2026-09-24. This is
controlled renderer evidence, not hosted Google tile delivery evidence.
