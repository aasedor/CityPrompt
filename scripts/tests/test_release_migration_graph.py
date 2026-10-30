"""Both previously deployed database histories must upgrade without restamping."""
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
import pytest


@pytest.mark.parametrize('starting_revision', [
    None, '022_document_processing_task', '030_render_attempts', '031_merge_legacy_documents', '032_auth_sessions',
])
def test_old_production_and_current_release_have_one_upgrade_target(starting_revision):
    config = Config()
    config.set_main_option('script_location', str(Path(__file__).resolve().parents[2] / 'backend/migrations'))
    scripts = ScriptDirectory.from_config(config)
    assert scripts.get_heads() == ['033_repair_document_task_binding']
    # Match Alembic upgrade traversal, which includes unapplied sibling branches.
    revisions = list(scripts.iterate_revisions('heads', starting_revision, implicit_base=True))
    applied = {r.revision for r in revisions}
    assert '033_repair_document_task_binding' in applied
    if starting_revision == '032_auth_sessions':
        assert applied == {'033_repair_document_task_binding'}
        return
    assert '032_auth_sessions' in applied
    if starting_revision == '031_merge_legacy_documents':
        assert applied == {'032_auth_sessions', '033_repair_document_task_binding'}
        return
    assert '031_merge_legacy_documents' in applied
    if starting_revision == '022_document_processing_task':
        assert '022_document_processing_task' not in applied
        assert '022_create_urban_dna_tables' in applied
        assert '030_render_attempts' in applied
    elif starting_revision == '030_render_attempts':
        assert '030_render_attempts' not in applied
        assert '022_document_processing_task' in applied
    else:
        assert {'022_document_processing_task', '030_render_attempts'} <= applied
