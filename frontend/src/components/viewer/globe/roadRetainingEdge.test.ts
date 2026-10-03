import {describe,it,expect} from 'vitest';
import * as THREE from 'three';
import {createRoadTerrainTransition,fitRoadTerrainEdges} from './roadTerrainTransition';
import {createTransitionTileGeometry} from './roadTerrainTransitionMesh';
import {createRoadRetainingEdge,constrainRoadEdgeWalk} from './roadRetainingEdge';

const options=()=>({profile:Array.from({length:31},(_,i)=>({x:i*2,z:1.5})),halfWidth:3,
  shoulderWidth:.6,blendWidth:4,endBlend:4,tieLength:30,startHeight:0,endHeight:0});

describe('constrained road edges',()=>{
  it('keeps a natural slope on the unconstrained side',()=>{
    const probes=[{x:30,y:6,z:0},{x:30,y:-6,z:1.45}];
    const {field}=fitRoadTerrainEdges(options(),probes,(_,y)=>y>0?0:1.45);
    expect(field.edgeAt(1)).toBe('retaining');expect(field.edgeAt(-1)).toBe('slope');
    expect(field.groundHeight(30,4.01,.5)).toBe(.5);
    expect(field.weight(30,-4.01)).toBeGreaterThan(.9);
  });
  it('supports different available widths while preserving each outer seam',()=>{
    const f=createRoadTerrainTransition({...options(),leftBlendWidth:6,rightBlendWidth:12});
    expect(f.outerWidthAt(1)).toBe(9.6);expect(f.outerWidthAt(-1)).toBe(15.6);
    expect(f.groundHeight(30,9.6,.2)).toBe(.2);expect(f.groundHeight(30,-15.6,.7)).toBe(.7);
  });
  it('never uses an edge treatment to hide a core obstacle or missing ground',()=>{
    expect(()=>fitRoadTerrainEdges(options(),[{x:30,y:0,z:4}],()=>0)).toThrow(/tree|structure/);
    expect(()=>fitRoadTerrainEdges(options(),[{x:30,y:0,z:null}],()=>0)).toThrow(/coverage/);
  });
  it('builds closed faces, coping and a guard over the complete short blend',()=>{
    const f=createRoadTerrainTransition({...options(),leftEdge:'retaining'});
    const wall=createRoadRetainingEdge(f,1,()=>0,()=>0);
    for(const g of [wall.face,wall.cap,wall.rail]) {
      g.computeBoundingBox();expect(g.getAttribute('position').count).toBeGreaterThan(0);
      expect(Array.from(g.getAttribute('position').array).every(Number.isFinite)).toBe(true);
      expect(g.getAttribute('uv').count).toBe(g.getAttribute('position').count);
    }
    expect(wall.face.boundingBox!.min.y).toBeLessThan(f.options.halfWidth+f.options.shoulderWidth);
    expect(wall.face.boundingBox!.max.y).toBeGreaterThan(f.outerWidthAt(1));
    expect(wall.maximumHeight).toBeCloseTo(1.44,2);expect(wall.blockers.length).toBeGreaterThan(0);
    [wall.face,wall.cap,wall.rail].forEach(g=>g.dispose());
  });
  it('checks narrow objects along the physical wall even outside the deformation',()=>{
    const f=createRoadTerrainTransition({...options(),leftEdge:'retaining'});
    expect(()=>createRoadRetainingEdge(f,1,(x,y)=>x===30&&y>3.8?5:0,()=>0)).toThrow(/object/);
    expect(()=>createRoadRetainingEdge(f,1,()=>null,()=>0)).toThrow(/unverified/);
    expect(()=>createRoadRetainingEdge(f,1,()=>-3,()=>-3)).toThrow(/height/);
  });
  it('splits coarse triangles exactly at retaining boundaries, preserving the ground and UVs outside',()=>{
    const f=createRoadTerrainTransition({...options(),leftEdge:'retaining',rightEdge:'retaining'});
    const source=new THREE.PlaneGeometry(24,12);source.translate(30,0,0);
    const geometry=createTransitionTileGeometry(source,new THREE.Matrix4(),f)!;
    const mesh=new THREE.Mesh(geometry,new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));mesh.updateMatrixWorld();
    const ray=new THREE.Raycaster();
    for(const x of [18.1,24.2,30.13,40.9])for(const side of [-1,1]) {
      ray.set(new THREE.Vector3(x,side*(f.outerWidthAt(side)+.0001),10),new THREE.Vector3(0,0,-1));
      expect(ray.intersectObject(mesh)[0].point.z).toBeCloseTo(0,6);
      const y=side*(f.options.halfWidth+f.options.shoulderWidth-.1);
      ray.set(new THREE.Vector3(x,y,10),new THREE.Vector3(0,0,-1));
      expect(Math.abs(ray.intersectObject(mesh)[0].point.z-f.groundHeight(x,y,0))).toBeLessThan(.003);
    }
    const p=geometry.getAttribute('position'),uv=geometry.getAttribute('uv');
    for(let i=0;i<p.count;i++) {
      expect(uv.getX(i)).toBeCloseTo((p.getX(i)-18)/24,5);
      expect(uv.getY(i)).toBeCloseTo((p.getY(i)+6)/12,5);
    }
    geometry.dispose();source.dispose();mesh.material.dispose();
  });
  it('blocks tunnelling in both directions and permits sliding, retreat and walking around ends',()=>{
    const walls=[{minX:0,maxX:10,minY:3.3,maxY:4.3}];
    expect(constrainRoadEdgeWalk({x:5,y:2},{x:5,y:5},walls)).toEqual({x:5,y:2});
    expect(constrainRoadEdgeWalk({x:5,y:5},{x:5,y:2},walls)).toEqual({x:5,y:5});
    expect(constrainRoadEdgeWalk({x:5,y:3.2},{x:6,y:3.5},walls)).toEqual({x:6,y:3.2});
    expect(constrainRoadEdgeWalk({x:5,y:3.2},{x:5,y:2},walls)).toEqual({x:5,y:2});
    expect(constrainRoadEdgeWalk({x:11,y:2},{x:11,y:5},walls)).toEqual({x:11,y:5});
    expect(constrainRoadEdgeWalk({x:5,y:3.6},{x:5,y:3.1},walls)).toEqual({x:5,y:3.1});
  });
});
