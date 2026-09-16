import { useEffect, useMemo, useRef, useState } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import { Matrix4, PerspectiveCamera, Scene, type Group, type WebGLRenderer } from 'three';
import type { SparkRenderer, SplatMesh } from '@sparkjsdev/spark';
import { readFixedSplat } from './fixedSplatAsset';
import { copyCameraToLocalFrame } from './localContextCamera';
import { applySplatSpatialMask } from './splatSpatialMask';
import { createTileSpatialMaskSetConfig } from '@/components/viewer/globe/TileSpatialMaskPlugin';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import type { SiteZone } from '@/types';

// This bounded, development-only pilot retains one renderer per Canvas. Spark
// 0.1 has no renderer-wide dispose API; never create another on every switch.
// R3F destroys the WebGL context when the Canvas is destroyed. Production needs
// the current renderer API after a separately verified Three.js upgrade.
type ContextEngine = { renderer: SparkRenderer; scene: Scene; worldToLocal: Matrix4; camera: PerspectiveCamera };
const renderers = new WeakMap<WebGLRenderer, ContextEngine>();

export function GaussianContextLayer({ enabled, onReady, onFailure, zones }: {
  enabled: boolean; onReady: () => void; onFailure: () => void; zones: SiteZone[];
}) {
  const { gl, scene, invalidate } = useThree();
  const group = useRef<Group>(null);
  const mesh = useRef<SplatMesh | null>(null);
  const spark = useRef<SparkRenderer | null>(null);
  const requested = useRef(enabled);
  requested.current = enabled;
  const reported = useRef(false);
  const callbacks = useRef({ onReady, onFailure });
  callbacks.current = { onReady, onFailure };
  const started = useRef(false);
  const [activated, setActivated] = useState(false);
  const loadingTimer = useRef<number>();
  const mask = useMemo(() => {
    const boundary = getActiveSiteBoundary(zones);
    return boundary ? createTileSpatialMaskSetConfig([boundary], 1102) : null;
  }, [zones]);
  const maskRef = useRef(mask);
  maskRef.current = mask;

  useEffect(() => {
    if (!spark.current || !group.current) return;
    if (!mask) { callbacks.current.onFailure(); return; }
    group.current.updateWorldMatrix(true, false);
    applySplatSpatialMask(spark.current.material, mask, group.current.matrixWorld);
  }, [mask]);

  useEffect(() => {
    if (enabled) setActivated(true);
    reported.current = false;
    if (spark.current) spark.current.visible = enabled;
    if (mesh.current) mesh.current.visible = enabled;
    invalidate();
  }, [enabled, invalidate]);

  useEffect(() => {
    if (!activated || started.current) return;
    if (!maskRef.current) { callbacks.current.onFailure(); setActivated(false); return; }
    started.current = true;
    const controller = new AbortController();
    let owned: SplatMesh | null = null;
    const timer = window.setTimeout(() => { controller.abort(); callbacks.current.onFailure(); setActivated(false); }, 30000);
    loadingTimer.current = timer;
    void Promise.all([import('@sparkjsdev/spark'), readFixedSplat(controller.signal)]).then(async ([module, bytes]) => {
      if (controller.signal.aborted) return;
      let engine = renderers.get(gl);
      if (!engine) {
        const renderer = new module.SparkRenderer({ renderer: gl });
        renderer.name = 'gaussian-context-renderer';
        renderer.userData = { sceneRole: 'existing', contextProvider: 'gaussian-splat' };
        const local = { renderer, scene: new Scene(), worldToLocal: new Matrix4(), camera: new PerspectiveCamera() };
        const beforeRender = renderer.onBeforeRender.bind(renderer);
        renderer.onBeforeRender = (webgl, _scene, camera) => {
          // Decode/generate in local coordinates. Adding ECEF and subtracting it
          // again in a float shader creates visible half-metre quantization.
          copyCameraToLocalFrame(camera as PerspectiveCamera, local.camera, local.worldToLocal);
          local.scene.updateMatrixWorld(true);
          beforeRender(webgl, local.scene, local.camera);
        };
        engine = local;
        renderers.set(gl, engine);
      }
      const { renderer } = engine;
      spark.current = renderer;
      group.current?.updateWorldMatrix(true, false);
      if (group.current) engine.worldToLocal.copy(group.current.matrixWorld).invert();
      if (!maskRef.current) throw new Error('Missing proposal replacement area');
      applySplatSpatialMask(renderer.material, maskRef.current, engine.worldToLocal.clone().invert());
      scene.add(renderer);
      owned = new module.SplatMesh({ fileBytes: bytes, fileType: module.SplatFileType.PCSOGSZIP });
      owned.name = 'knock-community-hall-context';
      owned.userData = { sceneRole: 'existing', contextProvider: 'gaussian-splat', registration: 'local-engineering-test' };
      owned.position.set(35, 30, 0); owned.rotation.x = -Math.PI / 2; owned.scale.setScalar(4);
      await owned.initialized;
      if (controller.signal.aborted) { owned.dispose(); owned = null; return; }
      mesh.current = owned;
      engine.scene.add(owned);
      renderer.visible = owned.visible = requested.current;
      invalidate();
    }).catch(error => {
      window.clearTimeout(timer);
      if (!controller.signal.aborted) {
        console.warn('[context] Gaussian sample failed', error instanceof Error ? error.message : 'load failure');
        callbacks.current.onFailure();
        setActivated(false);
      }
    });
    return () => {
      controller.abort(); window.clearTimeout(timer); started.current = false;
      if (owned?.isInitialized) { owned.removeFromParent(); owned.dispose(); owned = null; }
      mesh.current = null;
      if (spark.current) { spark.current.visible = false; spark.current.removeFromParent(); }
    };
  }, [activated, gl, scene, invalidate]);

  useFrame(() => {
    if (enabled && mesh.current?.isInitialized && !reported.current
      && (spark.current?.defaultView.display?.geometry.instanceCount ?? 0) > 0) {
      reported.current = true; callbacks.current.onReady();
      window.clearTimeout(loadingTimer.current);
    }
  });

  // Explicit artificial placement. Source download has no surveyed CRS/datum or
  // metric control. This never feeds placement, terrain sampling or capture.
  return <EastNorthUpFrame lat={51.0169 * Math.PI / 180} lon={-114.1249 * Math.PI / 180} height={1102}>
    <group ref={group} />
  </EastNorthUpFrame>;
}
