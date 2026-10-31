import json
from pathlib import Path
import pytest
from tools.drawn_bridge_routes.install_review_batch import append_roster_array,atomic_module_copy


def test_roster_dependency_insertion_preserves_nested_entry_dependencies():
    original=json.dumps({'entries':[{'variantId':'old','dependencies':['public:old.glb']}],
                         'dependencies':[{'id':'public:old.glb','bytes':12}]},indent=2)
    addition={'id':'public:new.glb','bytes':24}
    result=append_roster_array(original,'dependencies',[addition],'id',False)
    parsed=json.loads(result)
    assert parsed['entries']==json.loads(original)['entries']
    assert parsed['dependencies']==[{'id':'public:old.glb','bytes':12},addition]
    assert append_roster_array(result,'dependencies',[addition],'id',False)==result


def test_interrupted_copy_preserves_old_module_and_retry_recovers(tmp_path,monkeypatch):
    destination=tmp_path/'module.glb';destination.write_bytes(b'old verified module')
    write=Path.write_bytes
    def interrupted(path,data):
        if path.name.endswith('.review-tmp'):
            write(path,data[:4]);raise OSError('simulated interrupted write')
        return write(path,data)
    with monkeypatch.context() as patch:
        patch.setattr(Path,'write_bytes',interrupted)
        with pytest.raises(OSError):atomic_module_copy(destination,b'new verified module')
    assert destination.read_bytes()==b'old verified module'
    atomic_module_copy(destination,b'new verified module')
    assert destination.read_bytes()==b'new verified module'
