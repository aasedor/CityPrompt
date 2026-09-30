import { expect, it } from 'vitest';
import manual from '@/data/streetManual.json';
import { MANUAL_STREET_ASSETS } from '@/features/pickPlace/assetRegistry';
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
  expect(row.widthM).toBe(widths[Number(row.figure)-1]);
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
  for(const tree of fixtures.trees) expect(profile.bands.some(b=>b.kind==='planting' && tree.offsetM>b.startM && tree.offsetM<b.endM)).toBe(true);
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
it('industrial utility strip is retained outside its asymmetric constructed mask',()=>{
  const asset=MANUAL_STREET_ASSETS.find(a=>a.properties.road_archetype_id==='calgary_collector_industrial')!;
  const zone={id:'test',project_id:'qa',color:'#888',sort_order:0,created_at:'',updated_at:'',zone_type:'road',properties:{...asset.properties,plan_centerline:line},coordinates:bufferLineToPolygon(line,26)} as SiteZone;
  const ys=streetSurfaceMaskZone(zone).coordinates.map(p=>p[1]*111320);
  expect(Math.min(...ys)).toBeCloseTo(-12.7,4);
  expect(Math.max(...ys)).toBeCloseTo(11,4);
});
it('preserves raised cycling, grass verges and opposing turn-lane markings',()=>{
  const profile=(id:string)=>resolvePilotStreetSectionProfile({properties:MANUAL_STREET_ASSETS.find(a=>a.properties.road_archetype_id===id)!.properties})!;
  const urban=profile('calgary_collector_high_activity');
  expect(urban.bands.filter(b=>b.kind==='parking').map(b=>b.widthM)).toEqual([2.3,2.3]);
  expect(urban.bands.find(b=>b.kind==='cycle')!.liftM).toBeGreaterThan(urban.bands.find(b=>b.kind==='motor')!.liftM+.04);
  const rural=profile('calgary_local_rural');
  for(const band of rural.bands.filter(b=>b.sourceType==='ditch')) expect(resolveStreetBandMaterial(rural,band).kind).toBe('planting_grass');
  const turn=profile('calgary_collector_industrial');
  expect(turn.markings.filter(m=>m.color==='#dfb846' && !m.dashed)).toHaveLength(2);
  expect(profile('calgary_alley').markings).toHaveLength(0);
});
