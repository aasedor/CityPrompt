import {describe,it,expect} from 'vitest';
import type {SiteZone} from '@/types';
import {rectangleAt,placementProblem} from '@/features/pickPlace/geometry';
import {GROUND_SURFACES,groundSurfaceFor,groundSurfaceProblem,groundSurfaceProperties} from './groundSurfaces';

const coords=rectangleAt([-114,51],30,30);
const zone={id:'surface',zone_type:'development_area',coordinates:coords,properties:groundSurfaceProperties('black_pavers')} as SiteZone;
describe('student ground surface polygons',()=>{
  it('offers 25 distinct finishes and round-trips their identity without a building programme',()=>{
    expect(GROUND_SURFACES).toHaveLength(25);
    expect(new Set(GROUND_SURFACES.map(s=>s.id)).size).toBe(25);
    for(const surface of GROUND_SURFACES){
      const saved=JSON.parse(JSON.stringify({...zone,properties:groundSurfaceProperties(surface.id)}));
      expect(groundSurfaceFor(saved)?.id).toBe(surface.id);
      expect(saved.properties.development_type).toBeUndefined();
    }
    expect(groundSurfaceFor({...zone,properties:{ground_surface_material:'unknown'}})).toBeUndefined();
  });
  it('accepts a concave finish inside overlapping building and park plots, while retaining boundary limits',()=>{
    const boundary={...zone,id:'site',zone_type:'site_boundary',coordinates:rectangleAt([-114,51],100,100)} as SiteZone;
    const objects=['building','green_space'].map(zone_type=>({...zone,id:zone_type,zone_type,properties:{}} as SiteZone));
    expect(placementProblem(coords,objects,boundary,undefined,{properties:zone.properties})).toBeNull();
    expect(groundSurfaceProblem(coords,boundary)).toBeNull();
    expect(groundSurfaceProblem(boundary.coordinates,boundary)).toBeNull();
    expect(placementProblem(boundary.coordinates,objects,boundary,undefined,{properties:zone.properties})).toBeNull();
    expect(groundSurfaceProblem(rectangleAt([-114,51],150,150),boundary)).toContain('boundary');
    expect(groundSurfaceProblem([coords[0],coords[2],coords[1],coords[3]],boundary)).not.toBeNull();
  });
});
