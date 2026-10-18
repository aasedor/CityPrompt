"""Write original parent definitions to the local trial package only."""
import importlib,json,shutil
from pathlib import Path
from specs import DESIGNS
ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=Path('C:/dev-artifacts/CityPrompt/parkade-family-2026-10-17')


def main():
    path=ROOT/'seed/parkade-family-trial/parents.json';new=[]
    for key,brief in DESIGNS.items():
        slug=brief['slug'];w,d=brief['dimensions'];levels=brief['levels'];height=.15+3.3*(levels-1)+2.75
        variant='classic-concrete-v1' if key=='classic' else key+'-v1'
        new.append(dict(id=slug,title=brief['label'],buildingSubcategory='Parkades',developmentType='mobility_infrastructure',aestheticCategory='original_parkade',
            description=brief['identity']+' Original fixed native architectural-clay concept. No structural, accessibility, capacity or traffic-engineering certification.',
            generationTags=['parkade','parking garage','structured parking',brief['style']],
            styleProfile=dict(materials=['concrete','steel','transparent core glass'],facadeRhythm=brief['identity'],roofForm='Open roof parking with authored signature features',windowStyle='Transparent stair-core glazing; permeable deck guards',massing=f'{w} by {d} m native envelope, {levels} fixed parking levels'),
            prompt=dict(subject=brief['label'],details=[brief['identity'],'Preserve exact fixed deck count, open rear ramps, glazed stair cores and native geometry. Do not invent enclosed floors.']),
            suggestedWidth_m=w+4,suggestedDepth_m=d+4,minWidth_m=w+3,maxWidth_m=200,minDepth_m=d+3,maxDepth_m=200,
            suggestedFloorHeight=3.3,minFloors=levels,maxFloors=levels,thumbnailUrl=f'/archetypes/buildings/{slug}/front.png',
            variants=[dict(id=variant,label=brief['label'],description=brief['identity']+' Fixed native assembly.',thumbnailUrl=f'/archetypes/buildings/{slug}/front.png',minFloors=levels,maxFloors=levels,suggestedFloorHeight=3.3)]))
    content=json.dumps(dict(archetypes=new),indent=2,ensure_ascii=False)+'\n'
    if path.exists():
        if json.loads(path.read_text(encoding='utf-8'))!=json.loads(content):raise ValueError('Refuse conflicting trial parents')
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(content,encoding='utf-8')
    print('Created exactly five local trial parents; production catalogue unchanged')


if __name__=='__main__':main()
