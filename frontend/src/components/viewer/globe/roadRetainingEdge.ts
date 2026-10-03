import * as THREE from 'three';
import type { RoadTerrainTransition } from './roadTerrainTransition';

export interface RoadEdgeBlocker { minX:number; maxX:number; minY:number; maxY:number }
export interface CorridorPoint { x:number; y:number }

/** Closed retaining faces and a separate coping cover the short ground blend.
 * The outer Google surface and its imagery stay intact. Sample both wall edges
 * densely so an object outside the road cannot silently become part of a wall. */
export function createRoadRetainingEdge(field:RoadTerrainTransition,side:-1|1,
  sample:(x:number,y:number)=>number|null,expected:(x:number,y:number)=>number|null) {
  if(field.edgeAt(side)!=='retaining')throw new Error('A retaining edge must be explicitly planned.');
  const inner=field.options.halfWidth+field.options.shoulderWidth-.1;
  const outer=field.outerWidthAt(side)+.1;
  const face:number[]=[],cap:number[]=[],rail:number[]=[],blockers:RoadEdgeBlocker[]=[];
  const rows:{x:number;low:number;high:number;drop:number}[]=[];
  const start=-field.options.endBlend,end=field.length+field.options.endBlend;
  const count=Math.ceil((end-start)/.25);
  let maximumHeight=0;
  for(let i=0;i<=count;i++) {
    const x=start+(end-start)*i/count;
    const heights=[inner,outer].map(y=>{
      const z=sample(x,side*y),reference=expected(x,side*y);
      if(z===null||!Number.isFinite(z)||reference===null||!Number.isFinite(reference)||Math.abs(z-reference)>1)
        throw new Error(`A retaining edge intersects an object or unverified ground. Move the route. ${JSON.stringify({x,y:side*y,z,reference})}`);
      return z;
    });
    const w=field.weight(x,0);
    const road=field.groundHeight(x,side*inner,heights[0])+.01*w;
    const height=Math.abs(road-heights[1]);maximumHeight=Math.max(maximumHeight,height);
    if(height>2.5)throw new Error('The retaining edge would exceed the supported height. Move or lengthen the route.');
    rows.push({x,low:Math.min(road,heights[1])-.08*w,high:Math.max(road,heights[1])+.12*w,drop:road-heights[1]});
  }
  const quad=(out:number[],a:number[],b:number[],c:number[],d:number[])=>out.push(...a,...b,...c,...a,...c,...d);
  const strip=(out:number[],a:typeof rows[number],b:typeof rows[number],loA:number,loB:number,hiA:number,hiB:number,
    y1=side*inner,y2=side*outer)=>{
    quad(out,[a.x,y1,loA],[b.x,y1,loB],[b.x,y1,hiB],[a.x,y1,hiA]);
    quad(out,[a.x,y2,loA],[a.x,y2,hiA],[b.x,y2,hiB],[b.x,y2,loB]);
    quad(out,[a.x,y1,hiA],[b.x,y1,hiB],[b.x,y2,hiB],[a.x,y2,hiA]);
    quad(out,[a.x,y1,loA],[a.x,y2,loA],[b.x,y2,loB],[b.x,y1,loB]);
    quad(out,[a.x,y1,loA],[a.x,y1,hiA],[a.x,y2,hiA],[a.x,y2,loA]);
    quad(out,[b.x,y1,loB],[b.x,y2,loB],[b.x,y2,hiB],[b.x,y1,hiB]);
  };
  for(let i=1;i<rows.length;i++) {
    const a=rows[i-1],b=rows[i];
    strip(face,a,b,a.low,b.low,Math.max(a.low,a.high-.06),Math.max(b.low,b.high-.06));
    strip(cap,a,b,Math.max(a.low,a.high-.06),Math.max(b.low,b.high-.06),a.high,b.high);
    if(Math.max(a.high-a.low,b.high-b.low)>.2)
      blockers.push({minX:a.x-.18,maxX:b.x+.18,minY:Math.min(side*inner,side*outer)-.18,maxY:Math.max(side*inner,side*outer)+.18});
    // A visible guard marks a fill-side drop; this is conceptual geometry,
    // not a claim of engineered retaining or accessibility compliance.
    if(Math.max(a.drop,b.drop)>.6) {
      const y=side*(inner+outer)/2;
      strip(rail,a,b,a.high+.98,b.high+.98,a.high+1.04,b.high+1.04,y-.035,y+.035);
      strip(rail,a,b,a.high+.48,b.high+.48,a.high+.52,b.high+.52,y-.025,y+.025);
      if(i%8===0||i===1||rows[i-2]?.drop<=.6) {
        const post={...a,x:Math.min(b.x,a.x+.06)};
        strip(rail,a,post,a.high,a.high,a.high+1.04,a.high+1.04,y-.035,y+.035);
      }
    }
  }
  const geometry=(values:number[])=>{
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(values,3));
    // Metre-based coordinates preserve the catalogue material's physical scale.
    const uv:number[]=[];
    for(let i=0;i<values.length;i+=3)uv.push(values[i],values[i+2]+values[i+1]);
    g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.computeVertexNormals();return g;
  };
  return {face:geometry(face),cap:geometry(cap),rail:geometry(rail),blockers,maximumHeight};
}

/** Swept segment checks prevent tunnelling. Sliding preserves movement along
 * a wall, and a walker caught by a newly installed wall can move back out. */
export function constrainRoadEdgeWalk(from:CorridorPoint,to:CorridorPoint,blockers:RoadEdgeBlocker[]):CorridorPoint {
  const contains=(b:RoadEdgeBlocker,p:CorridorPoint)=>p.x>b.minX&&p.x<b.maxX&&p.y>b.minY&&p.y<b.maxY;
  const clear=(target:CorridorPoint)=>!blockers.some(b=>{
    if(contains(b,from))return contains(b,target);
    let enter=0,leave=1;
    for(const [origin,delta,low,high] of [[from.x,target.x-from.x,b.minX,b.maxX],[from.y,target.y-from.y,b.minY,b.maxY]]) {
      if(Math.abs(delta)<1e-12){if(origin<=low||origin>=high)return false;}
      else {const a=(low-origin)/delta,c=(high-origin)/delta;enter=Math.max(enter,Math.min(a,c));leave=Math.min(leave,Math.max(a,c));}
    }
    return enter<leave&&leave>0&&enter<1;
  });
  if(clear(to))return to;
  const along={x:to.x,y:from.y};if(clear(along))return along;
  const across={x:from.x,y:to.y};if(clear(across))return across;
  return {...from};
}
