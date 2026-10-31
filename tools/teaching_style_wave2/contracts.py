"""Fail-closed boundaries for this finite, unactivated teaching batch."""
from pathlib import Path

from tools.teaching_style_pilot.contracts import lock_sources


def candidate_path(output, batch_root):
    output, batch_root = Path(output).resolve(), Path(batch_root).resolve()
    if output == batch_root or batch_root not in output.parents:
        raise ValueError('Output must stay inside the named external batch')
    if output.exists():
        raise FileExistsError('Preserve the existing candidate; use a new version')
    return output


def source_lock(archetype_id, variant_id, roles, authoritative_root):
    root = Path(authoritative_root).resolve()
    for path in roles.values():
        if root not in Path(path).resolve().parents:
            raise ValueError('Source is outside the authoritative reference root')
    return lock_sources(archetype_id, variant_id, roles)
