import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import type { SiteZone } from '@/types';
import { rectangleAt } from '@/features/pickPlace/geometry';
import { preparedWalkSurface } from './preparedWalkSurface';
const boundary = {id:'site',project_id:'test',color:'#aaa',sort_order:0,created_at:'now',updated_at:'now',zone_type:'site_boundary',is_active_boundary:true, coordinates:rectangleAt([0,0],100,100), properties:{terrain_elevation_m:1044.64,community_3d_mask_existing_tiles:true}} as SiteZone;
const point = (height: number) => WGS84_ELLIPSOID.getCartographicToPosition(0,0,height,new THREE.Vector3());
const ray = new THREE.Raycaster(point(1100),new THREE.Vector3(-1,0,0));
const surface = (height:number) => {
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(20,20),new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));
  mesh.rotation.y=Math.PI/2;mesh.position.copy(point(height));mesh.updateMatrixWorld(true);return mesh;
};
describe('prepared Walk picking',()=>{
  it('picks prepared ground instead of higher hidden Google tiles',()=>{
    const scene=new THREE.Scene(),tiles=new THREE.Group();tiles.add(surface(1047.78));scene.add(tiles);
    const hit=preparedWalkSurface(ray,[boundary],scene,tiles,1047.78)!;
    expect(hit.height).toBeCloseTo(1044.64,2);expect(hit.lngLat[0]).toBeCloseTo(0,5);
  });
  it('preserves a foreground off-site tile roof on a ray reaching prepared land',()=>{
    const scene=new THREE.Scene(),tiles=new THREE.Group(),roof=surface(1080);
    roof.position.y=-60;roof.updateMatrixWorld(true);tiles.add(roof);scene.add(tiles);
    const oblique=new THREE.Raycaster(point(1100).add(new THREE.Vector3(0,-80,0)),new THREE.Vector3(-1,1,0).normalize());
    expect(preparedWalkSurface(oblique,[boundary],scene,tiles,1047.78)!.height).toBeGreaterThan(1079);
  });
  it('preserves authored roofs for above-ground rejection',()=>{
    const scene=new THREE.Scene();scene.add(surface(1052));
    expect(preparedWalkSurface(ray,[boundary],scene,undefined,1047.78)!.height).toBeGreaterThan(1044.64+3);
  });
  it('ignores hidden authored objects',()=>{
    const scene=new THREE.Scene(),group=new THREE.Group();group.visible=false;group.add(surface(1052));scene.add(group);
    expect(preparedWalkSurface(ray,[boundary],scene,undefined,1047.78)!.height).toBeCloseTo(1044.64,2);
  });
  it('leaves off-site and landscape picks to existing terrain/roof guard',()=>{
    const outside={...boundary,coordinates:rectangleAt([.01,0],100,100)};
    expect(preparedWalkSurface(ray,[outside],null,undefined,1047.78)).toBeNull();
    expect(preparedWalkSurface(ray,[{...boundary,properties:{...boundary.properties,terrain_strategy:'landscape'}}],null,undefined,1047.78)).toBeNull();
  });
});
