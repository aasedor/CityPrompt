"""The next finite batch must reject missing image bytes and unenrolled views."""
import pytest
from PIL import Image
from tools.catalogue_zoning_next_five.plan import SPECS,source_entry

@pytest.mark.parametrize('kind',list(SPECS))
def test_pointer_cannot_become_locked_reference(tmp_path,kind):
    s=SPECS[kind];root=tmp_path/'frontend/public/archetypes/buildings'/s['directory'];root.mkdir(parents=True)
    (root/f'variant_{s["index"]}.png').write_bytes(b'version https://git-lfs.github.com/spec/v1\noid sha256:abc\nsize 99\n')
    with pytest.raises(ValueError,match='Unhydrated source'):source_entry(kind,tmp_path)

def test_new_source_angle_requires_compatibility_review(tmp_path):
    s=SPECS['peaks'];root=tmp_path/'frontend/public/archetypes/buildings'/s['directory'];root.mkdir(parents=True)
    for suffix in ('.png','_angle_60.jpg','_angle_90.jpg','_rear.jpg'):
        Image.new('RGB',(8,8),'gray').save(root/f'variant_{s["index"]}{suffix}')
    with pytest.raises(ValueError,match='Additional views need compatibility review'):source_entry('peaks',tmp_path)
