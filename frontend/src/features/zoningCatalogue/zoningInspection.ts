import * as THREE from 'three';
import type { ReferenceLayer } from '@/features/referenceLayers/api';
import type { ZoningLabelsState } from '@/features/referenceLayers/useZoningLabels';
import { studyMetadata, studyZones, studyZoneName } from '@/features/referenceLayers/zoningStudy';
import { pickPolicyMesh } from '@/features/policyPlans/policyPicking';
import { zoningColor } from '@/features/referenceLayers/zoningAppearance';
import type { ZoneInspection } from './types';

export type ZoningMapState = Pick<ZoningLabelsState, 'data' | 'enabled' | 'fill' | 'fillOpacity'>;
export interface ZoningInspectionControls {
  selected: ZoneInspection | null;
  select: (zone: ZoneInspection | null) => void;
}

/** Resolve by stable ID on every render so edits, deletion and hidden layers
 * cannot leave an old designation's recommendations on screen. */
export function resolveZoneInspection(selection: ZoneInspection | null, existing: ZoningMapState, layers: ReferenceLayer[]): ZoneInspection | null {
  if (!selection) return null;
  if (selection.layerId) {
    const layer = layers.find(candidate => candidate.id === selection.layerId && candidate.opacity > 0);
    const zone = layer && studyZones(layer).find(candidate => candidate.id === selection.id);
    if (!zone || !layer || !studyMetadata(layer)) return null;
    return { id: zone.id, layerId: layer.id, label: studyZoneName(zone), source: layer.name,
      district: zone.district, custom: zone.custom, color: zone.color };
  }
  if (!existing.enabled || !existing.fill || existing.fillOpacity <= 0) return null;
  const zone = existing.data?.districts.find(candidate => candidate.id === selection.id);
  return zone ? { id: zone.id, label: zone.label, source: 'Existing City zoning', color: zoningColor(zone),
    district: { designation: zone.label, code: zone.code, description: zone.description } } : null;
}

export function pickZoningArea(root: THREE.Group | null, raycaster: THREE.Raycaster, existing: ZoningMapState | undefined, layers: ReferenceLayer[]): ZoneInspection | null {
  if (!root) return null;
  // Student-authored zones take precedence when two zoning layers overlap.
  for (const layer of [...layers].reverse()) {
    if (!studyMetadata(layer) || layer.opacity <= 0) continue;
    const mesh = root.getObjectByName(`study-layer:${layer.id}`)?.getObjectByName('calgary-land-use-fill');
    const id = mesh instanceof THREE.Mesh ? pickPolicyMesh(mesh, raycaster) : null;
    if (id) return resolveZoneInspection({ id, layerId: layer.id, label: '', source: '' }, existing ?? { data: undefined, enabled: false, fill: false, fillOpacity: 0 }, layers);
  }
  if (existing?.enabled && existing.fill && existing.fillOpacity > 0) {
    const mesh = root.children.find(child => child.name === 'zoning-label-overlay')?.getObjectByName('calgary-land-use-fill');
    const id = mesh instanceof THREE.Mesh ? pickPolicyMesh(mesh, raycaster) : null;
    if (id) return resolveZoneInspection({ id, label: '', source: '' }, existing, layers);
  }
  return null;
}
