import * as THREE from 'three';
import type {ReferenceFeature, ReferenceLayer} from './api';

export type ReferenceSelection = {layerId: string; featureIndex: number; revision: string};
export function resolveReferenceSelection(selection: ReferenceSelection | null, layers: ReferenceLayer[]): {layer: ReferenceLayer; feature: ReferenceFeature} | null {
  const layer = layers.find(item => item.id === selection?.layerId && item.opacity > 0);
  if (!layer || (layer.content_hash ?? layer.created_at) !== selection?.revision) return null;
  const feature = selection && layer?.feature_collection.features[selection.featureIndex];
  return layer && feature ? {layer, feature} : null;
}

/** Transport batches retain stable feature indices. Their explicit raycast is
 * used because overlays intentionally opt out of ordinary R3F selection. */
export function pickReferenceFeature(root: THREE.Group | null, ray: THREE.Raycaster, layers: ReferenceLayer[]): ReferenceSelection | null {
  if (!root) return null;
  const hits: THREE.Intersection[] = [];
  root.updateWorldMatrix(true, true);
  ray.params.Line2 = {threshold: 8};
  root.traverse(object => {
    const mapId = object.userData.cityPolicyId;
    if (typeof mapId !== 'string' || !mapId.startsWith('reference:')) return;
    for (let parent: THREE.Object3D | null = object; parent; parent = parent.parent) if (!parent.visible) return;
    if (typeof object.userData.policyRaycast === 'function') object.userData.policyRaycast(ray, hits);
  });
  hits.sort((a,b) => b.object.renderOrder-a.object.renderOrder || a.distance-b.distance);
  for (const hit of hits) {
    const id = hit.object.userData.transportIds?.[hit.instanceId ?? hit.faceIndex ?? -1];
    if (typeof id !== 'string' || !/^\d+:(point|line):\d+$/.test(id)) continue;
    const layerId = String(hit.object.userData.cityPolicyId).slice('reference:'.length);
    const layer = layers.find(item => item.id === layerId);
    if (!layer) continue;
    const selection = {layerId, featureIndex: Number(id.split(':')[0]), revision: layer.content_hash ?? layer.created_at};
    if (resolveReferenceSelection(selection, layers)) return selection;
  }
  return null;
}
