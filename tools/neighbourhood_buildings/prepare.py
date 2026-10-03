"""Lock the finite library/cafe source set without modifying catalogue images."""
import argparse
import hashlib
import json
from pathlib import Path

SPECS = {
    'library': ('university_library', 'mass_timber_biophilic_barn', 'university-library', 2),
    'cafe': ('parisian_boulevard_corner', 'parisian_corner_cafe_culture', 'parisian_boulevard_corner', 1),
}

def main():
    p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();entries=[]
    for kind,(parent,variant,folder,index) in SPECS.items():
        sources=[]
        for role,suffix in [('front','.png'),('oblique','_angle_60.jpg'),('top','_angle_90.jpg')]:
            path=a.source_root/'frontend/public/archetypes/buildings'/folder/f'variant_{index}{suffix}'
            data=path.read_bytes();assert len(data)>10000, path
            sources.append(dict(role=role,path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
        entries.append(dict(kind=kind,archetype_id=parent,variant_id=variant,sources=sources))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as f:json.dump(dict(schema=1,entries=entries),f,indent=2)
    print('LOCKED',len(entries),'buildings; six exact source views')

if __name__=='__main__':main()
