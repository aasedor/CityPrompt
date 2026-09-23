"""Explicit finite offline queue; dry run all candidates first, preserve prior output."""
import argparse, concurrent.futures, json, subprocess, sys
from pathlib import Path
from street_specs import STREETS


def main():
    p=argparse.ArgumentParser();p.add_argument('--blender',type=Path,required=True)
    p.add_argument('--kit',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--kinds',choices=STREETS,nargs='+',required=True)
    p.add_argument('--workers',type=int,choices=(1,2),default=2);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args();src=Path(__file__).parent;assert len(a.kinds)==len(set(a.kinds))
    assert a.blender.is_file() and a.kit.is_file()
    for kind in a.kinds:assert not (a.output/kind).exists(),f'Preserve earlier package: {kind}'
    def command(kind):
        return [str(a.blender),'--background','--threads','4','--python-exit-code','1','--python',str(src/'build_street_batch.py'),
            '--','--kind',kind,'--kit',str(a.kit),'--reference-root',str(a.reference_root),'--output',str(a.output/kind)]
    for kind in a.kinds:
        result=subprocess.run([*command(kind),'--dry-run'],capture_output=True,text=True)
        if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    if a.dry_run:print('DRY_RUN_PASS',json.dumps(a.kinds));return
    a.output.mkdir(parents=True,exist_ok=True)
    def build(kind):
        with (a.output/f'{kind}.log').open('w',encoding='utf-8') as log:
            result=subprocess.run(command(kind),stdout=log,stderr=subprocess.STDOUT)
            if result.returncode:return dict(kind=kind,status='BUILD_FAILED')
            result=subprocess.run([str(a.blender),'--background','--threads','2','--python-exit-code','1','--python',str(src/'verify_street_batch.py'),'--',str(a.output/kind)],stdout=log,stderr=subprocess.STDOUT)
            return dict(kind=kind,status='PASS' if result.returncode==0 else 'VERIFY_FAILED')
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        for future in concurrent.futures.as_completed([pool.submit(build,kind) for kind in a.kinds]):
            record=future.result();results.append(record);print(json.dumps(record),flush=True)
    (a.output/('batch-'+'-'.join(a.kinds)+'.json')).write_text(json.dumps(results,indent=2)+'\n')
    if any(r['status']!='PASS' for r in results):sys.exit(1)


if __name__=='__main__':main()
