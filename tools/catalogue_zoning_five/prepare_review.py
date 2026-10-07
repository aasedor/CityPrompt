"""Assemble unchanged render evidence and an honest, untested runtime record."""
from pathlib import Path
import argparse
import importlib.util
import json
import shutil

ROOT=Path(__file__).resolve().parents[2]

def require_complete(root,manifest):
    paths=[root/'build-report.json']+[root/'renders'/f'{view}.png' for view in manifest['mandatory_review_views']]
    missing=[str(path) for path in paths if not path.is_file()]
    if missing:raise FileNotFoundError('Build is not complete; no review output written: '+', '.join(missing))

def main():
    p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);a=p.parse_args()
    root=a.candidate.resolve()
    spec=importlib.util.spec_from_file_location('clay_proof',ROOT/'tools/catalogue_services_batch/proof.py')
    proof=importlib.util.module_from_spec(spec);spec.loader.exec_module(proof)
    manifest=proof.read(root/'prework-manifest.json')
    require_complete(root,manifest)
    if (root/'evidence/delivery-verification.json').exists():raise FileExistsError('Evidence already recorded')
    proof.boards(root,manifest)
    result=proof.verify(root,manifest)
    shutil.copy2(ROOT/'tools/catalogue_services_batch/proof.py',root/'scripts/proof.py')
    report=proof.read(root/'build-report.json')
    template=(ROOT/'docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md').read_text(encoding='utf-8')
    prefix=(f'# Candidate build checkpoint: {manifest["candidate"]}\n\n'
        f'Exact variant: `{manifest["variant_id"]}`. GLB SHA-256: `{report["runtime"]["sha256"]}`.\n\n'
        'This package is an offline architectural-clay candidate. Runtime installation, student authoring, '
        'terrain, connections, editing, persistence, browser performance and capture are **NOT TESTED**. '
        'The retained template below is an open acceptance checklist, not a completed runtime approval. '
        'No catalogue, database or hosted application was modified. Fixed native scale only.\n\n'
        f'Measured complete bounds: `{json.dumps(report["native_dimensions_m"])}` metres.\n\n')
    with (root/'evidence/runtime-review.md').open('x',encoding='utf-8') as f:f.write(prefix+template)
    print(json.dumps(dict(status=result['status'],failures=[k for k,v in result['checks'].items() if not v],runtime='NOT TESTED'),indent=2))
    return 0 if result['status']=='PASS_DELIVERY_CHECKS' else 1

if __name__=='__main__':raise SystemExit(main())
