import * as THREE from 'three';
import type {SiteZone,SiteZoneProperties} from '@/types';
import {parkOutlineProblem} from '@/features/pickPlace/parkOutline';
import clipping from 'polygon-clipping';
import {metersPerDegLon,METERS_PER_DEG_LAT} from '@/components/viewer/mapEngine/geoUtils';

type Pattern='soft'|'grain'|'pavers'|'brick'|'concrete';
export const GROUND_SURFACES:ReadonlyArray<{id:string;label:string;color:string;pattern:Pattern}>=[
  {id:'grass',label:'Grass',color:'#658347',pattern:'soft'},
  {id:'mown_grass',label:'Mown lawn',color:'#75984f',pattern:'soft'},
  {id:'dry_grass',label:'Dry grass',color:'#a49c64',pattern:'soft'},
  {id:'meadow',label:'Meadow ground',color:'#7f8b52',pattern:'soft'},
  {id:'snow',label:'Snow',color:'#f2f4f6',pattern:'soft'},
  {id:'sand',label:'Sand',color:'#d4c194',pattern:'grain'},
  {id:'gravel',label:'Natural gravel',color:'#a09887',pattern:'grain'},
  {id:'light_gravel',label:'Light gravel',color:'#d2cec1',pattern:'grain'},
  {id:'dark_gravel',label:'Dark gravel',color:'#656866',pattern:'grain'},
  {id:'black_pavers',label:'Black pavers',color:'#303336',pattern:'pavers'},
  {id:'charcoal_pavers',label:'Charcoal pavers',color:'#50545a',pattern:'pavers'},
  {id:'grey_pavers',label:'Grey pavers',color:'#91918b',pattern:'pavers'},
  {id:'light_pavers',label:'Light stone pavers',color:'#c9c6b9',pattern:'pavers'},
  {id:'red_brick',label:'Red brick',color:'#a45f47',pattern:'brick'},
  {id:'buff_brick',label:'Buff brick',color:'#bfa47e',pattern:'brick'},
  {id:'concrete',label:'Concrete',color:'#aaa9a1',pattern:'concrete'},
  {id:'light_concrete',label:'Light concrete',color:'#d0cec4',pattern:'concrete'},
  {id:'exposed_aggregate',label:'Exposed aggregate',color:'#ada58e',pattern:'grain'},
  {id:'asphalt',label:'Asphalt',color:'#414446',pattern:'grain'},
  {id:'red_asphalt',label:'Red asphalt',color:'#a05d4c',pattern:'grain'},
  {id:'blue_rubber',label:'Blue rubber surfacing',color:'#6196a9',pattern:'grain'},
  {id:'terracotta',label:'Terracotta tiles',color:'#bb7755',pattern:'pavers'},
  {id:'decomposed_granite',label:'Decomposed granite',color:'#c0a783',pattern:'grain'},
  {id:'mulch',label:'Bark mulch',color:'#70533c',pattern:'grain'},
  {id:'cobblestone',label:'Cobblestone',color:'#8a8983',pattern:'pavers'},
];
export const groundSurfaceProperties=(id:string):SiteZoneProperties=>({ground_surface_material:id});
export const groundSurfaceFor=(zone:Pick<SiteZone,'properties'>)=>GROUND_SURFACES.find(s=>s.id===zone.properties?.ground_surface_material);
export function groundSurfaceProblem(coordinates:number[][],boundary?:SiteZone|null):string|null {
  const problem=parkOutlineProblem(coordinates); if(problem)return problem;
  if(!boundary)return null;
  const origin=coordinates[0],sx=metersPerDegLon(origin[1]);
  const local=(ring:number[][])=>ring.map(p=>[(p[0]-origin[0])*sx,(p[1]-origin[1])*METERS_PER_DEG_LAT] as [number,number]);
  try {
    const outside=clipping.difference([local(coordinates)],[local(boundary.coordinates)]);
    const area=(ring:number[][])=>Math.abs(ring.reduce((sum,p,i)=>{const next=ring[(i+1)%ring.length];return sum+p[0]*next[1]-next[0]*p[1];},0))/2;
    return outside.reduce((sum,polygon)=>sum+area(polygon[0])-polygon.slice(1).reduce((holes,ring)=>holes+area(ring),0),0)<.0001
      ?null:'Keep the surface inside your site boundary.';
  } catch { return 'Choose a valid ground surface outline.'; }
}

/** Small repeatable metric textures; no downloads or generation calls. */
export function createGroundSurfaceTexture(surface:NonNullable<ReturnType<typeof groundSurfaceFor>>) {
  const canvas=document.createElement('canvas');canvas.width=canvas.height=128;
  const ctx=canvas.getContext('2d');
  if(ctx){
    ctx.fillStyle=surface.color;ctx.fillRect(0,0,128,128);
    for(let i=0;i<1400;i++){
      const x=(i*73+17)%128,y=(i*31+Math.floor(i/128)*19)%128;
      ctx.fillStyle=i%2?'rgba(255,255,255,.07)':'rgba(0,0,0,.06)';
      ctx.fillRect(x,y,surface.pattern==='grain'?2:1,surface.pattern==='soft'?3:1);
    }
    if(['pavers','brick','concrete'].includes(surface.pattern)){
      const rows=surface.pattern==='concrete'?2:surface.pattern==='brick'?12:6,cols=surface.pattern==='concrete'?2:4;
      ctx.strokeStyle='rgba(25,25,25,.25)';ctx.lineWidth=surface.pattern==='concrete'?.5:1;
      for(let row=0;row<=rows;row++){
        const y=row*128/rows;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(128,y);ctx.stroke();
        const shift=surface.pattern==='brick'&&row%2?64/cols:0;
        for(let col=-1;col<=cols;col++){const x=col*128/cols+shift;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x,y+128/rows);ctx.stroke();}
      }
    }
  }
  const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
  texture.wrapS=texture.wrapT=THREE.RepeatWrapping;texture.anisotropy=4;return texture;
}
