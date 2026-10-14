# Previous production database compatibility

The previous Render service ran beemanbesh/2D-Maps2 at commit 807e323. Its database
was at revision 022_document_processing_task, a sibling of this repository's
022_create_urban_dna_tables revision. Both descend from 021_add_previous_snapshot.

An isolated restore of the production backup reproduced a startup failure:
Alembic could not resolve 022_document_processing_task. Deployment was held before
the new API reached the production database.

This release preserves the previous migration's identity and operations (a
nullable documents.processing_task_id VARCHAR(100) column and nonunique index).
031_merge_legacy_documents joins that branch with 030_render_attempts. Alembic
applies only the missing branch before merging. No manual version restamping,
database reset, or deletion is required.

Validation on an isolated PostgreSQL 16 container:

- Restored production directory-format backup successfully.
- Upgraded the restored legacy database to the merge head.
- Confirmed existing user/project counts and the legacy document index remained.
- Repeated startup migrations successfully with no pending changes.
- Upgraded a fresh database and a database at 030_render_attempts to the same head.
- Three migration-graph regression cases passed.

The exact backup, restore script and receipts are private deployment artifacts,
not repository data. These are local rehearsal results; production migration and
application checks must be recorded separately after successful deployment.

Rollback of application code is not a schema downgrade. Preserve the backup and
inspect compatibility before any production schema rollback. A destructive
restore or downgrade is not part of this deployment.
