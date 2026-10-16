# Student stress-test fixes

Branch base: `94abf42265aa0b133c7421c00c0f8dd229c7225f` (the inspected
`origin/deployment-version`). Evidence is outside Git at
`C:/dev-artifacts/CityPrompt/student-stress-test-2026-10-16/`.

## Boundary recovery

Rejected `temp-` boundary drafts remain recoverable, but are excluded from the
automatic compilation input key, readiness checks and cache refresh snapshot.
The persisted scene stays usable. Site assessments require a persisted UUID.
The drawing rejection is shown beside Retry/Discard in both Site and Design.

## Vancouver tower delivery

The 16–40-storey programme already has reviewed source bands and runtime code;
the missing podium/floor/roof records and object bytes cause taller designs to
fall back to massing. The original 16-storey assembly is unchanged. The local
repair installs the three exact existing modules through the finite installer.

The base-selection hosted audit previously excluded optional modules. It now
requires the three modules advertised by the Vancouver programme, checking each
role, programme identity, dimensions, hash, storage and privacy. A complete
native assembly cannot satisfy a missing floor module.

Local verification/install:

```powershell
python scripts/vancouver_tower_storeys.py
python scripts/vancouver_tower_storeys.py --verify
python scripts/vancouver_tower_storeys.py --install --owner-id EXISTING_LOCAL_OWNER_UUID
```

For a separately authorized hosted repair, use the reviewed checkout with its
four hydrated, hash-verified LFS files and explicitly configured database/S3
environment. Never substitute the local target or overwrite conflicts:

```powershell
python scripts/vancouver_tower_storeys.py --verify --hosted --expected-database-host EXACT_DATABASE_HOST --expected-storage-endpoint EXACT_STORAGE_ENDPOINT
python scripts/vancouver_tower_storeys.py --install --hosted --expected-database-host EXACT_DATABASE_HOST --expected-storage-endpoint EXACT_STORAGE_ENDPOINT --owner-id EXISTING_PRODUCTION_OWNER_UUID
python scripts/vancouver_tower_storeys.py --verify --hosted --expected-database-host EXACT_DATABASE_HOST --expected-storage-endpoint EXACT_STORAGE_ENDPOINT
python backend/scripts/verify_hosted_catalogue.py --verify-target --report EXTERNAL_REPORT_PATH
```

The installer is additive and refuses conflicting IDs, role ownership or stored
bytes. Default target remains loopback-only. Hosted options require both exact
destination locks; they do not grant deployment approval. Review/record the
existing deployment and binding inventory before a production change. Roll back
application commits through the established deployment history; retain the
additive module objects/records while checking whether saved scenes use them.
Do not delete or disable modules as an automatic rollback.

No hosted writes or paid image/video generations are part of these local fixes.
