/**
 * MapEngine — Shared interface for both Mapbox and Globe rendering engines.
 *
 * All drawing, editing, and AI render code targets this interface,
 * allowing transparent switching between Mapbox GL JS and the R3F globe.
 */

export type MapMode = 'mapbox' | 'globe';

/** Unified event payload for map interactions */
export interface MapEngineEvent {
  /** Geographic coordinates at the event location */
  lngLat: [number, number];
  /** Screen pixel coordinates */
  point: { x: number; y: number };
  /** Original DOM event */
  originalEvent: MouseEvent | PointerEvent | KeyboardEvent;
  /** Prevent default behavior */
  preventDefault(): void;
}

/** Camera state snapshot */
export interface CameraState {
  center: [number, number]; // [lng, lat]
  zoom: number;
  bearing: number;  // degrees, 0=north
  pitch: number;    // degrees, 0=top-down
}

/** Options for camera movement */
export interface FlyToOptions {
  center?: [number, number];
  zoom?: number;
  bearing?: number;
  pitch?: number;
  duration?: number; // ms, 0 = instant
}

/** Map interaction event types */
export type MapEventType =
  | 'click'
  | 'dblclick'
  | 'mousedown'
  | 'mousemove'
  | 'mouseup'
  | 'contextmenu'
  | 'pitch'
  | 'moveend';

/**
 * Engine-agnostic map interface.
 * Both MapboxEngine and GlobeEngine implement this.
 */
export interface MapEngine {
  readonly mode: MapMode;

  // --- Coordinate projection ---
  /** Convert geographic [lng, lat] to screen pixels */
  project(lngLat: [number, number]): { x: number; y: number };
  /** Convert screen pixels to geographic [lng, lat] (may return null if off-globe) */
  unproject(point: { x: number; y: number }): [number, number] | null;

  // --- Camera state ---
  getCenter(): [number, number];
  getZoom(): number;
  getBearing(): number;
  getPitch(): number;
  getCameraState(): CameraState;

  // --- Camera control ---
  flyTo(options: FlyToOptions): void;
  jumpTo(options: FlyToOptions): void;
  fitBounds(sw: [number, number], ne: [number, number], options?: { padding?: number; duration?: number }): void;

  // --- Canvas access ---
  getCanvas(): HTMLCanvasElement;
  /** Capture the current view as a base64 PNG */
  captureScreenshot(): Promise<string>;

  // --- Interaction control ---
  /** Disable navigation (for drawing mode) */
  disableInteraction(): void;
  /** Re-enable navigation */
  enableInteraction(): void;

  // --- Events ---
  on(type: MapEventType, handler: (event: MapEngineEvent) => void): void;
  off(type: MapEventType, handler: (event: MapEngineEvent) => void): void;

  // --- Lifecycle ---
  destroy(): void;
}
