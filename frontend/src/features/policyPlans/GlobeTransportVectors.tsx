import { useContext, useEffect, useLayoutEffect, useMemo, useRef } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { TilesRendererContext } from '3d-tiles-renderer/r3f';
import * as THREE from 'three';
import { LineSegments2 } from 'three/examples/jsm/lines/LineSegments2.js';
import { retainResourceForDeferredDisposal } from '@/components/viewer/globe/strictModeResourceDisposal';
import { useSharedSiteGround } from '@/components/viewer/globe/SharedSiteGroundProvider';
import { buildGroundedTransport, sampleGeographicSurface, type GroundNode } from './groundedTransport';
import type { TransportSnapshot } from './transportVectors';

export function disposeTransportObjects(objects: Array<LineSegments2 | THREE.Mesh>) {
  objects.forEach(object => {
    object.geometry.dispose();
    (object.material as THREE.Material).dispose();
    if (object instanceof THREE.InstancedMesh) THREE.InstancedMesh.prototype.dispose.call(object);
  });
}
/** Geographic ground contact, sampled incrementally, never projected from the camera. */
export function GlobeTransportVectors({ data, mapId, opacity, order, color }: {
  data: TransportSnapshot; mapId: string; opacity: number; order: number; color?: string;
}) {
  const size = useThree(state => state.size), invalidate = useThree(state => state.invalidate);
  const tiles = useContext(TilesRendererContext), ground = useSharedSiteGround();
  const resources = useMemo(() => buildGroundedTransport(data, mapId, order), [data, mapId, order]);
  const run = useRef({ index: 0, epoch: 0, changed: 0, lastCamera: new THREE.Matrix4(), nextScan: 0, queue: [] as GroundNode[], rescan: true });
  const scratch = useMemo(() => ({ frustum: new THREE.Frustum(), matrix: new THREE.Matrix4(), sphere: new THREE.Sphere(), ray: new THREE.Raycaster() }), []);
  useEffect(() => retainResourceForDeferredDisposal(resources, value => value.dispose()), [resources]);
  useEffect(() => {
    run.current.index = 0; run.current.queue = []; run.current.rescan = true; run.current.epoch++;
    const changed = () => { run.current.changed = performance.now(); invalidate(); };
    tiles?.addEventListener('tiles-load-end', changed);
    tiles?.addEventListener('tile-visibility-change', changed);
    return () => { tiles?.removeEventListener('tiles-load-end', changed); tiles?.removeEventListener('tile-visibility-change', changed); };
  }, [resources, tiles, ground.revision, invalidate]);
  useLayoutEffect(() => {
    for (const object of resources.objects) {
      (object.material as THREE.Material).opacity = opacity;
      if (color) (object.material as THREE.MeshBasicMaterial).color.set(color);
      if (object instanceof LineSegments2) object.material.resolution.set(size.width, size.height);
    }
  }, [resources, opacity, color, size.width, size.height]);
  useFrame(({ camera }) => {
    const state = run.current, now = performance.now();
    if (state.changed && now - state.changed > 700) {
      state.changed = 0; state.epoch++; state.rescan = true;
    }
    // Camera motion only changes which geographic nodes need work. It never
    // supplies a height or moves an already measured geographic anchor.
    scratch.frustum.setFromProjectionMatrix(scratch.matrix.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse));
    if ((state.index >= state.queue.length && state.rescan) || (now >= state.nextScan && !state.lastCamera.equals(camera.matrixWorld))) {
      // Nearby visible chunks first. A full-city snapshot must not make the
      // student's foreground wait behind distant features near the horizon.
      state.queue = resources.chunks.filter(chunk => {
        scratch.sphere.center.copy(chunk.center); scratch.sphere.radius = 650;
        return scratch.frustum.intersectsSphere(scratch.sphere);
      }).map(chunk => ({ chunk, distance: chunk.center.distanceToSquared(camera.position) }))
        .sort((a, b) => a.distance - b.distance).flatMap(({ chunk }) => chunk.nodes);
      state.index = 0; state.rescan = false; state.nextScan = now + 400; state.lastCamera.copy(camera.matrixWorld);
    }
    if (state.index >= state.queue.length) { if (state.changed) invalidate(); return; }
    let probes = 0, scanned = 0;
    // Keep the TilesGroup root so its spatially optimized raycast can prune
    // unrelated city tiles instead of traversing every loaded mesh per vertex.
    const roots = tiles?.group ? [tiles.group] : [];
    // Bounded CPU budget even for full-city imports. Misses remain hidden until
    // tiles arrive; prior good samples are retained through LOD transitions.
    const batchStart = performance.now();
    while (state.index < state.queue.length && probes < 8 && scanned++ < 3000 && performance.now() - batchStart < 3) {
      const node = state.queue[state.index++];
      if (node.epoch === state.epoch) continue;
      scratch.sphere.center.copy(node.position).add(resources.origin); scratch.sphere.radius = node.height === null ? 500 : 25;
      if (!scratch.frustum.intersectsSphere(scratch.sphere)) continue;
      probes++; node.epoch = state.epoch;
      resources.setHeight(node, ground.heightAt(node.lng, node.lat) ?? sampleGeographicSurface(node.lng, node.lat, roots, scratch.ray));
    }
    resources.dirty.clear();
    if (state.index < state.queue.length || state.changed || state.rescan) invalidate();
  });
  return <group position={resources.origin} name={`transport-vector:${mapId}`}>
    {resources.objects.map((object, i) => <primitive key={i} object={object} dispose={null} />)}
  </group>;
}
