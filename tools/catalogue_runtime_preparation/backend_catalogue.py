"""Register the finite authored roster in the backend's trusted identity table.

Preserve established planning dimensions. New original families copy their
authored dimensions, rather than guessing from their visual catalogue label.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def sync(root=ROOT):
    def read(path):
        return json.loads((root/path).read_text(encoding='utf8'))
    source = {a['id']: a for a in read('frontend/src/data/buildingArchetypes.json')['archetypes']}
    roster = read('frontend/src/data/catalogueOctober2026.json')['entries']
    path = root/'backend/app/data/archetype_plan_dims.json'
    data = json.loads(path.read_text(encoding='utf8'))
    existing = {a['id']: a for a in data['archetypes']}
    for item in roster:
        parent, variant = item['archetype_id'], item['variant_id']
        if parent not in source:
            continue  # A later finite wave may not be installed yet.
        authored = source[parent]
        assert any(v['id'] == variant for v in authored.get('variants', [])), item
        if parent not in existing:
            entry = dict(id=parent, title=authored['title'],
                development_type=authored['developmentType'], aesthetic_category=authored['aestheticCategory'],
                district_kit=None, generation_tags=authored.get('generationTags', []),
                min_floors=authored['minFloors'], max_floors=authored['maxFloors'],
                usable=True, has_variants=True, variant_ids=[], default_variant_id=variant,
                suggested_w_m=authored['suggestedWidth_m'], suggested_d_m=authored['suggestedDepth_m'],
                min_w_m=authored['minWidth_m'], max_w_m=authored['maxWidth_m'],
                min_d_m=authored['minDepth_m'], max_d_m=authored['maxDepth_m'],
                suggested_area_sqm=authored['suggestedWidth_m']*authored['suggestedDepth_m'])
            data['archetypes'].append(entry)
            existing[parent] = entry
        if variant not in existing[parent]['variant_ids']:
            existing[parent]['variant_ids'].append(variant)
    data['count'] = len(data['archetypes'])
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1)+'\n', encoding='utf8')

if __name__ == '__main__':
    sync()
