import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { pickZoningArea, resolveZoneInspection, type ZoningMapState } from './zoningInspection';
import { studyPreviewLayer } from '@/features/referenceLayers/zoningStudy';
import type { Position } from '@/features/referenceLayers/zoningLabels';

const ring: Position[] = [[-114,51],[-113.999,51],[-113.999,51.001],[-114,51.001],[-114,51]];
const city: ZoningMapState = { enabled: true, fill: true, fillOpacity: .5, data: { bounds: [-114,51,-113.999,51.001], loadedAt: '', districts: [
  { id: 'city', label: 'M-C1 d75', code: 'M-C1', anchor: ring[0], polygon: [ring] },
] } };
const study = studyPreviewLayer([{ id: 'student', label: 'Homes', origin: 'student', color: '#abcdef', rings: [ring], district: { designation: 'R-G' } }], ring, 'proposed', .5);
const selection = { id: 'student', layerId: study.id, label: '', source: '' };

describe('zoning selection', () => {
  it('resolves the district, not an arbitrary map caption, and refreshes after rezoning', () => {
    expect(resolveZoneInspection(selection, city, [study])?.district?.designation).toBe('R-G');
    const edited = structuredClone(study);
    edited.feature_collection.features[0].properties.district = { designation: 'MU-1 h23' };
    expect(resolveZoneInspection(selection, city, [edited])?.district?.designation).toBe('MU-1 h23');
  });
  it('clears deleted, hidden, transparent or disabled selections', () => {
    expect(resolveZoneInspection(selection, city, [])).toBeNull();
    expect(resolveZoneInspection(selection, city, [{ ...study, opacity: 0 }])).toBeNull();
    const selected = { id: 'city', label: '', source: '' };
    expect(resolveZoneInspection(selected, city, [])?.district?.designation).toBe('M-C1 d75');
    for (const patch of [{ enabled: false }, { fill: false }, { fillOpacity: 0 }, { data: undefined }]) expect(resolveZoneInspection(selected, { ...city, ...patch }, [])).toBeNull();
  });
  it('picks the exact study or City polygon using existing render geometry', () => {
    const root = new THREE.Group(), cityGroup = new THREE.Group(), studyGroup = new THREE.Group();
    cityGroup.name = 'zoning-label-overlay'; studyGroup.name = `study-layer:${study.id}`;
    function mesh(id: string) {
      const geometry = new THREE.PlaneGeometry(10, 10);
      geometry.userData.zoningFaceRanges = [{ id, firstFace: 0, endFace: 2 }];
      const m = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }));
      m.name = 'calgary-land-use-fill'; m.raycast = () => {}; return m;
    }
    const cityMesh = mesh('city'), studyMesh = mesh('student');
    cityGroup.add(cityMesh); studyGroup.add(studyMesh); root.add(cityGroup, studyGroup);
    const ray = new THREE.Raycaster(new THREE.Vector3(1,1,20), new THREE.Vector3(0,0,-1));
    expect(pickZoningArea(root, ray, city, [study])?.id).toBe('student');
    expect(pickZoningArea(root, ray, city, [{ ...study, opacity: 0 }])?.id).toBe('city');
    studyGroup.visible = false;
    expect(pickZoningArea(root, ray, city, [study])?.id).toBe('city');
    expect(pickZoningArea(root, ray, { ...city, enabled: false }, [])).toBeNull();
    expect(ray.intersectObject(root, true)).toHaveLength(0);
    for (const m of [cityMesh, studyMesh]) { m.geometry.dispose(); m.material.dispose(); }
  });
});
