import * as THREE from 'three';
import { stationNormals, streetStationElevationAt, type LocalPt, type StreetStationTerrain } from './streetMesh3D';

/** Close the cut/fill sides of a prepared road using the same measured stations
 * as its pavement. No guessed deep skirt, extra terrain probes or ground edits. */
export function createPreparedStreetEdges(points: LocalPt[], pavement: StreetStationTerrain[],
  measured: StreetStationTerrain[], lowOffset: number, highOffset: number): THREE.BufferGeometry | null {
  if (points.length < 2 || pavement.length !== points.length || measured.length !== points.length
    || [...pavement, ...measured].some(p => ![p.centerZ,p.leftZ,p.rightZ,p.halfWidthM].every(Number.isFinite))) return null;
  const normals = stationNormals(points);
  const at = (i: number, offset: number) => ({
    x: points[i].x + normals[i].x * offset, y: points[i].y + normals[i].y * offset,
    road: streetStationElevationAt(pavement,i,offset), ground: streetStationElevationAt(measured,i,offset),
  });
  // Include the centre at the two ends to preserve their measured cross slope.
  const ring = [...points.map((_,i)=>at(i,lowOffset)), at(points.length-1,0),
    ...points.map((_,i)=>at(points.length-1-i,highOffset)), at(0,0)];
  const positions: number[] = [];
  const face = (a: ReturnType<typeof at>, b: ReturnType<typeof at>) => {
    if (Math.max(Math.abs(a.road-a.ground),Math.abs(b.road-b.ground)) < .03) return;
    const vertices = [[a.x,a.y,Math.min(a.road,a.ground)-.08], [b.x,b.y,Math.min(b.road,b.ground)-.08],
      [b.x,b.y,Math.max(b.road,b.ground)], [a.x,a.y,Math.max(a.road,a.ground)]];
    for (const index of [0,1,2,0,2,3]) positions.push(...vertices[index]);
  };
  ring.forEach((a,i) => {
    const b=ring[(i+1)%ring.length], da=a.road-a.ground, db=b.road-b.ground;
    if (da*db < 0) {
      const t=da/(da-db),cross={x:a.x+t*(b.x-a.x),y:a.y+t*(b.y-a.y),
        road:a.road+t*(b.road-a.road),ground:a.ground+t*(b.ground-a.ground)};
      face(a,cross);face(cross,b);
    } else face(a,b);
  });
  if (!positions.length) return null;
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  geometry.computeVertexNormals();geometry.computeBoundingSphere();
  return geometry;
}
