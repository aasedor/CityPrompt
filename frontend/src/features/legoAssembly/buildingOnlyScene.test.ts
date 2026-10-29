import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { prepareBuildingOnlyScene } from './buildingOnlyScene';

const revision = 'clay-calgary-cbe-brutalist-hq-clay-v004';
function boxes(name: string, specs: number[][]) {
  const geometries = specs.map(([x,y,z,w,h,d]) => new THREE.BoxGeometry(w,h,d).toNonIndexed().translate(x,y,z));
  const geometry = new THREE.BufferGeometry();
  for (const key of ['position','normal','uv']) {
    const values = geometries.flatMap(g => Array.from(g.getAttribute(key).array));
    geometry.setAttribute(key, new THREE.Float32BufferAttribute(values,key === 'uv' ? 2 : 3));
  }
  const mesh = new THREE.Mesh(geometry,new THREE.MeshStandardMaterial()); mesh.name=name;
  return mesh;
}
function fixture() {
  const source = new THREE.Group();
  // The exporter merges main and neighbour glazing under the first module tag.
  const glass=boxes('CLAY_GLASS',[[0,12,0,35,20,33],[-30,5,0,8,10,12]]);
  glass.userData.cityprompt_lego_module='neighbours';
  const concrete=boxes('CLAY_CONCRETE',[[0,.225,0,40.2,.45,37.5],[0,.1,21,12,.2,1],
    [0,.01,0,85,.02,90],[35,.04,0,4,.08,70]]);
  const roof=boxes('CLAY_ROOF',[[0,27,0,39,.5,36]]);
  source.add(glass,concrete,roof,boxes('CLAY_ASPHALT',[[0,.01,35,80,.02,7]]),
    boxes('CLAY_PLANTING',[[3,4,4,2,6,2]]));
  return {source,glass,concrete,roof};
}
function bounds(source:THREE.Object3D) { return new THREE.Box3().setFromObject(source,true); }

describe('exact building-only runtime scene',()=>{
  it('separates a source-owned slab even when its vertices touch scene paving',()=>{
    const source=new THREE.Group();
    // Source ordinal ownership: four scene boxes first; the building base last.
    const foundation=boxes('CLAY_FOUNDATION',[[0,.075,14,22,.15,6],[0,.075,-14,22,.15,6],
      [14,.075,0,6,.15,34],[-14,.075,0,6,.15,34],[0,.075,0,22,.15,22]]);
    source.add(foundation);
    const result=prepareBuildingOnlyScene(source,'clay-arched-mill-mixed-use-clay-v005');
    const kept=result.clone.children[0] as THREE.Mesh;
    expect(result.applied).toBe(true);
    expect(kept.geometry.getIndex()!.count).toBe(36);
    expect(bounds(kept).min.x).toBeCloseTo(-11);
    expect(bounds(kept).max.z).toBeCloseTo(11);
  });
  it('removes source roads, site plates, landscape and neighbours, retaining main glazing and attached support',()=>{
    const {source,glass,concrete,roof}=fixture();
    const result=prepareBuildingOnlyScene(source,revision);
    expect(result.applied).toBe(true);
    expect(result.clone.getObjectByName('CLAY_ASPHALT')).toBeUndefined();
    expect(result.clone.getObjectByName('CLAY_PLANTING')).toBeUndefined();
    const keptGlass=result.clone.getObjectByName('CLAY_GLASS') as THREE.Mesh;
    expect(bounds(keptGlass).min.x).toBeCloseTo(-17.5);
    expect(bounds(keptGlass).max.x).toBeCloseTo(17.5);
    expect(keptGlass.geometry.getAttribute('position').count).toBe(36);
    const keptConcrete=result.clone.getObjectByName('CLAY_CONCRETE') as THREE.Mesh;
    expect(bounds(keptConcrete).max.z).toBeCloseTo(21.5);
    expect(bounds(keptConcrete).min.y).toBeCloseTo(0);
    expect(bounds(result.clone).max.y).toBeCloseTo(27.25);
    expect((result.clone.getObjectByName('CLAY_ROOF') as THREE.Mesh).geometry).toBe(roof.geometry);
    expect(glass.geometry.getAttribute('position').count).toBe(72);
    expect(concrete.geometry.getAttribute('position').count).toBe(144);
    expect(result.ownedGeometries).toHaveLength(2);
    expect(source.children).toHaveLength(5);
  });
  it('uses native coordinates including mesh transforms and preserves normals and UVs',()=>{
    const source=new THREE.Group(), mesh=boxes('CLAY_GLASS',[[0,0,0,2,2,2],[60,0,0,2,2,2]]);
    mesh.position.y=8; source.add(mesh);
    const result=prepareBuildingOnlyScene(source,'/api/v1/files/library/rlasm-architectural-clay/'+revision+'.glb');
    const kept=result.clone.children[0] as THREE.Mesh;
    expect(bounds(kept).min.y).toBeCloseTo(7);
    expect(bounds(kept).max.x).toBeCloseTo(1);
    expect(kept.geometry.getAttribute('uv').count).toBe(kept.geometry.getAttribute('normal').count);
    expect(kept.geometry.getIndex()!.count).toBe(36);
  });
  it('leaves uploads, unknown revisions and unregistered model URLs unchanged',()=>{
    const {source}=fixture();
    for(const identity of [undefined,'uploaded-building.glb',revision.replace('v004','v005'),
      '/api/v1/files/imported/'+revision+'.glb']) {
      const result=prepareBuildingOnlyScene(source,identity);
      expect(result.applied).toBe(false);
      expect(result.clone.children).toHaveLength(source.children.length);
      expect(result.ownedGeometries).toHaveLength(0);
      expect(bounds(result.clone)).toEqual(bounds(source));
    }
  });
});
