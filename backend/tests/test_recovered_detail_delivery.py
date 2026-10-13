import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_all_196_concepts_reconcile_to_catalogue_or_explicit_hold():
    audit = json.loads((ROOT/'docs/add-details-recovery/inventory.json').read_text())
    catalogue = json.loads((ROOT/'frontend/src/features/parks/recoveredDetails.json').read_text())
    assert len(audit['records']) == len({r['id'] for r in audit['records']}) == 196
    assert {r['canonical_id'] for r in audit['records'] if r['status'] == 'accepted_local_trial'} == {r['id'] for r in catalogue}
    assert len(catalogue) == 185
    assert all(r.get('reason') for r in audit['records'] if r['status'] == 'held')


def test_hydration_checks_whole_batch_before_copying_and_preserves_conflicts(tmp_path):
    spec = importlib.util.spec_from_file_location('hydrate', ROOT/'scripts/hydrate_recovered_details.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    bundle = tmp_path/'bundle'; bundle.mkdir(); public = tmp_path/'public'
    (bundle/'a.glb').write_bytes(b'approved'); (bundle/'a.webp').write_bytes(b'preview')
    row = {'url': '/park-kits/recovered-details-v1/a.glb', 'sha256': hashlib.sha256(b'approved').hexdigest(),
           'thumbnailUrl': '/park-kits/recovered-details-v1/a.webp', 'thumbnailSha256': '0'*64}
    with pytest.raises(ValueError, match='Checksum'):
        module.hydrate(bundle, public, [row])
    assert not public.exists()
    row['thumbnailSha256'] = hashlib.sha256(b'preview').hexdigest()
    assert module.hydrate(bundle, public, [row]) == 2
    target = public/row['url'].lstrip('/'); target.write_bytes(b'user work')
    with pytest.raises(ValueError, match='conflicting'):
        module.hydrate(bundle, public, [row])
    assert target.read_bytes() == b'user work'
