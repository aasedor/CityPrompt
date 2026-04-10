/**
 * Google3DTilesLayer.ts
 *
 * Mapbox CustomLayerInterface that renders Google Photorealistic 3D Tiles
 * inside Mapbox's WebGL context using Three.js and 3d-tiles-renderer.
 *
 * Usage:
 *   const layer = new Google3DTilesLayer(apiKey, [lng, lat]);
 *   map.addLayer(layer);
 */

import * as THREE from 'three';
import { TilesRenderer } from '3d-tiles-renderer';
import { GoogleCloudAuthPlugin } from '3d-tiles-renderer/plugins';
import { buildECEFToMercatorMatrix } from './ecefToMercator';
import type { Map as MapboxMap } from 'mapbox-gl';

const DEG_TO_RAD = Math.PI / 180;

// How far the map center can move before we recompute the ECEF matrix
const MATRIX_REFRESH_THRESHOLD_KM = 10;

export class Google3DTilesLayer {
  readonly id = 'google-3d-tiles';
  readonly type = 'custom' as const;
  readonly renderingMode = '3d' as const;

  private renderer: THREE.WebGLRenderer | null = null;
  private scene: THREE.Scene | null = null;
  private camera: THREE.Camera | null = null;
  private tiles: TilesRenderer | null = null;
  private ecefToMercator: THREE.Matrix4;
  private map: MapboxMap | null = null;

  // Reference point for the ECEF matrix
  private refLng: number;
  private refLat: number;

  // Attribution callback
  public onAttributionsChange: ((text: string) => void) | null = null;
  private lastAttributionText = '';
  private _frameCount = 0;

  constructor(
    private apiKey: string,
    center: [number, number], // [lng, lat]
  ) {
    this.refLng = center[0];
    this.refLat = center[1];
    this.ecefToMercator = buildECEFToMercatorMatrix(this.refLng, this.refLat);
    console.log('[Google3DTiles] constructor — center:', center);
  }

  onAdd(map: MapboxMap, gl: WebGL2RenderingContext) {
    console.log('[Google3DTiles] onAdd called');
    this.map = map;

    // Create Three.js renderer sharing Mapbox's GL context
    this.renderer = new THREE.WebGLRenderer({
      canvas: map.getCanvas(),
      context: gl,
      antialias: true,
    });
    this.renderer.autoClear = false;
    console.log('[Google3DTiles] WebGLRenderer created');

    // Scene
    this.scene = new THREE.Scene();

    // Raw Camera — we set projectionMatrix directly from Mapbox's matrix
    this.camera = new THREE.Camera();

    // Create TilesRenderer with Google auth plugin
    this.tiles = new TilesRenderer();
    console.log('[Google3DTiles] TilesRenderer created');

    this.tiles.registerPlugin(
      new GoogleCloudAuthPlugin({
        apiToken: this.apiKey,
        useRecommendedSettings: true,
      }),
    );
    console.log('[Google3DTiles] GoogleCloudAuthPlugin registered');

    // Quota management
    this.tiles.maxDepth = 25;

    // Apply ECEF-to-Mercator transform to the tiles group
    this.tiles.group.matrixAutoUpdate = false;
    this.tiles.group.matrix.copy(this.ecefToMercator);
    this.tiles.group.matrixWorldNeedsUpdate = true;

    // Add tiles to scene
    this.tiles.setCamera(this.camera);
    this.scene.add(this.tiles.group);

    // Log events from tile renderer
    this.tiles.addEventListener('load-error', (event: any) => {
      console.error('[Google3DTiles] load-error:', event.url, event.error?.message);
    });
    this.tiles.addEventListener('load-root-tileset', () => {
      console.log('[Google3DTiles] Root tileset loaded!');
      console.log('[Google3DTiles] root tile:', this.tiles?.root);
      console.log('[Google3DTiles] group position:', this.tiles?.group.position);
      console.log('[Google3DTiles] group children after root:', this.tiles?.group.children.length);
      // Reset frame count so we get fresh render logs after root loads
      this._frameCount = 0;
    });
    this.tiles.addEventListener('load-content', () => {
      console.log('[Google3DTiles] Content loaded! group children:', this.tiles?.group.children.length);
    });
    this.tiles.addEventListener('load-model', (event: any) => {
      console.log('[Google3DTiles] Model loaded:', event.url?.substring(0, 80));
    });

    // Listen for map movements to refresh ECEF matrix if needed
    map.on('moveend', this.handleMoveEnd);
    // Debug: log the transform matrix
    const me = this.ecefToMercator.elements;
    console.log('[Google3DTiles] ECEF→Mercator matrix translation:', me[12], me[13], me[14]);
    console.log('[Google3DTiles] ECEF→Mercator matrix scale approx:',
      Math.sqrt(me[0]*me[0] + me[1]*me[1] + me[2]*me[2]),
      Math.sqrt(me[4]*me[4] + me[5]*me[5] + me[6]*me[6]),
      Math.sqrt(me[8]*me[8] + me[9]*me[9] + me[10]*me[10]),
    );
    console.log('[Google3DTiles] onAdd complete');
  }

  render(_gl: WebGL2RenderingContext, matrix: number[]) {
    if (!this.renderer || !this.scene || !this.camera || !this.tiles || !this.map) return;

    // Set camera projection matrix directly from Mapbox
    // The ECEF transform is on tiles.group.matrix, not the camera
    this.camera.projectionMatrix.fromArray(matrix);
    this.camera.projectionMatrixInverse.copy(this.camera.projectionMatrix).invert();

    // Update tile LOD resolution
    const canvas = this.map.getCanvas();
    this.tiles.setResolution(this.camera, canvas.clientWidth, canvas.clientHeight);

    // Process tile loading queue
    this.tiles.update();

    // Debug: log first 10 frames
    this._frameCount++;
    if (this._frameCount <= 10) {
      const visibleCount = this.tiles.visibleTiles?.size ?? 0;
      const activeCount = this.tiles.activeTiles?.size ?? 0;
      console.log(`[Google3DTiles] render frame ${this._frameCount}`, {
        groupChildren: this.tiles.group.children.length,
        visibleTiles: visibleCount,
        activeTiles: activeCount,
        root: !!this.tiles.root,
        loadProgress: this.tiles.loadProgress,
      });
    }

    // Render — must resetState before/after to preserve Mapbox's GL state
    this.renderer.resetState();
    this.renderer.render(this.scene, this.camera);
    this.renderer.resetState();

    // Update attributions
    this.updateAttributions();

    // Keep render loop alive while tiles are loading
    this.map.triggerRepaint();
  }

  onRemove() {
    console.log('[Google3DTiles] onRemove');
    if (this.map) {
      this.map.off('moveend', this.handleMoveEnd);
    }
    if (this.tiles) {
      this.tiles.dispose();
      this.tiles = null;
    }
    if (this.renderer) {
      this.renderer.dispose();
      this.renderer = null;
    }
    this.scene = null;
    this.camera = null;
    this.map = null;
  }

  // --- Private ---

  private handleMoveEnd = () => {
    if (!this.map) return;
    const center = this.map.getCenter();
    const distKm = this.haversineKm(this.refLat, this.refLng, center.lat, center.lng);
    if (distKm > MATRIX_REFRESH_THRESHOLD_KM) {
      this.refLng = center.lng;
      this.refLat = center.lat;
      this.ecefToMercator = buildECEFToMercatorMatrix(this.refLng, this.refLat);
      if (this.tiles) {
        this.tiles.group.matrix.copy(this.ecefToMercator);
        this.tiles.group.matrixWorldNeedsUpdate = true;
      }
      console.log('[Google3DTiles] ECEF matrix refreshed for new center:', center.lng, center.lat);
    }
  };

  private updateAttributions() {
    if (!this.tiles || !this.onAttributionsChange) return;
    try {
      const attributions = this.tiles.getAttributions();
      if (attributions) {
        const text = Array.isArray(attributions)
          ? attributions.map((a: any) => (typeof a === 'string' ? a : a?.value || '')).filter(Boolean).join(' | ')
          : String(attributions);
        if (text !== this.lastAttributionText) {
          this.lastAttributionText = text;
          this.onAttributionsChange(text);
        }
      }
    } catch {
      // Attribution API may vary by version — fail silently
    }
  }

  private haversineKm(lat1: number, lng1: number, lat2: number, lng2: number): number {
    const R = 6371;
    const dLat = (lat2 - lat1) * DEG_TO_RAD;
    const dLng = (lng2 - lng1) * DEG_TO_RAD;
    const a =
      Math.sin(dLat / 2) ** 2 +
      Math.cos(lat1 * DEG_TO_RAD) * Math.cos(lat2 * DEG_TO_RAD) * Math.sin(dLng / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }
}
