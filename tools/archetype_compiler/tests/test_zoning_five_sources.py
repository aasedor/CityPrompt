"""Prevent absent source bytes and partial renders becoming review evidence."""
from pathlib import Path
import pytest
from tools.catalogue_zoning_five.plan import SPECS, source_entry
from tools.catalogue_zoning_five.prepare_review import require_complete

def test_lfs_pointer_is_not_a_build_reference(tmp_path):
    s=SPECS['office']
    root=tmp_path/'frontend/public/archetypes/buildings'/s['directory']
    root.mkdir(parents=True)
    (root/'variant_1.png').write_bytes(b'version https://git-lfs.github.com/spec/v1\noid sha256:abc\nsize 99\n')
    with pytest.raises(ValueError,match='Unhydrated source'):
        source_entry('office',tmp_path)

def test_review_requires_final_report_and_every_declared_view(tmp_path):
    (tmp_path/'renders').mkdir()
    (tmp_path/'renders/front.png').write_bytes(b'not relevant to completeness check')
    before={p.relative_to(tmp_path) for p in tmp_path.rglob('*')}
    with pytest.raises(FileNotFoundError,match='Build is not complete'):
        require_complete(tmp_path,dict(mandatory_review_views=['front','rear']))
    assert {p.relative_to(tmp_path) for p in tmp_path.rglob('*')}==before
    (tmp_path/'build-report.json').write_text('{}')
    with pytest.raises(FileNotFoundError,match='rear.png'):
        require_complete(tmp_path,dict(mandatory_review_views=['front','rear']))

def test_same_variant_extra_view_cannot_escape_enrollment(tmp_path):
    from PIL import Image
    s=SPECS['row'];root=tmp_path/'frontend/public/archetypes/buildings'/s['directory'];root.mkdir(parents=True)
    for suffix in ('.png','_angle_60.jpg','_angle_90.jpg','_rear.jpg'):
        Image.new('RGB',(8,8),'gray').save(root/f'variant_2{suffix}')
    with pytest.raises(ValueError,match='Additional views need compatibility review'):
        source_entry('row',tmp_path)
