"""Add three independently reviewed autumn native building pilots locally.

No browser approval or publication is implied. Existing models and references
are immutable. Use --package once per reviewed delivery, then --stage-public.
"""
import argparse,json,hashlib,math,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.catalogue_promotion import prepare,check,validate_review,LIBRARY
from tools.rlasm_clay_library import _validate_payload
from scripts.classroom_buildings import catalogue_records,stage_references

SPECS={
 'timber':('Nordic Roof-Garden Apartments','apartments','A six-storey timber frame with recessed balconies, planted roof terrace and shaded pavilion.'),
 'villa':('Tuscan Arcade Villa','detached','A three-level Tuscan home with a covered stone arcade, green shutters and a canal-tile roof.'),
 'cinema':('Grand Deco Cinema','civic','An Art Deco movie palace with arched gallery windows, a gold marquee and a double-sided blade sign.'),
}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def register(package):
    pre=read(package/'prework-manifest.json');report=read(package/'build-report.json')
    kind=pre['candidate'].split('-')[1]
    if kind not in SPECS:raise ValueError('Outside the finite autumn trio')
    title,group,description=SPECS[kind];references=[]
    for source in read(package/'source-entry.json')['sources']:
        data=(package/source['path']).read_bytes()
        if hashlib.sha256(data).hexdigest()!=source['sha256']:raise ValueError('Source hash changed')
        # Dedicated names preserve photographs or previews already bound elsewhere.
        rel=Path(source['repo_path']).parent/f"autumn-v1-{source['role']}{Path(source['path']).suffix}"
        target=ROOT/rel
        if target.exists() and target.read_bytes()!=data:raise ValueError('Existing reference differs')
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        references.append(dict(role=source['role'],repo_path=rel.as_posix(),bytes=len(data),sha256=source['sha256']))
    lo,hi=report['original_bounds_m'];dims=pre['measurement_contract']['dimensions_m']
    entry=dict(candidate=pre['candidate'],family='rlasm-autumn-'+kind,archetype_id=pre['archetype_id'],variant_id=pre['variant_id'],
        archetype_label=title,variant_label=title,native_floors=pre['measurement_contract']['floors'],design_dimensions_m=dims,
        references=references,external_evidence=str(package),picker=dict(id='autumn_'+kind,description=description,group_id=group,
        reshape_mode='fixed_native',reshape_description='One complete native building. Enlarge its surrounding plot or place another building.',
        width=math.ceil(hi[0]-lo[0]+3),depth=math.ceil(hi[1]-lo[1]+3),max_size=150))
    spec=dict(entry=entry,model_file=str(package/report['runtime']['path']),review_file=str(package/'review/independent-architectural-clay-review.json'))
    source_package=package/'local-trial-package.json';write(source_package,spec)
    prepare(ROOT,source_package,trial_only=True)
    prepare(ROOT,source_package,apply=True,trial_only=True)
    payload=check(ROOT,allow_trials=True);new=next(e for e in payload['entries'] if e['candidate']==entry['candidate'])
    records,assets=catalogue_records(dict(payload,entries=[new]));path=ROOT/'frontend/src/data/classroomExpansion.json';catalogue=read(path)
    if any(e['placement_id']==records[0]['placement_id'] for e in catalogue['entries']):raise ValueError('Existing picker identity')
    catalogue['entries']+=records;catalogue['assets']+=assets;write(path,catalogue)
    ledger=ROOT/'seed/classroom-buildings/autumn-selection.json';selection=read(ledger) if ledger.exists() else dict(schema='cityprompt.autumn-buildings@1',buildings=[])
    selection['buildings'].append(dict(candidate=new['candidate'],sha256=new['model']['sha256'],runtime='NOT TESTED',completed=False))
    write(ledger,selection)
    print('Registered local pilot:',title)

def selection(*,hydrated=True):
    payload=read(ROOT/LIBRARY);locks=read(ROOT/'seed/classroom-buildings/autumn-selection.json')['buildings']
    if len(locks)!=3:raise ValueError('Expected exactly three autumn buildings')
    if {lock['candidate'].split('-')[1] for lock in locks}!=set(SPECS):raise ValueError('Expected the exact autumn trio')
    chosen=[]
    for lock in locks:
        entry=next(e for e in payload['entries'] if e['candidate']==lock['candidate'])
        if entry['model']['sha256']!=lock['sha256']:raise ValueError('Changed model')
        validate_review(entry,ROOT)
        chosen.append(entry)
    selected=dict(payload,entries=chosen)
    if hydrated:_validate_payload(selected,clay_root=(ROOT/LIBRARY).parent,repo_root=ROOT)
    return selected

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path);p.add_argument('--stage-public',type=Path);a=p.parse_args()
    if a.package:register(a.package.resolve())
    if a.stage_public:print('Staged references:',stage_references(selection(),a.stage_public))
