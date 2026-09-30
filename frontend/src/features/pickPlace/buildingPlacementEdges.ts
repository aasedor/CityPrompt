import type { SiteZone } from '@/types';
import { CATALOGUE_ASSETS } from './assetRegistry';
import { footprintProgramSupports } from './buildingFootprintProgram';
import { storeyProgramSupports } from './buildingStoreyProgram';
import edges from '@/data/buildingPlacementEdges.json';
import { computeCentroid, metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';

type PlacedZone = Pick<SiteZone, 'coordinates' | 'properties'> & Partial<Pick<SiteZone,'zone_type'>>;

/** Only the exact reviewed, single native assembly can release plot padding.
 * Unknown revisions, repeated houses and custom footprints retain their plot. */
export function buildingEdgeContract(zone: PlacedZone) {
  const p=zone.properties;
  if (!p || p.native_plot_axes!==true || p.native_home_plot===true || zone.coordinates.length!==4
    || (zone.zone_type && !['building','residential'].includes(zone.zone_type))) return null;
  // Custom/legacy quadrilaterals are not necessarily the rectangular native frame.
  const ring=zone.coordinates, east=metersPerDegLon(ring[0][1]);
  if(ring.some(point=>!Number.isFinite(point[0]+point[1])))return null;
  const vectors=ring.map((point,i)=>[(ring[(i+1)%4][0]-point[0])*east,(ring[(i+1)%4][1]-point[1])*METERS_PER_DEG_LAT]);
  if(vectors.some((v,i)=>{
    const next=vectors[(i+1)%4],opposite=vectors[(i+2)%4];
    return Math.hypot(...v)<.01 || Math.abs(v[0]*next[0]+v[1]*next[1])>Math.hypot(...v)*Math.hypot(...next)*.001
      || Math.hypot(v[0]+opposite[0],v[1]+opposite[1])>.01;
  }) || vectors[0][0]*vectors[1][1]-vectors[0][1]*vectors[1][0]<=0)return null;
  const asset=CATALOGUE_ASSETS.find(a=>a.id===p.pick_place_asset);
  const row=edges.buildings.find(r=>r.assetId===asset?.id);
  if (!row || asset?.kind!=='object' || asset.zoneType!=='building' || asset.reshapeMode!=='fixed_native'
    || asset.model.variantId!==row.variantId || asset.model.revision!==row.revision
    || p.development_selected_variant_id!==row.variantId || p.pick_place_model_revision!==row.revision) return null;
  if(p.development_height_override_m!=null && (!asset.storeyProgram || !storeyProgramSupports(
    asset.storeyProgram,p.floor_count ?? p.floors,p.development_height_override_m,
  )))return null;
  let scale=Number(p.building_footprint_scale ?? 1);
  if (!Number.isFinite(scale) || (asset.footprintProgram
    ? !footprintProgramSupports(asset.footprintProgram,scale) : scale!==1)) return null;
  if(scale!==1 && p.building_footprint_program_id!==asset.footprintProgram?.id)return null;
  if(row.plotFit){
    const w=Math.hypot(...vectors[0]),d=Math.hypot(...vectors[1]),fit=row.plotFit;
    if(w<fit.minWidthM-.01 || w>fit.maxWidthM+.01 || d<fit.minDepthM-.01 || d>fit.maxDepthM+.01)return null;
    // Match the compiler's 0.1 m targets and five-decimal uniform XY scale.
    scale=Math.round(Math.min(Math.round(w*10)/10/row.nativeWidthM,Math.round(d*10)/10/row.nativeDepthM,fit.maxScale)*1e5)/1e5;
  }
  return {...row, width:row.nativeWidthM*scale, depth:row.nativeDepthM*scale};
}

/** Local -Y is the authored front. The plot remains the compilation/ground
 * frame; this separate envelope controls contact with neighbouring objects. */
export function buildingPlacementEnvelope(zone: PlacedZone): number[][] {
  const contract=buildingEdgeContract(zone), ring=zone.coordinates;
  if (!contract || ring.some(p=>!Number.isFinite(p[0]+p[1]))) return ring;
  const center=computeCentroid(ring), east=metersPerDegLon(center[1]);
  const v=[(ring[1][0]-ring[0][0])*east,(ring[1][1]-ring[0][1])*METERS_PER_DEG_LAT];
  const w=Math.hypot(...v), d=Math.hypot((ring[2][0]-ring[1][0])*east,(ring[2][1]-ring[1][1])*METERS_PER_DEG_LAT);
  if(w<.01 || d<.01)return ring;
  const c=v[0]/w,s=v[1]/w;
  const left=contract.left==='abut'?-contract.width/2:-Math.max(w,contract.width)/2;
  const right=contract.right==='abut'?contract.width/2:Math.max(w,contract.width)/2;
  const front=-contract.depth/2,rear=Math.max(d,contract.depth)/2;
  return [[left,front],[right,front],[right,rear],[left,rear]].map(([x,y])=>[
    center[0]+(x*c-y*s)/east,center[1]+(x*s+y*c)/METERS_PER_DEG_LAT,
  ]);
}

/** Near-edge attraction, without rotating or changing the saved plot. Only
 * opposing approved side edges and the authored front can attract. */
export function buildingEdgeSnapCandidates(zone: PlacedZone, neighbours: SiteZone[], distanceM=1) {
  const contract=buildingEdgeContract(zone);
  if(!contract)return [];
  const origin=zone.coordinates[0],east=metersPerDegLon(origin[1]);
  const local=(p:number[])=>[(p[0]-origin[0])*east,(p[1]-origin[1])*METERS_PER_DEG_LAT];
  const ring=buildingPlacementEnvelope(zone).map(local);
  const candidates:{coordinates:number[][];distance:number}[]=[];
  for(const other of neighbours) {
    const road=other.zone_type==='road',otherContract=buildingEdgeContract(other);
    if(!road&&!otherContract)continue;
    const target=(road?other.coordinates:buildingPlacementEnvelope(other)).map(local);
    const ownEdges=road?[0]:[...(contract.right==='abut'?[1]:[]),...(contract.left==='abut'?[3]:[])];
    const targetEdges=road?target.map((_,i)=>i):[...(otherContract?.right==='abut'?[1]:[]),...(otherContract?.left==='abut'?[3]:[])];
    for(const i of ownEdges)for(const j of targetEdges) {
      const a=ring[i],b=ring[(i+1)%ring.length],q=target[j],r=target[(j+1)%target.length];
      const length=Math.hypot(b[0]-a[0],b[1]-a[1]),otherLength=Math.hypot(r[0]-q[0],r[1]-q[1]);
      if(length<.01||otherLength<.01)continue;
      const t=[(b[0]-a[0])/length,(b[1]-a[1])/length],n=[t[1],-t[0]];
      // Parallel faces only; angled corners must still pass full polygon checks.
      if(Math.abs(t[0]*(r[1]-q[1])-t[1]*(r[0]-q[0]))/otherLength>.001)continue;
      const along=(p:number[])=>p[0]*t[0]+p[1]*t[1];
      const overlap=Math.min(Math.max(along(a),along(b)),Math.max(along(q),along(r)))
        -Math.max(Math.min(along(a),along(b)),Math.min(along(q),along(r)));
      if(overlap<1)continue;
      const shift=(q[0]-a[0])*n[0]+(q[1]-a[1])*n[1]-.02;
      if(Math.abs(shift)>distanceM||Math.abs(shift)<.001)continue;
      candidates.push({distance:Math.abs(shift),coordinates:zone.coordinates.map(p=>[
        p[0]+n[0]*shift/east,p[1]+n[1]*shift/METERS_PER_DEG_LAT,
      ])});
    }
  }
  return candidates.sort((a,b)=>a.distance-b.distance);
}
