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
role, programme identity, source version, dimensions, executable floor range,
repeatability, occupied storeys, family/placement contract, hash, storage and privacy. A complete
native assembly cannot satisfy a missing floor module.

Height edits preflight the exact candidate zone through the same request builder
as compilation, including saved model revision and footprint geometry. A failed
check leaves the saved building unchanged; closing the editor prevents a delayed
response from saving an obsolete edit.

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

## Responsive tools and validation

Below 1024 px, tools use compact bottom sheets with expansion for detailed
settings. Catalogue ownership stays mounted across breakpoint changes so an
open dialogue can close normally and release map editing. Existing editing,
placement, selection and undo/redo logic is reused.

The final relevant suites passed: 169 frontend tests (including compiler
regressions), 274 backend tests and four installer-target tests; TypeScript and
changed-file lint passed. Browser checks covered rejected-boundary recovery,
valid-boundary save, detailed 17/25/40-storey towers, save/reload, detail
place/select/rotate/move/delete/undo/copy, and 360/390/768 px layouts. Actual
phone hardware was unavailable. The full lint command retains pre-existing
failures in untouched files. A production bundle build passed with the shared
hydrated public directory and `copyPublicDir:false`; duplicating that large
directory for a full self-contained build exceeded local disk space.
