/** Intentional bridge-owned modules, separate from immutable fixed source scenes. */
/** Lane counts come from the two source road programmes, not deck width. */
export function sourceBridgeLaneCount(variant:string):number {
  return variant==='stone_arch_road_bridge_route_v1'?4:variant==='steel_truss_road_bridge_route_v1'?2:0;
}
export interface BridgeDeformation {
  mode: 'longitudinal-core-v1' | 'circle-radius-v1';
  nativeLengthM: number; requestedLengthM: number;
  rigidEndM?: number; radiusM?: number; centerAcrossM?: number;
  collarHeightM?: number;
}
export interface SourceBridgePart {
  kind: string; lengthM: number; mode: 'fixed' | 'span' | 'repeat';
  deformation?: Omit<BridgeDeformation,'requestedLengthM'>;
  companions?: Array<{kind:string;pitchM:number;lengthM:number}>;
}
export interface SourceSpanBridge {
  parts: SourceBridgePart[]; deckHeightM: number; clearWidthM: number;
  approachM: number; endM: number; trafficKind: 'walk'|'cycle'|'road'|'rail';
  walkingPaths?: Array<{partKind?:string;widthM:number;points:[number,number,number][];surfacePolygon?:[number,number,number][]}>;
}
export interface BridgePartPlacement {
  kind: string; startM: number; lengthM: number; scale: number;
  companion?: boolean; deformation?: BridgeDeformation;
}

/** Rigid ends/pods do not stretch. Only declared spans share the remaining length. */
export function sourceSpanBridgeLayout(bridge:SourceSpanBridge,length:number):BridgePartPlacement[] {
  const fixed=bridge.parts.filter(p=>p.mode==='fixed').reduce((n,p)=>n+p.lengthM,0);
  const flexible=bridge.parts.filter(p=>p.mode!=='fixed').reduce((n,p)=>n+p.lengthM,0);
  if(!Number.isFinite(length)||length<=fixed||flexible<=0
    ||bridge.parts.some(p=>!Number.isFinite(p.lengthM)||p.lengthM<=0))
    throw new Error('The bridge span must leave room for its complete end structures.');
  const ratio=(length-fixed)/flexible,result:BridgePartPlacement[]=[];
  let startM=0;
  for(const part of bridge.parts){
    const total=part.lengthM*(part.mode==='fixed'?1:ratio);
    const count=part.mode==='repeat'?Math.max(1,Math.round(total/part.lengthM)):1;
    const size=total/count;
    for(let i=0;i<count;i++)result.push({kind:part.kind,startM:startM+i*size,lengthM:size,
      scale:part.deformation?1:size/part.lengthM,
      ...(part.deformation?{deformation:{...part.deformation,requestedLengthM:size}}:{})});
    for(const companion of part.companions??[]){
      if(total<companion.lengthM-1e-6)throw new Error('The bridge span needs room for a complete source landscape and support module.');
      const copies=Math.max(0,Math.floor((total-companion.lengthM+1e-6)/companion.pitchM)+1);
      const inset=(total-(copies-1)*companion.pitchM-companion.lengthM)/2;
      for(let i=0;i<copies;i++)result.push({kind:companion.kind,startM:startM+inset+i*companion.pitchM,
        lengthM:companion.lengthM,scale:1,companion:true});
    }
    startM+=total;
  }
  return result;
}

/** Source glTF coordinates are X across / Y up / -Z along. */
export function deformSourceBridgePoint(point:[number,number,number],d:BridgeDeformation,role='ring'):[number,number,number] {
  const [x,y,z]=point,k=d.requestedLengthM/d.nativeLengthM;
  if(d.mode==='longitudinal-core-v1'){
    const core=d.nativeLengthM/2-(d.rigidEndM??0),s=-z;
    const along=s+(d.requestedLengthM-d.nativeLengthM)/2*Math.max(-1,Math.min(1,s/core));
    return [x,y,-along];
  }
  const center=d.centerAcrossM??0,radius=d.radiusM??1;
  if(role==='pylon')return [x+center*(k-1),y,z];
  const dx=x-center,r=Math.hypot(dx,z);
  if(role==='cables'){
    const weight=Math.max(0,Math.min(1,((d.collarHeightM??48)-y)/((d.collarHeightM??48)-6.3)));
    return [x+center*(k-1)+(r?dx/r:0)*radius*(k-1)*weight,y,z+(r?z/r:0)*radius*(k-1)*weight];
  }
  if(r<1e-8)return [center*k,y,z];
  const target=radius*k+(r-radius);
  return [center*k+dx/r*target,y,z/r*target];
}

function mappedWalkingPoint(bridge:SourceSpanBridge,point:[number,number,number],length:number,partKind?:string):[number,number,number] {
  const layout=sourceSpanBridgeLayout(bridge,length).filter(p=>!p.companion);
  let nativeStart=0;
  for(const part of bridge.parts){
    if(partKind?part.kind===partKind:point[1]<=nativeStart+part.lengthM+1e-6){
      const group=layout.filter(p=>p.kind===part.kind),start=group[0].startM;
      const size=group.reduce((n,p)=>n+p.lengthM,0),along=partKind?point[1]+part.lengthM/2:point[1]-nativeStart,t=along/part.lengthM;
      if(part.deformation){
        const p=deformSourceBridgePoint([point[0],point[2],-(along-part.lengthM/2)],
          {...part.deformation,requestedLengthM:size});
        return [p[0],start+size/2-p[2],p[1]];
      }
      return [point[0],start+size*t,point[2]];
    }
    nativeStart+=part.lengthM;
  }
  return [point[0],length,point[2]];
}

/** Camera support follows the actual native curves and approaches, never the box. */
export function sourceSpanBridgeWalkingHeight(bridge:SourceSpanBridge,lateral:number,station:number,length:number,preferredHeight?:number):number|null {
  if(bridge.trafficKind==='rail'||![lateral,station,length].every(Number.isFinite)||station<0||station>length)return null;
  let nearest:{distance:number;height:number}|undefined;
  const accept=(height:number,distance:number)=>{
    if(preferredHeight!==undefined&&Math.abs(height-preferredHeight)>.65)return;
    const score=distance+(preferredHeight===undefined?0:Math.abs(height-preferredHeight)*1e-6);
    if(!nearest||score<nearest.distance)nearest={distance:score,height};
  };
  for(const path of bridge.walkingPaths??[]){
    if(path.surfacePolygon){
      const polygon=path.surfacePolygon.map(p=>mappedWalkingPoint(bridge,p,length,path.partKind));
      for(let i=1;i<polygon.length-1;i++){
        const a=polygon[0],b=polygon[i],c=polygon[i+1];
        const bx=b[0]-a[0],by=b[1]-a[1],cx=c[0]-a[0],cy=c[1]-a[1],det=bx*cy-by*cx;
        if(Math.abs(det)<1e-10)continue;
        const x=lateral-a[0],y=station-a[1],u=(x*cy-y*cx)/det,v=(bx*y-by*x)/det;
        if(u>=-1e-6&&v>=-1e-6&&u+v<=1+1e-6)accept(a[2]+u*(b[2]-a[2])+v*(c[2]-a[2]),0);
      }
      continue;
    }
    const points=path.points.map(p=>mappedWalkingPoint(bridge,p,length,path.partKind));
    for(let i=1;i<points.length;i++){
      const a=points[i-1],b=points[i],dx=b[0]-a[0],dy=b[1]-a[1],size=dx*dx+dy*dy;
      if(size<1e-8)continue;
      const t=((lateral-a[0])*dx+(station-a[1])*dy)/size;
      if(t< -1e-6||t>1+1e-6)continue;
      const distance=Math.hypot(lateral-a[0]-dx*t,station-a[1]-dy*t);
      const height=a[2]+(b[2]-a[2])*t;
      if(distance<=path.widthM/2)accept(height,distance);
    }
  }
  return nearest?.height??null;
}
