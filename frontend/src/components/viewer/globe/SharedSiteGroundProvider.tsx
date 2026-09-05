import { createContext, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { useFrame } from '@react-three/fiber';
import { TilesRendererContext } from '3d-tiles-renderer/r3f';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { createGroundSelection } from './sharedGroundSelection';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { createSharedSiteGroundLayout, createSharedSiteGroundSnapshot, sampleSharedSiteGround,
  sharedSiteGroundContains, sharedSiteGroundGridPoint, sharedSiteGroundSourceSignature, validateSharedSiteGroundPass,
  type SharedSiteGroundLayout, type SharedSiteGroundPassQuality, type SharedSiteGroundSnapshot } from './sharedSiteGround';

export interface SharedSiteGroundState {
  status: 'inactive' | 'sampling' | 'ready' | 'unavailable';
  snapshot: SharedSiteGroundSnapshot | null;
  heightAt: (lng: number, lat: number) => number | null;
  contains: (lng: number, lat: number) => boolean;
  revision: string;
}
export const INACTIVE_SHARED_SITE_GROUND: SharedSiteGroundState = Object.freeze({
  status: 'inactive', snapshot: null, heightAt: () => null, contains: () => false, revision: 'inactive',
});
const Context = createContext<SharedSiteGroundState>(INACTIVE_SHARED_SITE_GROUND);
export function useSharedSiteGround(): SharedSiteGroundState { return useContext(Context); }

const SETTLE_MS = 900, PASS_GAP_MS = 150, MAX_PASSES = 4, TIMEOUT_MS = 45000, MAX_SAMPLES_PER_FRAME = 8;

interface SharedGroundDiagnostics {
  source: string; generation: number; status: SharedSiteGroundState['status'];
  layout: SharedSiteGroundLayout | null; passes: number; index: number; missCount: number;
  elapsedMs: number; settledForMs: number; deadlineAt: number; deadlineReason: string | null;
  passQuality: SharedSiteGroundPassQuality | null; maxPassDeltaM: number | null;
  latestCompletedRawValues: Array<number | null> | null;
  visibleTileCount: number; visibleSceneCount: number; sampledFrames: number; lastBatchMs: number;
  lastInvalidation: { type: string; at: number } | null;
}
declare global { interface Window { __sharedGroundDiagnostics?: SharedGroundDiagnostics } }

function visibleTileHit(object: THREE.Object3D, tileGroup: THREE.Object3D, visibleScenes: ReadonlySet<THREE.Object3D>): boolean {
  let cursor: THREE.Object3D | null = object, belongsToVisibleTile = false;
  while (cursor) {
    if (!cursor.visible) return false;
    if (visibleScenes.has(cursor)) belongsToVisibleTile = true;
    if (cursor === tileGroup) return belongsToVisibleTile;
    cursor = cursor.parent;
  }
  return false;
}

/** Samples only the tile group, never proposed buildings/parks. Relevant LOD changes
 * invalidate the surface; a capture must wait for the next ready revision.
 * Full coverage and repeatability establish visible-mesh contact, not surveyed
 * bare earth. No unknown or outlier sample is synthesized. */
export function SharedSiteGroundProvider({ zones, children, onChange }: {
  zones: SiteZone[]; children: ReactNode; onChange?: (state: SharedSiteGroundState) => void;
}) {
  const tiles = useContext(TilesRendererContext);
  const active = getActiveSiteBoundary(zones);
  const boundary = active?.properties?.community_3d_mask_existing_tiles === false ? active : null;
  const sourceSignature = boundary ? sharedSiteGroundSourceSignature(boundary) : 'inactive';
  const layout = useMemo(() => boundary ? createSharedSiteGroundLayout(boundary) : null,
    // Properties unrelated to the site's revision/geometry do not restart sampling.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [sourceSignature]);
  const [result, setResult] = useState<{ source: string; status: SharedSiteGroundState['status']; snapshot: SharedSiteGroundSnapshot | null; generation: number }>(
    { source: 'inactive', status: 'inactive', snapshot: null, generation: 0 });
  const onChangeRef = useRef(onChange); onChangeRef.current = onChange;
  const raycaster = useRef(new THREE.Raycaster());
  const origin = useRef(new THREE.Vector3()), normal = useRef(new THREE.Vector3());
  const run = useRef({ source: '', dirty: true, generation: 0, changedAt: 0, startedAt: 0, index: 0, passes: 0,
    previous: null as Array<number | null> | null, values: [] as Array<number | null>, nextPassAt: 0, done: false,
    visibleScenes: new Set<THREE.Object3D>() });
  const diagnostics = useRef<SharedGroundDiagnostics | null>(null);
  const selection = useMemo(() => layout ? createGroundSelection(layout,
    Number(boundary?.properties?.terrain_elevation_m ?? 1500)) : null,
    // A row metadata write does not move this fixed site-coverage camera.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [layout]);
  const diagnose = (patch: Partial<SharedGroundDiagnostics>) => {
    if (!import.meta.env.DEV || typeof window === 'undefined') return;
    diagnostics.current ??= { source: '', generation: 0, status: 'inactive', layout: null, passes: 0, index: 0, missCount: 0,
      elapsedMs: 0, settledForMs: 0, deadlineAt: 0, deadlineReason: null, passQuality: null, maxPassDeltaM: null,
      latestCompletedRawValues: null, visibleTileCount: 0, visibleSceneCount: 0, sampledFrames: 0, lastBatchMs: 0,
      lastInvalidation: null };
    Object.assign(diagnostics.current, patch);
    window.__sharedGroundDiagnostics = diagnostics.current;
  };
  useEffect(() => () => {
    if (import.meta.env.DEV && typeof window !== 'undefined' && window.__sharedGroundDiagnostics === diagnostics.current)
      delete window.__sharedGroundDiagnostics;
  }, []);

  useEffect(() => {
    const invalidate = (event?: { type?: string; scene?: THREE.Object3D }) => {
      // Previously even a download behind the camera cleared every assembly.
      // Keep the last measured surface when the changed model cannot cover it.
      if (event?.scene && selection && !selection.intersects(event.scene)) return;
      run.current.dirty = true; run.current.changedAt = Date.now();
      diagnose({ lastInvalidation: { type: event?.type ?? 'source_or_renderer', at: Date.now() } });
    };
    invalidate();
    if (!tiles) return;
    if (selection) {
      tiles.setCamera(selection.camera);
      tiles.setResolution(selection.camera, ...selection.resolution);
    }
    tiles.addEventListener('load-model', invalidate);
    tiles.addEventListener('dispose-model', invalidate);
    tiles.addEventListener('tile-visibility-change', invalidate);
    return () => {
      tiles.removeEventListener('load-model', invalidate);
      tiles.removeEventListener('dispose-model', invalidate);
      tiles.removeEventListener('tile-visibility-change', invalidate);
      if (selection) tiles.deleteCamera(selection.camera);
    };
  }, [tiles, sourceSignature, selection]);

  useFrame(() => {
    const current = run.current, now = Date.now();
    if (current.source !== sourceSignature || current.dirty) {
      current.source = sourceSignature; current.dirty = false; current.generation += 1;
      current.changedAt = now; current.startedAt = now; current.index = 0; current.passes = 0;
      current.previous = null; current.values = []; current.done = false; current.nextPassAt = 0;
      diagnose({ source: sourceSignature, generation: current.generation, layout, status: !boundary ? 'inactive' : layout && tiles ? 'sampling' : 'unavailable',
        passes: 0, index: 0, missCount: 0, elapsedMs: 0, settledForMs: 0, deadlineAt: now + TIMEOUT_MS,
        deadlineReason: boundary && (!layout || !tiles) ? !layout ? 'invalid_layout' : 'missing_renderer' : null,
        passQuality: null, maxPassDeltaM: null, latestCompletedRawValues: null, sampledFrames: 0, lastBatchMs: 0 });
      setResult({ source: sourceSignature, status: !boundary ? 'inactive' : layout && tiles ? 'sampling' : 'unavailable', snapshot: null, generation: current.generation });
    }
    diagnose({ elapsedMs: now - current.startedAt, settledForMs: now - current.changedAt,
      visibleTileCount: tiles?.visibleTiles.size ?? 0, visibleSceneCount: current.visibleScenes.size });
    if (!boundary || !layout || !tiles || current.done) return;
    const unavailable = (reason: string) => {
      current.done = true;
      diagnose({ status: 'unavailable', deadlineReason: reason });
      setResult({ source: sourceSignature, status: 'unavailable', snapshot: null, generation: current.generation });
    };
    if (now - current.startedAt > TIMEOUT_MS) { unavailable('sampling_deadline'); return; }
    // Match capture readiness: a nonempty visible tile set must be unchanged
    // for 900 ms. Off-camera download progress must not stall visible ground.
    if (now - current.changedAt < SETTLE_MS || now < current.nextPassAt || !tiles.visibleTiles.size) return;
    const count = layout.grid.columns * layout.grid.rows;
    if (current.index === 0) {
      current.visibleScenes.clear();
      tiles.forEachLoadedModel((scene, tile) => {
        if (tiles.visibleTiles.has(tile) && (!selection || selection.intersects(scene))) current.visibleScenes.add(scene);
      });
    }
    const batchStarted = performance.now();
    for (let processed = 0; current.index < count && processed < MAX_SAMPLES_PER_FRAME; processed += 1) {
      const [lng, lat] = sharedSiteGroundGridPoint(layout, current.index);
      WGS84_ELLIPSOID.getCartographicToPosition(lat * Math.PI / 180, lng * Math.PI / 180, 50000, origin.current);
      WGS84_ELLIPSOID.getCartographicToNormal(lat * Math.PI / 180, lng * Math.PI / 180, normal.current);
      raycaster.current.set(origin.current, normal.current.negate()); raycaster.current.far = 100000;
      const validHit = (candidate: THREE.Intersection) => visibleTileHit(candidate.object, tiles.group, current.visibleScenes);
      let hit = raycaster.current.intersectObject(tiles.group, true).find(validHit);
      if (!hit) {
        // The optimized TilesGroup traversal can cull a ray along a tile's
        // bounding-volume seam. Measure the actual visible meshes directly
        // before declaring that cell missing; never synthesize a height.
        hit = raycaster.current.intersectObjects([...current.visibleScenes], true).find(validHit);
      }
      current.values.push(hit ? WGS84_ELLIPSOID.getPositionElevation(hit.point) : null);
      current.index += 1;
      // A triangle-heavy tile may consume the frame budget in one raycast.
      if (performance.now() - batchStarted >= 4) break;
    }
    if (import.meta.env.DEV) diagnose({ index: current.index, missCount: current.values.filter((value) => value === null).length,
      sampledFrames: (diagnostics.current?.sampledFrames ?? 0) + 1, lastBatchMs: performance.now() - batchStarted });
    if (current.index < count) return;
    current.passes += 1;
    const quality = validateSharedSiteGroundPass(layout, current.values);
    const snapshot = current.previous ? createSharedSiteGroundSnapshot(layout, current.previous, current.values) : null;
    if (import.meta.env.DEV) diagnose({ passes: current.passes, passQuality: quality, latestCompletedRawValues: [...current.values],
      maxPassDeltaM: current.previous && quality.valid ? Math.max(...current.values.map((value, index) => Math.abs(value! - current.previous![index]!))) : null });
    if (snapshot) {
      current.done = true;
      diagnose({ status: 'ready', deadlineReason: null });
      setResult({ source: sourceSignature, status: 'ready', snapshot, generation: current.generation });
    } else if (current.passes >= MAX_PASSES) unavailable(quality.valid ? 'unstable_passes' : quality.reason ?? 'quality_rejected');
    else {
      current.previous = quality.valid ? current.values : null;
      current.values = []; current.index = 0; current.nextPassAt = now + PASS_GAP_MS;
    }
  });

  const state = useMemo<SharedSiteGroundState>(() => {
    if (!boundary) return INACTIVE_SHARED_SITE_GROUND;
    const matching = result.source === sourceSignature;
    const measured = matching && result.status === 'ready' ? result.snapshot : null;
    const snapshot = measured ? { ...measured, boundaryUpdatedAt: boundary.updated_at } : null;
    const ring = layout?.boundaryCoordinates ?? boundary.coordinates.map(([lng, lat]): [number, number] => [lng, lat]);
    return { status: matching ? result.status : layout ? 'sampling' : 'unavailable', snapshot,
      contains: (lng, lat) => sharedSiteGroundContains(ring, lng, lat),
      heightAt: (lng, lat) => sampleSharedSiteGround(snapshot, lng, lat),
      revision: `${sourceSignature}:${result.generation}:${snapshot?.signature ?? (matching ? result.status : 'sampling')}` };
    // Source identity freezes the boundary ring across unrelated parent renders.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sourceSignature, layout, result, boundary?.updated_at]);
  useEffect(() => { onChangeRef.current?.(state); }, [state]);
  return <Context.Provider value={state}>{children}</Context.Provider>;
}
