"""Index only verified local packages and carry explicit pending runtime gates."""
import argparse,json,hashlib,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);p.add_argument('packages',type=Path,nargs='+');a=p.parse_args()
repo=Path(__file__).resolve().parents[2];template=(repo/'docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md').read_text(encoding='utf-8')
source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
records=[]
for root in a.packages:
    r=json.loads((root/'recipe.json').read_text());v=json.loads((root/'geometry-verification.json').read_text())
    assert v['status']=='PASS_OFFLINE_GEOMETRY'
    for name in ('aerial','top','detail'):assert (root/'renders'/f'{name}.png').stat().st_size>1000
    sources={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in root.glob('*.py')}
    manifest=dict(id=r['id'],title=r['title'],package=str(root),dimensions_m=r['dimensions_m'],assembly=r['assembly'],modules=r['modules'],
      triangles=r['triangles'],mesh_instances=r['mesh_instances'],verification=v,source_sha256=sources,
      builder_review='Visual review recorded in repository batch report; not independent human approval',
      runtime_status='NOT TESTED; not installed in student picker',source_base_revision=source_revision)
    if 'sport_asset' in r:manifest['sport_asset']=r['sport_asset']
    records.append(manifest)
    intro=f"# Pending runtime review: {r['title']}\n\nExact ID: `{r['id']}`. Native footprint: {r['dimensions_m']} metres.\nAssembly SHA-256: `{r['assembly']['sha256']}`.\nSource base: `{source_revision}`; exact builder hashes in batch manifest.\n\nOffline native geometry passed; this is not runtime acceptance. All runtime\nchecks below remain NOT TESTED. No current picker, seed or catalogue ID is\noverwritten. Integrate with shared terrain/access/recovery/capture and test on\na disposable vacant Currie layout before classroom activation. Street preview\nassemblies must not be bent/repeated; courts must retain their full run-off.\n\n"
    (root/'runtime-review-pending.md').write_text(intro+template,encoding='utf-8')
a.report.write_text(json.dumps(dict(version=1,paid_calls=0,runtime_activated=False,candidates=records),indent=2)+'\n',encoding='utf-8')
print(json.dumps([dict(id=r['id'],triangles=r['triangles'],bytes=r['assembly']['bytes'],mesh_instances=r['mesh_instances']) for r in records],indent=2))
