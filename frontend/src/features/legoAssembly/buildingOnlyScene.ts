import * as THREE from 'three';
import contractData from './buildingOnlyContracts.json';

type Prism = readonly [number, number, number, number, number, number];
export type NativeSceneOwnershipContract = {
  regions: readonly Prism[]; landscape: readonly string[];
  meshRegions?: Record<string, readonly Prism[]>;
  triangleRanges?: Record<string, readonly (readonly [number,number])[]>;
  triangleRegions?: Record<string, readonly Prism[]>;
};
type Contract = NativeSceneOwnershipContract;

/** Source-pinned CBE v004: family_cbe.py main()/site(), not an inferred crop.
 * The exporter joins objects by material: its 'neighbours' GLASS also contains
 * the main facade. Preserve complete connected source components, never remove
 * a material or trust the first component's surviving module label. X/Z are
 * native glTF metres. The second prism owns only the podium and four steps. */
const CONTRACTS = contractData as unknown as Record<string,Contract>;
const boxesFor=(prisms:readonly Prism[])=>prisms.map(p=>new THREE.Box3(
  new THREE.Vector3(p[0],p[1],p[2]),new THREE.Vector3(p[3],p[4],p[5])));

function contractFor(identity?: string) {
  if (!identity) return undefined;
  if (CONTRACTS[identity]) return CONTRACTS[identity];
  // Only the catalogue's exact immutable library path opts in. Uploads with a
  // coincidentally identical filename retain all their original geometry.
  const path = identity.split('?')[0].replace(/^https?:\/\/[^/]+/, '');
  const match = /^\/api\/v1\/files\/library\/rlasm-architectural-clay\/([^/]+)\.glb$/.exec(path);
  return match ? CONTRACTS[match[1]] : undefined;
}

interface Component { offsets: number[]; localBounds: THREE.Box3 }
const componentsByGeometry = new WeakMap<THREE.BufferGeometry, Component[]>();

/** Weld position seams only for ownership analysis, preserving normal/UV seams
 * in the actual output. Cached source buffers are immutable and never disposed. */
function components(geometry: THREE.BufferGeometry): Component[] {
  const cached = componentsByGeometry.get(geometry);
  if (cached) return cached;
  const position=geometry.getAttribute('position'), index=geometry.getIndex();
  const count=index?.count ?? position.count, triangleCount=count/3;
  const parents=Uint32Array.from({length:triangleCount},(_,i)=>i);
  const root=(value:number):number=>{
    while(parents[value]!==value) { parents[value]=parents[parents[value]]; value=parents[value]; }
    return value;
  };
  const weld=new Map<string,number>();
  for(let offset=0;offset<count;offset++) {
    const vertex=index ? index.getX(offset) : offset;
    const key=[position.getX(vertex),position.getY(vertex),position.getZ(vertex)]
      .map(value=>Math.round(value*1e5)).join(',');
    const triangle=Math.floor(offset/3), previous=weld.get(key);
    if(previous===undefined) weld.set(key,triangle);
    else parents[root(triangle)]=root(previous);
  }
  const groups=new Map<number,Component>(), point=new THREE.Vector3();
  for(let offset=0;offset<count;offset+=3) {
    const id=root(offset/3);
    let group=groups.get(id);
    if(!group) { group={offsets:[],localBounds:new THREE.Box3()}; groups.set(id,group); }
    for(let k=0;k<3;k++) {
      group.offsets.push(offset+k);
      point.fromBufferAttribute(position,index ? index.getX(offset+k) : offset+k);
      group.localBounds.expandByPoint(point);
    }
  }
  const result=[...groups.values()]; componentsByGeometry.set(geometry,result); return result;
}

/** Compact attributes as well as indices: Three's bounds otherwise still see
 * removed context vertices, shifting centring, foundation and capture framing. */
function subsetGeometry(source:THREE.BufferGeometry, offsets:number[]):THREE.BufferGeometry {
  const result=new THREE.BufferGeometry(), sourceIndex=source.getIndex();
  const remap=new Map<number,number>(), vertices:number[]=[], indices:number[]=[];
  for(const offset of offsets) {
    const original=sourceIndex ? sourceIndex.getX(offset) : offset;
    let mapped=remap.get(original);
    if(mapped===undefined) { mapped=vertices.length; remap.set(original,mapped); vertices.push(original); }
    indices.push(mapped);
  }
  for(const [name,attribute] of Object.entries(source.attributes)) {
    const array=new (attribute.array.constructor as typeof Float32Array)(vertices.length*attribute.itemSize);
    for(const [to,from] of vertices.entries()) for(let axis=0;axis<attribute.itemSize;axis++) {
      array[to*attribute.itemSize+axis]=(attribute as THREE.InterleavedBufferAttribute).isInterleavedBufferAttribute
        ? (attribute as THREE.InterleavedBufferAttribute).data.array[from*(attribute as THREE.InterleavedBufferAttribute).data.stride
          +(attribute as THREE.InterleavedBufferAttribute).offset+axis]
        : attribute.array[from*attribute.itemSize+axis];
    }
    result.setAttribute(name,new THREE.BufferAttribute(array,attribute.itemSize,attribute.normalized));
  }
  result.setIndex(indices);
  if(source.groups.length) for(let i=0;i<offsets.length;i+=3) {
    const material=source.groups.find(group=>offsets[i]>=group.start && offsets[i]<group.start+group.count)?.materialIndex ?? 0;
    const previous=result.groups[result.groups.length-1];
    if(previous?.materialIndex===material) previous.count+=3;
    else result.addGroup(i,3,material);
  }
  result.computeBoundingBox(); result.computeBoundingSphere(); return result;
}

export function prepareBuildingOnlyScene(source: THREE.Object3D, identity?: string): {
  clone: THREE.Object3D; ownedGeometries: THREE.BufferGeometry[]; applied: boolean;
} {
  return prepareOwnedNativeScene(source, contractFor(identity));
}

/** Retain complete source components or explicitly owned original faces. The
 * caller must bind this contract to an immutable catalogue identity. */
export function prepareOwnedNativeScene(source: THREE.Object3D, contract?: NativeSceneOwnershipContract): {
  clone: THREE.Object3D; ownedGeometries: THREE.BufferGeometry[]; applied: boolean;
} {
  const clone=source.clone(true), ownedGeometries:THREE.BufferGeometry[]=[];
  if(!contract) return {clone,ownedGeometries,applied:false};
  const regions=boxesFor(contract.regions);
  clone.updateMatrixWorld(true);
  const remove:THREE.Object3D[]=[];
  clone.traverse(object=>{
    const mesh=object as THREE.Mesh;
    if(!mesh.isMesh) return;
    if(contract.landscape.includes(mesh.name)) { remove.push(mesh); return; }
    const geometry=mesh.geometry, count=geometry.getIndex()?.count ?? geometry.getAttribute('position').count;
    const ranges=contract.triangleRanges?.[mesh.name];
    const meshRegions=contract.meshRegions?.[mesh.name];
    let keep:number[];
    if(ranges) {
      // Explicit original-face ownership separates coincident slabs without
      // cutting triangles or admitting neighbouring coplanar boundary faces.
      const position=geometry.getAttribute('position'), index=geometry.getIndex();
      const guards=contract.triangleRegions?.[mesh.name];
      const guardBoxes=guards ? boxesFor(guards) : undefined;
      keep=[];
      for(const [start,end] of ranges) {
        if(start<0 || end*3>count || end<start) throw new Error('Building-only source triangle contract mismatch');
        for(let triangle=start;triangle<end;triangle++) {
          if(guardBoxes) {
            const triangleBounds=new THREE.Box3();
            for(let k=0;k<3;k++) triangleBounds.expandByPoint(new THREE.Vector3()
              .fromBufferAttribute(position,index ? index.getX(triangle*3+k) : triangle*3+k).applyMatrix4(mesh.matrixWorld));
            if(!guardBoxes.some(box=>box.containsBox(triangleBounds))) throw new Error('Building-only source ownership changed');
          }
          keep.push(triangle*3,triangle*3+1,triangle*3+2);
        }
      }
    } else {
      const selectors=meshRegions ? boxesFor(meshRegions) : regions;
      keep=components(geometry).filter(component=>selectors.some(region=>
        region.containsBox(component.localBounds.clone().applyMatrix4(mesh.matrixWorld))))
        .flatMap(component=>component.offsets).sort((a,b)=>a-b);
    }
    if(!keep.length) remove.push(mesh);
    else if(keep.length!==count) {
      mesh.geometry=subsetGeometry(geometry,keep); ownedGeometries.push(mesh.geometry);
    }
  });
  remove.forEach(object=>object.removeFromParent());
  clone.updateMatrixWorld(true);
  clone.userData.buildingOnlyPolicy='cityprompt.building-only@2026-10-29-v1';
  return {clone,ownedGeometries,applied:true};
}
