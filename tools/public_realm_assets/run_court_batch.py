"""Finite offline build/verification queue. Never overwrites an earlier package."""
import argparse, concurrent.futures, json, subprocess, sys
from pathlib import Path
from court_specs import COURTS

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--blender',type=Path,required=True)
    parser.add_argument('--kit',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--kinds',choices=COURTS,nargs='+',required=True)
    parser.add_argument('--workers',type=int,choices=(1,2),default=2)
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--reference-root',type=Path)
    args=parser.parse_args();root=Path(__file__).parent
    assert args.blender.is_file() and args.kit.is_file()
    assert len(args.kinds)==len(set(args.kinds))
    for kind in args.kinds:assert not (args.output/kind).exists(),f'Preserve existing package: {kind}'
    def command(kind):
        return [str(args.blender),'--background','--threads','4','--python-exit-code','1','--python',str(root/'build_courts.py'),
                '--','--kind',kind,'--kit',str(args.kit),'--output',str(args.output/kind),
                *(['--reference-root',str(args.reference_root)] if args.reference_root else [])]
    # Dry run every recipe before any build, with no provider calls or output models.
    for kind in args.kinds:
        result=subprocess.run([*command(kind),'--dry-run'],capture_output=True,text=True)
        if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    if args.dry_run:
        print('DRY_RUN_PASS',json.dumps(args.kinds));return
    args.output.mkdir(parents=True,exist_ok=True)
    def build(kind):
        with (args.output/f'{kind}.log').open('w',encoding='utf-8') as log:
            result=subprocess.run(command(kind),stdout=log,stderr=subprocess.STDOUT)
            if result.returncode:return dict(kind=kind,status='BUILD_FAILED',code=result.returncode)
            verify=[str(args.blender),'--background','--threads','2','--python-exit-code','1','--python',str(root/'verify_courts.py'),'--',str(args.output/kind)]
            result=subprocess.run(verify,stdout=log,stderr=subprocess.STDOUT)
            return dict(kind=kind,status='PASS' if result.returncode==0 else 'VERIFY_FAILED',code=result.returncode)
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for future in concurrent.futures.as_completed([pool.submit(build,kind) for kind in args.kinds]):
            result=future.result();results.append(result);print(json.dumps(result),flush=True)
    summary=args.output/('batch-'+ '-'.join(args.kinds)+'.json')
    summary.write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    if any(result['status']!='PASS' for result in results):sys.exit(1)
if __name__=='__main__':main()
