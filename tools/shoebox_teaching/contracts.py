"""Physical datums and complete immutable replay archives for one shoebox pilot."""
import hashlib
import json
from pathlib import Path
import shutil


def datums():
    """Approximate native scale inferred from reference proportions, not a survey."""
    return dict(width=6.8,depth=8.6,floor=.53,wall_base=.42,ceiling=3.12,
        roof_front_top=3.38,roof_rear_top=3.29,roof_thickness=.14,
        parapet_top=3.74,corner_coping_top=3.84,
        entry_levels=[.53/3,.53*2/3,.53])


def archive_replay(repo,destination,paths):
    """Copy consumed code, JSON and original sources with their repository paths."""
    repo=Path(repo).resolve();destination=Path(destination)
    if destination.exists():raise FileExistsError(destination)
    sources=[]
    for name in sorted(set(paths)):
        source=(repo/name).resolve()
        if not source.is_relative_to(repo):raise ValueError('Replay input escapes repository')
        if not source.is_file():raise FileNotFoundError(source)
        sources.append(source)
    destination.mkdir(parents=True)
    records=[]
    for source in sources:
        relative=source.relative_to(repo);target=destination/relative
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:
            raise ValueError('Replay archive hash mismatch')
        records.append(dict(path=relative.as_posix(),bytes=source.stat().st_size,sha256=digest))
    manifest=dict(schema='cityprompt.replay-source-overlay@1',files=records,
        boundary='Repository-shaped overlay, requiring recorded real Git base and Blender/Python dependencies; not a byte-identical rendering guarantee.')
    (destination/'snapshot-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return manifest
