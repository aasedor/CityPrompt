import { describe,it,expect } from 'vitest';
import type { SiteZone } from '@/types';
import { CLASSROOM_CHOICES } from './canonicalCatalogue';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { streetConnectionProblem } from './streetConnectionProblem';
import { MANUAL_STREET_ASSETS } from './assetRegistry';
import { PUBLIC_REALM_STREET_SELECTIONS } from '@/components/viewer/globe/streetFamilyCatalog';
import { detectConnectedStreetIntersections } from '@/components/viewer/globe/streetGraphIntersections';
import { resolveStreetJunctionLayout } from '@/components/viewer/globe/streetJunctionGeometry';
import { streetEditConnectionCheck } from './streetEditConnections';
const street=(id:string,variant:string,points:number[][]):SiteZone=>{
  const asset=CLASSROOM_CHOICES.flatMap(c=>c.placements).find(a=>a.model.variantId===variant)!;
  const line=points.map(([x,y])=>[x/111320,y/111320]);
  return {id,project_id:'test',color:'#aaa',sort_order:0,created_at:'1',updated_at:'1',zone_type:'road',coordinates:bufferLineToPolygon(line,Number(asset.properties.width)),properties:{...asset.properties,plan_centerline:line}};
};
describe('ordinary route junction preflight',()=>{
  const main=street('main','student_main_street_v1',[[-120,0],[120,0]]);
  it.each(['student_quiet_residential_street_v1','student_planted_shared_lane_v1','student_market_street_v1'])('accepts complete native T and X joins for %s',variant=>{
    expect(streetConnectionProblem(street('a',variant,[[0,0],[0,100]]),[main])).toBeNull();
    expect(streetConnectionProblem(street('a',variant,[[0,-100],[0,100]]),[main])).toBeNull();
  });
  it('rejects shallow crossings, short arms and overlapping parallel duplicates',()=>{
    expect(streetConnectionProblem(street('a','student_quiet_residential_street_v1',[[-100,-20],[100,20]]),[main])).toMatch(/junction/);
    expect(streetConnectionProblem(street('a','student_quiet_residential_street_v1',[[115,-100],[115,100]]),[main])).toMatch(/junction/);
    expect(streetConnectionProblem(street('a','student_main_street_v1',[[-120,3],[120,3]]),[main])).toMatch(/junction/);
    expect(streetConnectionProblem(street('a','student_main_street_v1',[[120,0],[240,0]]),[main])).toBeNull();
    expect(streetConnectionProblem(street('a','student_main_street_v1',[[-120,50],[120,50]]),[main])).toBeNull();
  });
  it('checks the complete node when individually valid pairs have incompatible opposing sections',()=>{
    const north=street('north','student_planted_shared_lane_v1',[[0,0],[0,100]]);
    const south=street('south','student_quiet_residential_street_v1',[[0,-100],[0,0]]);
    expect(streetConnectionProblem(north,[main])).toBeNull();
    expect(streetConnectionProblem(south,[main])).toBeNull();
    expect(streetConnectionProblem(south,[main,north])).toMatch(/junction/);
  });
});

const manualStreet=(id:string,variant:string,points:number[][],saved:boolean):SiteZone=>{
  const asset=MANUAL_STREET_ASSETS.find(a=>a.model.variantId===variant)!;
  const selection=PUBLIC_REALM_STREET_SELECTIONS.find(s=>s.variantId===variant)!;
  const line=points.map(([x,y])=>[x/111320,y/111320]);
  const properties:Record<string,unknown>={...asset.properties,plan_centerline:line};
  if(saved) properties.public_realm_lego={
    schema_version:1,family_id:selection.familyId,family_version:1,kind:'street',generator:'street_section',
    archetype_id:selection.archetypeId,variant_id:variant,profile_id:selection.profileId,profile_version:1,
    appearance_kit_id:selection.appearanceKitId,component_set_ids:selection.componentSetIds,
    target:{target_type:'street_segment',row_width_m:asset.sectionWidth,length_m:points.length===2
      ? Math.hypot(points[1][0]-points[0][0],points[1][1]-points[0][1]):200},
    catalog_fingerprint:'a'.repeat(64),capability_fingerprint:'b'.repeat(64),recipe_hash:'c'.repeat(64),
  };
  return {id,project_id:'test',color:'#aaa',sort_order:0,created_at:'1',updated_at:'1',zone_type:'road',
    coordinates:bufferLineToPolygon(line,asset.sectionWidth),properties} as SiteZone;
};

describe('Street Manual junctions',()=>{
  const through=manualStreet('through','calgary_local_draft3_v1',[[-150,0],[150,0]],true);
  it.each(MANUAL_STREET_ASSETS.map(asset=>asset.model.variantId))('joins %s to a different manual street as T and X',variant=>{
    const crossing=manualStreet('draft-street',variant,[[0,-100],[0,100]],false);
    const tee=manualStreet('draft-street',variant,[[0,0],[0,100]],false);
    expect(streetConnectionProblem(crossing,[through])).toBeNull();
    expect(streetConnectionProblem(tee,[through])).toBeNull();
    const saved={...crossing,id:'saved-crossing',properties:manualStreet('saved-crossing',variant,[[0,-100],[0,100]],true).properties};
    const nodes=detectConnectedStreetIntersections([through,saved]);
    expect(nodes).toHaveLength(1);
    expect(resolveStreetJunctionLayout(nodes[0],[through,saved])).not.toBeNull();
  });

  it.each(MANUAL_STREET_ASSETS.map(asset=>asset.model.variantId))('retains a connected route when replacing its section with %s',variant=>{
    const original=manualStreet('existing-route','calgary_local_industrial_draft3_v1',[[0,-100],[0,100]],true);
    const candidate=manualStreet(original.id,variant,[[0,-100],[0,100]],false);
    const zones=[through,original];
    const before=JSON.stringify(zones);
    expect(streetConnectionProblem(candidate,zones)).toBeNull();
    expect(streetEditConnectionCheck(original,zones)(candidate)).toBe(true);
    expect(JSON.stringify(zones)).toBe(before);
    expect(candidate.properties?.junction_preview_candidate).toBeUndefined();
    // Preview admission cannot turn an unsaved selection into a runtime recipe.
    expect(detectConnectedStreetIntersections([through,candidate])).toHaveLength(0);
    const disconnected=manualStreet(original.id,variant,[[400,-100],[400,100]],false);
    expect(streetEditConnectionCheck(original,zones)(disconnected)).toBe(false);
  });

  it.each([
    {road_selected_variant_id:'invented'},
    {pick_place_street_section:'invented'},
    {road_archetype_id:'invented'},
    {width:7},
    {public_realm_lego:{family_id:'invented'}},
  ])('rejects a mismatched or invalid recipe draft: %j',change=>{
    const draft=manualStreet('existing-route','calgary_alley_draft3_v1',[[0,-100],[0,100]],false);
    draft.properties={...draft.properties,...change,junction_preview_candidate:true};
    expect(detectConnectedStreetIntersections([through,draft],true)).toHaveLength(0);
    const original=manualStreet(draft.id,'calgary_alley_draft3_v1',[[0,-100],[0,100]],true);
    expect(streetEditConnectionCheck(original,[through,original])(draft)).toBe(false);
  });
});
