import { expect, it } from 'vitest';
import manual from '@/data/streetManual.json';
import { MANUAL_STREET_ASSETS, ALL_MANUAL_STREET_ASSETS } from '@/features/pickPlace/assetRegistry';
import { CANONICAL_CHOICES } from '@/features/pickPlace/canonicalCatalogue';
import { pickerCategory } from '@/features/pickPlace/pickerCategories';
import { streetDesignUpdate } from '@/features/pickPlace/canonicalStreetPlacement';
import { streetAssetForZone } from '@/features/pickPlace/streetPlacement';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import type { SiteZone } from '@/types';
import { resolvePilotStreetSectionProfile } from './streetSectionProfiles';
import { buildRibbonBandGeometry, densifyPolyline } from './streetMesh3D';
import { buildStreetFamilyFixturePlacements } from './streetFamilyFurniture';
import { streetSurfaceMaskZone } from './streetSurfaceMask';
import { resolveStreetBandMaterial } from './streetSurfaceMaterials';

const stable = (v: unknown): string => Array.isArray(v) ? `[${v.map(stable).join(',')}]`
  : v && typeof v === 'object' ? `{${Object.entries(v).sort(([a],[b])=>a.localeCompare(b)).map(([k,x])=>`${JSON.stringify(k)}:${stable(x)}`).join(',')}}` : JSON.stringify(v);
const widths=[6.5,16,18,21,20,20,26,27,33,36,36,46,60];
const line=[[0,0],[180/111320,0]];
const points=densifyPolyline([{x:0,y:0},{x:180,y:0}],2);
it.each(MANUAL_STREET_ASSETS)('$label retains metric geometry, identity and clearance', async (asset) => {
  const row=manual.find(r=>r.variantId===asset.model.variantId)!;
  if (!row.sourceEdition) expect(row.widthM).toBe(widths[Number(row.figure)-1]);
  expect(Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(stable(row.section)))),b=>b.toString(16).padStart(2,'0')).join('')).toBe(row.sourceSectionSha256);
  const profile=resolvePilotStreetSectionProfile({properties:asset.properties})!;
  expect(profile.manualSection).toBe(true);
  expect(profile.rowM).toBe(row.widthM);
  expect(profile.bands.map(b=>b.widthM)).toEqual(row.section.zones.map(z=>z.width_m));
  for(const band of profile.bands){
    const geometry=buildRibbonBandGeometry(points,band.startM,band.endM,band.liftM)!;
    geometry.computeBoundingBox();
    expect(geometry.boundingBox!.max.y-geometry.boundingBox!.min.y).toBeCloseTo(band.widthM,4);
    geometry.dispose();
  }
  expect(profile.renderCurbs).toBe(row.curbed);
  const fixtures=buildStreetFamilyFixturePlacements({points,profile,sectionScale:1,enabled:true});
  for(const tree of fixtures.trees) expect(profile.bands.some(b=>(b.kind==='planting' || (profile.manualLandscape?.medianTrees && b.kind==='median')) && tree.offsetM>b.startM && tree.offsetM<b.endM)).toBe(true);
  expect(fixtures.transitShelters).toHaveLength(0);
  expect(fixtures.parkedVehicles).toHaveLength(0);
  expect(fixtures.bollards).toHaveLength(0); // raised cycle tracks do not need an invented bollard system
  const zone={id:'test',project_id:'qa',color:'#888',sort_order:0,created_at:'',updated_at:'',zone_type:'road',properties:{...asset.properties,plan_centerline:line},coordinates:bufferLineToPolygon(line,row.widthM)} as SiteZone;
  const saved=JSON.parse(JSON.stringify({...zone,...streetDesignUpdate(zone,asset)}));
  expect(streetAssetForZone(saved)?.model.variantId).toBe(row.variantId);
  expect(saved.properties.width).toBe(row.widthM);
  const choice=CANONICAL_CHOICES.find(c=>c.placements.includes(asset))!;
  expect(pickerCategory(choice)).toBe('street-manual');
});
it('locks the three sourced sections and retains the original bindings outside the picker', () => {
  const expected = {
    calgary_local: [.3,1.8,2.65,3.25,3.25,2.65,1.8,.3],
    calgary_local_industrial: [.3,1.6,2.6,4.5,4.5,2.6,1.6,.3],
    calgary_collector: [.3,3,2.7,2.2,3.3,3.3,2.2,3.9,1.8,.3],
  };
  for (const [id, widths] of Object.entries(expected)) {
    const current = MANUAL_STREET_ASSETS.find(a => a.properties.road_archetype_id === id)!;
    expect(current.model.variantId).toBe(`${id}_draft3_v1`);
    const profile = resolvePilotStreetSectionProfile({properties: current.properties})!;
    expect(profile.bands.map(b => b.widthM)).toEqual(widths);
    expect(profile.manualLandscape?.treeSpacingM).toBe(10);
    const fixtures = buildStreetFamilyFixturePlacements({points,profile,sectionScale:1,enabled:true});
    expect(fixtures.trees.length).toBeGreaterThan(10);
    const legacy = ALL_MANUAL_STREET_ASSETS.find(a => a.model.variantId === `${id}_manual_v1`)!;
    expect(streetAssetForZone({zone_type:'road',properties:legacy.properties})?.model.variantId).toBe(legacy.model.variantId);
    expect(MANUAL_STREET_ASSETS).not.toContain(legacy);
  }
  const collector = resolvePilotStreetSectionProfile({properties:MANUAL_STREET_ASSETS.find(a => a.properties.road_archetype_id === 'calgary_collector')!.properties})!;
  expect(collector.bands.filter(b => b.kind === 'path').map(b => b.widthM)).toEqual([3]);
  expect(collector.bands.filter(b => b.kind === 'parking').map(b => b.widthM)).toEqual([2.2,2.2]);
});
it('industrial utility strip is retained outside its asymmetric constructed mask',()=>{
  const asset=ALL_MANUAL_STREET_ASSETS.find(a=>a.model.variantId==='calgary_collector_industrial_manual_v1')!;
  const zone={id:'test',project_id:'qa',color:'#888',sort_order:0,created_at:'',updated_at:'',zone_type:'road',properties:{...asset.properties,plan_centerline:line},coordinates:bufferLineToPolygon(line,26)} as SiteZone;
  const ys=streetSurfaceMaskZone(zone).coordinates.map(p=>p[1]*111320);
  expect(Math.min(...ys)).toBeCloseTo(-12.7,4);
  expect(Math.max(...ys)).toBeCloseTo(11,4);
});
it('matches the arterial drawing envelopes and adds median trees only where illustrated', () => {
  for (const [id,width,lanes,median] of [
    ['calgary_arterial_4lane_50',30,4,4], ['calgary_arterial_4lane_70',36,4,6], ['calgary_arterial_6lane',46,6,9],
  ] as const) {
    const asset=MANUAL_STREET_ASSETS.find(a=>a.properties.road_archetype_id===id)!;
    const profile=resolvePilotStreetSectionProfile({properties:asset.properties})!;
    expect(profile.rowM).toBe(width);
    expect(profile.bands.filter(b=>b.kind==='motor')).toHaveLength(lanes);
    expect(profile.bands.filter(b=>b.kind==='median').map(b=>b.widthM)).toEqual([median]);
    expect(profile.bands.filter(b=>b.kind==='path').map(b=>b.widthM)).toEqual([3,3]);
    const fixtures=buildStreetFamilyFixturePlacements({points,profile,sectionScale:1,enabled:true});
    expect(fixtures.trees.some(tree=>Math.abs(tree.offsetM)<.01)).toBe(id!=='calgary_arterial_4lane_50');
    expect(fixtures.benches.every(b=>Math.abs(b.offsetM)>median/2)).toBe(true);
  }
});
it('preserves raised cycling, grass verges and opposing turn-lane markings',()=>{
  const profile=(id:string)=>resolvePilotStreetSectionProfile({properties:MANUAL_STREET_ASSETS.find(a=>a.properties.road_archetype_id===id)!.properties})!;
  const urban=profile('calgary_collector_high_activity');
  expect(urban.bands.filter(b=>b.kind==='parking').map(b=>b.widthM)).toEqual([2.3,2.3]);
  expect(urban.bands.find(b=>b.kind==='cycle')!.liftM).toBeGreaterThan(urban.bands.find(b=>b.kind==='motor')!.liftM+.04);
  const rural=resolvePilotStreetSectionProfile({properties:ALL_MANUAL_STREET_ASSETS.find(a=>a.properties.road_archetype_id==='calgary_local_rural')!.properties})!;
  for(const band of rural.bands.filter(b=>b.sourceType==='ditch')) expect(resolveStreetBandMaterial(rural,band).kind).toBe('planting_grass');
  const turn=profile('calgary_collector_industrial');
  expect(turn.markings.filter(m=>m.color==='#dfb846' && !m.dashed)).toHaveLength(2);
  expect(profile('calgary_alley').markings).toHaveLength(0);
});
it('offers twelve sourced types, preserves rural saves and clearly scopes the skeletal surface model', () => {
  expect(MANUAL_STREET_ASSETS).toHaveLength(12);
  expect(new Set(MANUAL_STREET_ASSETS.map(a=>a.properties.road_archetype_id)).size).toBe(12);
  expect(MANUAL_STREET_ASSETS.every(a=>String(a.properties.road_standard_citation).includes('Draft 3'))).toBe(true);
  const rural=ALL_MANUAL_STREET_ASSETS.find(a=>a.properties.road_archetype_id==='calgary_local_rural')!;
  expect(MANUAL_STREET_ASSETS).not.toContain(rural);
  expect(streetAssetForZone({zone_type:'road',properties:rural.properties})).toBe(rural);
  const skeletal=MANUAL_STREET_ASSETS.find(a=>a.properties.road_archetype_id==='calgary_skeletal')!;
  expect(skeletal.description).toContain('ditch slopes');
  const profile=resolvePilotStreetSectionProfile({properties:skeletal.properties})!;
  expect(profile.bands.filter(b=>b.kind==='shoulder' && b.sourceType==='shoulder').map(b=>b.widthM)).toEqual([3,2.5,2.5,3]);
  expect(profile.bands.find(b=>b.kind==='median')?.widthM).toBe(1);
});
