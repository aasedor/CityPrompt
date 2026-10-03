"""Install one independently reviewed church in the local validation catalogue.

This does not update seed, the approved library, or publication manifests.
The large source catalogue is surgically extended, never reformatted.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
DESIGNS={
 'gothic_community_church':dict(title='Gothic Community Church',width=35,depth=63,
   description='A six-bay limestone church with one bell tower and spire, rose window, vaulted nave, side aisles and polygonal sanctuary. A level entrance opens onto clear aisles between timber pews.',
   materials=['buff limestone','slate','stained glass','timber pews'],
   roof='Steep nave gable, lower lean-to aisle roofs, polygonal hipped apse and one octagonal spire.',
   frontage='Level stone forecourt with flowering perennial beds and low clipped hedges, keeping the central entrance and side circulation clear.',
   rhythm='Six pointed side windows with clerestory lights; rose window and recessed front portal.',color='#b1a185'),
 'timber_sanctuary_church':dict(title='Timber Sanctuary Church',width=42,depth=47,
   description='A contemporary timber sanctuary with a tall glazed front gable, eight exposed portal frames, warm timber walls and a low community annex. A level entrance leads to a broad centre aisle and two pew banks.',
   materials=['laminated timber','vertical cedar boards','standing-seam metal','clear glass','buff stone'],
   roof='One steep metal gable over the sanctuary and a low flat roof over the rear-right annex.',
   frontage='Level buff forecourt and native prairie grasses with flowering meadow planting; the entrance and side access stay open.',
   rhythm='Tall narrow side windows between eight timber portal frames, full-height glazed front and rear altar slit.',color='#b9925f'),
}
def splice_first(path,key,row):
    text=path.read_text(encoding='utf-8');token='"'+key+'": ['
    assert text.count(token)==1
    encoded=json.dumps(row,ensure_ascii=False,indent=2)
    text=text.replace(token,token+'\n    '+encoded.replace('\n','\n    ')+',',1)
    json.loads(text);path.write_text(text,encoding='utf-8')

def main():
    p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('--public-root',type=Path,required=True)
    p.add_argument('--assets-only',action='store_true',help='Hydrate an already registered local review without changing catalogue source')
    a=p.parse_args()
    report=json.loads((a.candidate/'build-report.json').read_text());lock=json.loads((a.candidate/'source-entry.json').read_text())
    review=json.loads((a.candidate/'review/independent-review.json').read_text())
    assert review['unresolved_p0']==0 and review['unresolved_p1']==0,'Independent review is still blocked'
    parent=lock['archetype_id'];variant=lock['variant_id'];d=DESIGNS[parent];name=report['candidate'];sha=report['runtime']['sha256']
    glb=a.candidate/report['runtime']['path'];assert hashlib.sha256(glb.read_bytes()).hexdigest()==sha
    assert review['exact_glb']['sha256']==sha,'Review belongs to different model bytes'
    dims=[report['native_dimensions_m'][k] for k in ('width','depth','height')]
    url=f'/validation-assets/{name}/{glb.name}';thumb=f'/archetypes/buildings/{parent}/reference-board-v1.png'
    dest=a.public_root/'validation-assets'/name;dest.mkdir(parents=True,exist_ok=True);shutil.copy2(glb,dest/glb.name)
    for img in (ROOT/'frontend/public/archetypes/buildings'/parent).glob('*.png'):
        output=a.public_root/'archetypes/buildings'/parent/img.name;output.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(img,output)
    if a.assets_only:
        print(json.dumps(dict(hydrated=url,sha256=sha)));return
    fixture='validation_'+variant
    entry=dict(record_id=f'building/{parent}/{variant}@{sha}',domain='building',title=d['title'],archetype_id=parent,variant_id=variant,version=name,
      sha256=sha,existing_reviews=['PASS_INDEPENDENT_ARCHITECTURAL_CLAY'],completed=False,remaining=['Human visual approval before catalogue publication'],
      quality_status='builder_candidate',approval_scope='Local architectural-clay review and browser trial only',verified_model_path=str(glb),app_eligible=False,
      status='Independently reviewed architectural clay; local trial',local_url=url,placement_id=fixture,runtime_status='PILOT_TESTING',binding='fixed-native-review',native_dimensions_m=dims)
    asset=dict(id=fixture,kind='object',definitionVersion=1,readiness='pilot',label=d['title'],description=d['description'],thumbnail=thumb,
      model=dict(variantId=variant,revision=sha,method='RLASM 6.1 architectural clay'),calgaryGuide=dict(groupId='civic',basis='form_reference'),
      zoneType='building',reshapeMode='fixed_native',width=d['width'],depth=d['depth'],minWidth=d['width'],minDepth=d['depth'],maxSize=160,
      reshapeDescription='Keep the church at its authored dimensions; enlarge its surrounding plot without stretching the architecture.',nativeDimensions=dims,
      properties=dict(validation_fixed_fixture=True,validation_native_url=url,building_archetype_id=parent,development_archetype_id=parent,
        development_selected_variant_id=variant,development_archetype_label=d['title'],native_home_plot=False,native_plot_axes=True,
        community_3d_mask_existing_tiles=True,floors=1,floor_count=1,floor_height=dims[2],height=dims[2]))
    archetype=dict(id=parent,title=d['title'],aestheticCategory='civic_institutional',description=d['description'],buildingSubcategory='Civic — Church / Community',
      developmentType='institutional',districtKit='calgary',generationTags=['church','community','sanctuary','interior'],
      suggestedWidth_m=d['width'],suggestedDepth_m=d['depth'],minWidth_m=d['width'],maxWidth_m=d['width'],minDepth_m=d['depth'],maxDepth_m=d['depth'],
      suggestedFloorHeight=dims[2],minFloors=1,maxFloors=1,suggestedAreaSqm=d['width']*d['depth'],aspectRatio=f"{d['width']}:{d['depth']}",shadeId=d['color'],thumbnailUrl=thumb,
      palette=dict(skyTop='#88a8ca',skyBottom='#d8e4ed',facadePrimary=d['color'],facadeSecondary='#e2d6bc',accent='#504637',window='#a6b7ba',ground='#71934f',street='#57595a',landscape='#567743'),
      styleProfile=dict(materials=d['materials'],massing=d['description'],facadeRhythm=d['rhythm'],roofForm=d['roof'],frontageType=d['frontage'],windowStyle=d['rhythm'],streetRelationship=d['frontage'],articulation=d['description']),
      facadeDetail=dict(primaryMaterial=d['materials'][0],secondaryMaterial=', '.join(d['materials'][1:]),groundFloor=d['frontage'],upperFloors='No occupied upper storeys; sanctuary height and tower are fixed architecture.',cornice=d['roof'],colorScheme=d['color']),
      roofDetail=dict(form=d['roof'],material=d['materials'][1],features=d['roof'],aerialAppearance=d['roof']),
      renderPrompt=dict(mapOverlay=d['description']+' '+d['frontage']+' Keep the site context and exact native architecture.',roofView=d['roof'],negative='extra towers, changed footprint, extra storeys, floating entrances, blocked aisles'),
      variants=[dict(id=variant,label=d['title'],thumbnailUrl=thumb,description=d['description'],minFloors=1,maxFloors=1,suggestedAreaSqm=d['width']*d['depth'],palette=dict(primary=d['color']))])
    registry=ROOT/'frontend/src/data/validationCatalogue.json';source=ROOT/'frontend/src/data/buildingArchetypes.json'
    assert fixture not in registry.read_text(),'Already registered: use an explicit reviewed revision update'
    assert parent not in [r['id'] for r in json.loads(source.read_text(encoding='utf-8'))['archetypes']]
    splice_first(source,'archetypes',archetype);splice_first(registry,'entries',entry);splice_first(registry,'assets',asset)
    print(json.dumps(dict(registered=variant,sha256=sha,dimensions=dims,scope='local trial only')))

if __name__=='__main__':main()
