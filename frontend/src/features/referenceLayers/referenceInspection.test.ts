import {expect, it} from 'vitest';
import * as THREE from 'three';
import type {ReferenceLayer} from './api';
import {pickReferenceFeature, resolveReferenceSelection} from './referenceInspection';

it('resolves the clicked batched heritage marker and drops hidden or removed records', () => {
  const layer = {id:'public-data:heritage',created_at:'snapshot-1',opacity:1,feature_collection:{features:[{properties:{name:'Historic school'}}]}} as unknown as ReferenceLayer;
  const root = new THREE.Group(), marker = new THREE.Mesh(); root.add(marker);
  marker.userData = {cityPolicyId:'reference:public-data:heritage',transportIds:['0:point:0'],policyRaycast:(_ray:unknown,hits:unknown[])=>hits.push({object:marker,instanceId:0,distance:2})};
  const selection = pickReferenceFeature(root,new THREE.Raycaster(),[layer]);
  expect(resolveReferenceSelection(selection,[layer])?.feature.properties.name).toBe('Historic school');
  marker.visible = false;
  expect(pickReferenceFeature(root,new THREE.Raycaster(),[layer])).toBeNull();
  expect(resolveReferenceSelection(selection,[])).toBeNull();
  expect(resolveReferenceSelection(selection,[{...layer,opacity:0}])).toBeNull();
  expect(resolveReferenceSelection(selection,[{...layer,created_at:'snapshot-2'}])).toBeNull();
});
