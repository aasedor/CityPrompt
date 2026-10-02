import * as THREE from 'three';
import type { RoadTerrainTransition } from './roadTerrainTransition';

interface Vertex { p:THREE.Vector3; attributes:number[][] }
/** Tessellate only triangles touching the transition and retain their original
 * imagery coordinates. The returned geometry is owned by the caller; source
 * buffers/materials/textures are never mutated or disposed here. */
export function createTransitionTileGeometry(source:THREE.BufferGeometry, meshToCorridor:THREE.Matrix4,
  field:RoadTerrainTransition, maximumVertices=300_000,
  expectedGround?:(x:number,y:number)=>number|null):THREE.BufferGeometry|null {
  if(Object.keys(source.morphAttributes).length || !source.getAttribute('position'))
    throw new Error('Unsupported terrain geometry.');
  const pos=source.getAttribute('position'), names=Object.keys(source.attributes).filter(n=>n!=='position');
  const attributes=names.map(n=>source.getAttribute(n));
  const inverse=meshToCorridor.clone().invert(), output:number[]=[], outputAttributes=attributes.map(()=>[] as number[]);
  const normalIndex=names.indexOf('normal'),toCorridorNormal=new THREE.Matrix3().getNormalMatrix(meshToCorridor),
    toMeshNormal=new THREE.Matrix3().getNormalMatrix(inverse);
  const groups:{start:number;count:number;materialIndex:number}[]=[];
  const index=source.index, count=index?.count??pos.count;
  let changed=false;
  const near=(v:Vertex[])=>Math.max(...v.map(q=>q.p.x))>=-field.options.endBlend
    && Math.min(...v.map(q=>q.p.x))<=field.length+field.options.endBlend
    && Math.max(...v.map(q=>q.p.y))>=-field.outerWidth && Math.min(...v.map(q=>q.p.y))<=field.outerWidth;
  const vertex=(i:number):Vertex=>({p:new THREE.Vector3().fromBufferAttribute(pos,i).applyMatrix4(meshToCorridor),
    attributes:attributes.map(a=>Array.from({length:a.itemSize},(_,j)=>a.getComponent(i,j)))});
  const middle=(a:Vertex,b:Vertex):Vertex=>({p:a.p.clone().add(b.p).multiplyScalar(.5),
    attributes:a.attributes.map((values,i)=>values.map((v,j)=>(v+b.attributes[i][j])/2))});
  // A short blend beneath a wall needs an exact shared outer edge. Refinement
  // alone can leave a triangle spanning the edge and pull untouched ground down.
  const split=(polygon:Vertex[],y:number)=>{
    const pieces:Vertex[][]=[];
    for(const sign of [-1,1]) {
      const out:Vertex[]=[];
      polygon.forEach((a,i)=>{
        const b=polygon[(i+1)%polygon.length],insideA=sign*(a.p.y-y)>=0,insideB=sign*(b.p.y-y)>=0;
        if(insideA)out.push(a);
        if(insideA!==insideB) {
          const t=(y-a.p.y)/(b.p.y-a.p.y);
          const p=a.p.clone().lerp(b.p,t);p.y=y;
          out.push({p,attributes:a.attributes.map((v,k)=>v.map((n,j)=>n+(b.attributes[k][j]-n)*t))});
        }
      });
      if(out.length>=3)pieces.push(out);
    }
    return pieces;
  };
  const emit=(triangle:Vertex[],materialIndex:number,depth=0)=>{
    const intersects=near(triangle);
    const distances=triangle.map((a,i)=>{const b=triangle[(i+1)%3];return (a.p.x-b.p.x)**2+(a.p.y-b.p.y)**2;});
    const edge=distances.indexOf(Math.max(...distances));
    // Fine geometry is needed because only displacing coarse original vertices
    // leaves a jagged edge. Longest-edge bisection bounds approximation error.
    if(intersects && distances[edge]>.5**2) {
      if(depth>=22) throw new Error('Terrain triangles exceed the refinement budget.');
      const a=triangle[edge],b=triangle[(edge+1)%3],c=triangle[(edge+2)%3],m=middle(a,b);
      emit([a,m,c],materialIndex,depth+1);emit([m,b,c],materialIndex,depth+1);return;
    }
    if(output.length/3+3>maximumVertices) throw new Error('Terrain transition exceeds the geometry budget.');
    const start=output.length/3;
    triangle.forEach(v=>{
      const p=v.p.clone();
      if(intersects && field.weight(p.x,p.y)>0 && expectedGround) {
        const expected=expectedGround(p.x,p.y);
        if(expected===null || !Number.isFinite(expected) || Math.abs(p.z-expected)>1)
          throw new Error('A narrow object or unsupported terrain triangle intersects the transition. Move the route to clear ground.');
      }
      let normal:number[]|undefined;
      if(intersects&&normalIndex>=0&&field.weight(p.x,p.y)>0){
        const n=new THREE.Vector3(...v.attributes[normalIndex] as [number,number,number]).applyMatrix3(toCorridorNormal).normalize();
        if(Math.abs(n.z)>.1){
          const dx=-n.x/n.z,dy=-n.y/n.z,e=.001;
          const gx=(field.groundHeight(p.x+e,p.y,p.z+dx*e)-field.groundHeight(p.x-e,p.y,p.z-dx*e))/(2*e);
          const gy=(field.groundHeight(p.x,p.y+e,p.z+dy*e)-field.groundHeight(p.x,p.y-e,p.z-dy*e))/(2*e);
          normal=new THREE.Vector3(-gx,-gy,1).normalize().applyMatrix3(toMeshNormal).normalize().toArray();
        }
      }
      if(intersects) { const z=field.groundHeight(p.x,p.y,p.z);if(Math.abs(z-p.z)>1e-7)changed=true;p.z=z; }
      p.applyMatrix4(inverse);output.push(p.x,p.y,p.z);
      v.attributes.forEach((values,i)=>outputAttributes[i].push(...(i===normalIndex&&normal?normal:values)));
    });
    const last=groups[groups.length-1];
    if(last?.materialIndex===materialIndex)last.count+=3;else groups.push({start,count:3,materialIndex});
  };
  for(let i=0;i<count;i+=3) {
    const materialIndex=source.groups.find(g=>i>=g.start&&i<g.start+g.count)?.materialIndex??0;
    let polygons=[[vertex(index?index.getX(i):i),vertex(index?index.getX(i+1):i+1),vertex(index?index.getX(i+2):i+2)]];
    for(const side of [-1,1] as const)if(field.edgeAt(side)==='retaining') {
      // Both limits matter: the inner split keeps steep hidden triangles from
      // poking through the shoulder at the foot of the wall.
      for(const width of [field.options.halfWidth+field.options.shoulderWidth,field.outerWidthAt(side)]) {
        const boundary=side*width;
        polygons=polygons.flatMap(p=>Math.min(...p.map(v=>v.p.y))<boundary&&Math.max(...p.map(v=>v.p.y))>boundary?split(p,boundary):[p]);
      }
    }
    for(const polygon of polygons)for(let j=1;j<polygon.length-1;j++)emit([polygon[0],polygon[j],polygon[j+1]],materialIndex);
  }
  if(!changed)return null;
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(output,3));
  names.forEach((n,i)=>geometry.setAttribute(n,new THREE.Float32BufferAttribute(outputAttributes[i],attributes[i].itemSize)));
  groups.forEach(g=>geometry.addGroup(g.start,g.count,g.materialIndex));
  geometry.computeBoundingBox();geometry.computeBoundingSphere();
  return geometry;
}

/** Road geometry and collision checks share the same grade and crown. */
export function createTransitionRoadGeometry(field:RoadTerrainTransition, low:number,high:number,lift=0):THREE.BufferGeometry {
  const positions:number[]=[],uv:number[]=[],indices:number[]=[];
  const columns=Math.max(1,Math.ceil((high-low)/.25)), rows=Math.ceil(field.length/.5);
  for(let i=0;i<=rows;i++)for(let j=0;j<=columns;j++) {
    const x=field.length*i/rows,y=low+(high-low)*j/columns;
    positions.push(x,y,field.roadHeight(x,y)+lift);uv.push(x,y);
    const k=i*(columns+1)+j;
    if(i<rows&&j<columns)indices.push(k,k+columns+1,k+columns+2,k,k+columns+2,k+1);
  }
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));geometry.setIndex(indices);geometry.computeVertexNormals();
  return geometry;
}
