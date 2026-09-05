import * as THREE from 'three';
import { inheritTileSpatialMask } from './TileSpatialMaskPlugin';
import type { ParkAccessSnapshot } from './parkAccessConnections';
import type { SharedSiteGroundSnapshot } from './sharedSiteGround';

export const DIRECT_3D_CAPTURE_SCHEMA = 'siteforge.direct-3d-capture/v2' as const;
export const DIRECT_3D_PROPOSAL_ROLE_KEY = 'siteforgeDirect3DProposalRole';
export const DIRECT_3D_INSTANCE_KEY = 'siteforgeDirect3DInstance';
export const DIRECT_3D_CAPTURE_EXCLUDE_KEY = 'siteforgeExcludeFromDirect3DCapture';
export const DIRECT_3D_CAPTURE_CONTEXT_KEY = 'siteforgeDirect3DContextOnly';

export const DIRECT_3D_PROPOSAL_ROLES = [
  'ground',
  'landscape',
  'street',
  'park',
  'building',
] as const;

export type Direct3DProposalRole = (typeof DIRECT_3D_PROPOSAL_ROLES)[number];

export interface Direct3DJunctionTopology {
  version: 1;
  arm_count: 3 | 4;
  longitude: number;
  latitude: number;
  source_fingerprint: string;
}

export interface Direct3DInstanceDescriptor {
  instance_id: string;
  semantic_class: Direct3DProposalRole;
  zone_id?: string;
  building_id?: string;
  source_zone_ids?: string[];
  junction_topology?: Direct3DJunctionTopology;
}

export interface Direct3DMaterialDescriptor {
  material_id: string;
  label: string;
  semantic_class: Direct3DProposalRole;
  material_family_id?: string;
  source_specific: boolean;
}

export interface Direct3DCameraManifest {
  projection: 'perspective' | 'orthographic' | 'other';
  projection_matrix: number[];
  matrix_world: number[];
  position: [number, number, number];
  quaternion: [number, number, number, number];
  near?: number;
  far?: number;
  fov?: number;
  aspect?: number;
  zoom?: number;
}

/**
 * Deliberately high-separation colors for a semantic ID pass. The image sent
 * to the renderer is an opaque, quantized PNG: black is context and each other
 * color has exactly one meaning. These colors are metadata, never appearance
 * guidance for the image model.
 */
export const DIRECT_3D_CLASS_COLORS: Readonly<Record<Direct3DProposalRole, string>> = {
  ground: '#f4e04d',
  landscape: '#30c875',
  street: '#ef6a3a',
  park: '#35a7ff',
  building: '#b452ff',
};

export const DIRECT_3D_CLASS_ID_MANIFEST: Readonly<Record<string, Direct3DProposalRole>> =
  Object.freeze(Object.fromEntries(
    DIRECT_3D_PROPOSAL_ROLES.map((role) => [DIRECT_3D_CLASS_COLORS[role].toUpperCase(), role]),
  ) as Record<string, Direct3DProposalRole>);

export interface Direct3DCaptureBundle {
  schema: typeof DIRECT_3D_CAPTURE_SCHEMA;
  /** Client-derived routes captured with this scene, bound to saved sources on submission. */
  parkAccessSnapshot?: ParkAccessSnapshot;
  /** Measured tile terrain used by the captured proposal; never an API datum. */
  sharedGroundSnapshot?: SharedSiteGroundSnapshot;
  beautyImageBase64: string;
  proposalMaskBase64: string;
  classIdImageBase64: string;
  classIdManifest: Readonly<Record<string, Direct3DProposalRole>>;
  instanceIdImageBase64: string;
  instanceIdManifest: Readonly<Record<string, Direct3DInstanceDescriptor>>;
  /** Same-camera depth-tested visibility; manifest membership alone includes hidden objects. */
  instancePixelCounts?: Readonly<Record<string, number>>;
  /** Optional renderer-space geometry controls used by video enhancement. */
  depthImageBase64?: string;
  normalImageBase64?: string;
  materialIdImageBase64?: string;
  materialIdManifest?: Readonly<Record<string, Direct3DMaterialDescriptor>>;
  camera: Direct3DCameraManifest;
  width: number;
  height: number;
  proposalPixelCount: number;
  contextPixelCount: number;
  maskCoverage: number;
  classCoverage: Partial<Record<Direct3DProposalRole, number>>;
  fingerprint: string;
}

export interface Direct3DCaptureQAPreview {
  width: number;
  height: number;
  maskCoverage: number;
  classCoverage: Partial<Record<Direct3DProposalRole, number>>;
  thumbnails: {
    beauty: string;
    mask: string;
    classId: string;
    instanceId: string;
  };
}

async function downscaleCapturePreview(
  source: string,
  maxLongEdge: number,
): Promise<string> {
  const response = await fetch(source);
  const blob = await response.blob();
  const bitmap = await createImageBitmap(blob);
  const scale = Math.min(1, maxLongEdge / Math.max(bitmap.width, bitmap.height));
  const canvas = document.createElement('canvas');
  canvas.width = Math.max(1, Math.round(bitmap.width * scale));
  canvas.height = Math.max(1, Math.round(bitmap.height * scale));
  try {
    const context = canvas.getContext('2d', { alpha: true });
    if (!context) {
      throw new Direct3DCaptureError(
        'capture_failed',
        'Could not create the small Direct 3D QA preview.',
      );
    }
    context.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/png');
  } finally {
    bitmap.close();
    canvas.width = 0;
    canvas.height = 0;
  }
}

/** Retain only small decoded QA images; never mount three full-size capture
 * passes beside the already memory-heavy Google Tiles renderer. */
export async function createDirect3DCaptureQAPreview(
  capture: Direct3DCaptureBundle,
  maxLongEdge = 320,
): Promise<Direct3DCaptureQAPreview> {
  const beauty = await downscaleCapturePreview(capture.beautyImageBase64, maxLongEdge);
  const mask = await downscaleCapturePreview(capture.proposalMaskBase64, maxLongEdge);
  const classId = await downscaleCapturePreview(capture.classIdImageBase64, maxLongEdge);
  const instanceId = await downscaleCapturePreview(capture.instanceIdImageBase64, maxLongEdge);
  return {
    width: capture.width,
    height: capture.height,
    maskCoverage: capture.maskCoverage,
    classCoverage: { ...capture.classCoverage },
    thumbnails: { beauty, mask, classId, instanceId },
  };
}

export type Direct3DCaptureErrorCode =
  | 'busy'
  | 'context_lost'
  | 'invalid_viewport'
  | 'invalid_beauty'
  | 'no_proposal_content'
  | 'invalid_mask_coverage'
  | 'capture_failed';

export class Direct3DCaptureError extends Error {
  readonly code: Direct3DCaptureErrorCode;

  constructor(code: Direct3DCaptureErrorCode, message: string, cause?: unknown) {
    super(message);
    this.name = 'Direct3DCaptureError';
    this.code = code;
    if (cause !== undefined) {
      (this as Error & { cause?: unknown }).cause = cause;
    }
  }
}

export interface Direct3DCaptureOptions {
  maxLongEdge?: number;
  minMaskCoverage?: number;
  maxMaskCoverage?: number;
  includeGeometryPasses?: boolean;
  /** Globe captures require actual drawn context, not a sky-only coarse tile. */
  minVisibleContextCoverage?: number;
}

interface CaptureAnalysis {
  classIdPixels: Uint8ClampedArray;
  maskPixels: Uint8ClampedArray;
  proposalPixelCount: number;
  contextPixelCount: number;
  maskCoverage: number;
  classCoverage: Partial<Record<Direct3DProposalRole, number>>;
}

interface RenderableSnapshot {
  object: THREE.Object3D & { material?: THREE.Material | THREE.Material[] };
  visible: boolean;
  effectivelyVisible: boolean;
  material: THREE.Material | THREE.Material[] | undefined;
  role: Direct3DProposalRole | null;
  instance: Direct3DInstanceDescriptor | null;
  excluded: boolean;
}

export interface Direct3DInstanceColorAssignment {
  color: string;
  descriptor: Direct3DInstanceDescriptor;
}

export interface Direct3DMaterialColorAssignment {
  color: string;
  descriptor: Direct3DMaterialDescriptor;
  material: THREE.Material;
}

interface InstanceCaptureAnalysis {
  instanceIdPixels: Uint8ClampedArray;
  pixelCounts: Readonly<Record<string, number>>;
}

interface RendererSnapshot {
  renderTarget: THREE.WebGLRenderTarget | null;
  viewport: THREE.Vector4;
  scissor: THREE.Vector4;
  scissorTest: boolean;
  clearColor: THREE.Color;
  clearAlpha: number;
  autoClear: boolean;
  background: THREE.Scene['background'];
  fog: THREE.Scene['fog'];
  overrideMaterial: THREE.Scene['overrideMaterial'];
}

const DEFAULT_MAX_LONG_EDGE = 2048;
// Keep the free client-side gate aligned with the authoritative API gate so a
// capture that passes local QA cannot be rejected only after a paid action is
// requested.
const DEFAULT_MIN_MASK_COVERAGE = 0.0025;
const DEFAULT_MAX_MASK_COVERAGE = 0.85;
const MASK_SOLID_ALPHA = 128;

export function direct3DProposalUserData(role: Direct3DProposalRole): Record<string, unknown> {
  return { [DIRECT_3D_PROPOSAL_ROLE_KEY]: role };
}

function normalizeInstanceDescriptor(
  value: Direct3DInstanceDescriptor | Record<string, unknown>,
): Direct3DInstanceDescriptor | null {
  const instanceId = typeof value.instance_id === 'string' ? value.instance_id.trim() : '';
  const semanticClass = value.semantic_class;
  if (
    !instanceId
    || typeof semanticClass !== 'string'
    || !(DIRECT_3D_PROPOSAL_ROLES as readonly string[]).includes(semanticClass)
  ) {
    return null;
  }

  const descriptor: Direct3DInstanceDescriptor = {
    instance_id: instanceId,
    semantic_class: semanticClass as Direct3DProposalRole,
  };
  if (typeof value.zone_id === 'string' && value.zone_id.trim()) {
    descriptor.zone_id = value.zone_id.trim();
  }
  if (typeof value.building_id === 'string' && value.building_id.trim()) {
    descriptor.building_id = value.building_id.trim();
  }
  if (Array.isArray(value.source_zone_ids)) {
    const sourceZoneIds = [...new Set(value.source_zone_ids
      .filter((entry): entry is string => typeof entry === 'string' && Boolean(entry.trim()))
      .map((entry) => entry.trim()))]
      .sort();
    if (sourceZoneIds.length > 0) descriptor.source_zone_ids = sourceZoneIds;
  }
  if (value.junction_topology && typeof value.junction_topology === 'object') {
    const topology = value.junction_topology as Direct3DJunctionTopology;
    if (topology.version !== 1 || ![3, 4].includes(topology.arm_count)
      || !Number.isFinite(topology.longitude) || !Number.isFinite(topology.latitude)
      || Math.abs(topology.longitude) > 180 || Math.abs(topology.latitude) > 90
      || typeof topology.source_fingerprint !== 'string' || topology.source_fingerprint.length > 1000) return null;
    descriptor.junction_topology = { version: 1, arm_count: topology.arm_count,
      longitude: topology.longitude, latitude: topology.latitude, source_fingerprint: topology.source_fingerprint };
  }
  return descriptor;
}

export function direct3DZoneInstanceDescriptor(
  zoneId: string,
  semanticClass: Direct3DProposalRole,
  details: Pick<Direct3DInstanceDescriptor, 'building_id' | 'source_zone_ids'> = {},
): Direct3DInstanceDescriptor {
  const normalizedZoneId = zoneId.trim();
  if (!normalizedZoneId) {
    throw new Direct3DCaptureError('capture_failed', 'Direct 3D instance zones require a stable id.');
  }
  return normalizeInstanceDescriptor({
    instance_id: `zone:${normalizedZoneId}:${semanticClass}`,
    semantic_class: semanticClass,
    zone_id: normalizedZoneId,
    ...details,
  }) as Direct3DInstanceDescriptor;
}

function fnv1a32(value: string): number {
  let hash = 0x811c9dc5;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193);
  }
  return hash >>> 0;
}

/** Canonical client/server junction identity. The server independently
 * verifies that these persisted street sources form a four-arm node. */
export function direct3DStreetJunctionInstanceDescriptor(
  sourceZoneIds: readonly string[],
  topology?: Direct3DJunctionTopology,
): Direct3DInstanceDescriptor {
  const normalized = [...new Set(sourceZoneIds.map((value) => value.trim()).filter(Boolean))].sort();
  if (normalized.length < 2) {
    throw new Direct3DCaptureError(
      'capture_failed',
      'Direct 3D street junctions require at least two persisted street sources.',
    );
  }
  const hash = fnv1a32(normalized.join(':')).toString(16).padStart(8, '0');
  return {
    instance_id: topology
      ? `junction:zones-${hash}:node-${fnv1a32(`${topology.longitude.toFixed(7)}:${topology.latitude.toFixed(7)}:${topology.arm_count}`).toString(16).padStart(8, '0')}:street`
      : `junction:zones-${hash}:street`,
    semantic_class: 'street',
    source_zone_ids: normalized,
    ...(topology ? { junction_topology: topology } : {}),
  };
}

export function direct3DInstanceUserData(
  descriptor: Direct3DInstanceDescriptor,
): Record<string, unknown> {
  const normalized = normalizeInstanceDescriptor(descriptor);
  if (!normalized) {
    throw new Direct3DCaptureError(
      'capture_failed',
      'Direct 3D instances require a stable id and semantic class.',
    );
  }
  return { [DIRECT_3D_INSTANCE_KEY]: normalized };
}

export function direct3DGroundRoleForCommunityKind(
  kind: 'building' | 'park' | 'street' | null | undefined,
): Direct3DProposalRole {
  if (kind === 'park' || kind === 'street') return kind;
  return 'ground';
}

export const DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA: Readonly<Record<string, boolean>> = Object.freeze({
  [DIRECT_3D_CAPTURE_EXCLUDE_KEY]: true,
});

/** Keep an object in the beauty/context pass while stopping proposal-role
 * inheritance from an ancestor. Unlike exclusion, context still renders. */
export const DIRECT_3D_CAPTURE_CONTEXT_USER_DATA: Readonly<Record<string, boolean>> = Object.freeze({
  [DIRECT_3D_CAPTURE_CONTEXT_KEY]: true,
});

export function computeDirect3DCaptureSize(
  sourceWidth: number,
  sourceHeight: number,
  maxLongEdge = DEFAULT_MAX_LONG_EDGE,
): { width: number; height: number } {
  if (
    !Number.isFinite(sourceWidth)
    || !Number.isFinite(sourceHeight)
    || !Number.isFinite(maxLongEdge)
    || sourceWidth < 1
    || sourceHeight < 1
    || maxLongEdge < 64
  ) {
    throw new Direct3DCaptureError('invalid_viewport', 'Direct 3D capture requires a valid render viewport.');
  }

  const scale = Math.min(1, maxLongEdge / Math.max(sourceWidth, sourceHeight));
  return {
    width: Math.max(1, Math.round(sourceWidth * scale)),
    height: Math.max(1, Math.round(sourceHeight * scale)),
  };
}

export function getDirect3DProposalRole(object: THREE.Object3D): Direct3DProposalRole | null {
  let current: THREE.Object3D | null = object;
  while (current) {
    if (current.userData?.[DIRECT_3D_CAPTURE_CONTEXT_KEY] === true) return null;
    const candidate = current.userData?.[DIRECT_3D_PROPOSAL_ROLE_KEY];
    if (
      typeof candidate === 'string'
      && (DIRECT_3D_PROPOSAL_ROLES as readonly string[]).includes(candidate)
    ) {
      return candidate as Direct3DProposalRole;
    }
    current = current.parent;
  }
  return null;
}

/** Resolve the nearest semantic instance tag. A context-only subtree clears
 * both role and instance inheritance so legacy models remain immutable. */
export function getDirect3DInstanceDescriptor(
  object: THREE.Object3D,
): Direct3DInstanceDescriptor | null {
  let current: THREE.Object3D | null = object;
  while (current) {
    if (current.userData?.[DIRECT_3D_CAPTURE_CONTEXT_KEY] === true) return null;
    const candidate = current.userData?.[DIRECT_3D_INSTANCE_KEY];
    if (candidate && typeof candidate === 'object' && !Array.isArray(candidate)) {
      const normalized = normalizeInstanceDescriptor(candidate as Record<string, unknown>);
      if (normalized) return normalized;
    }
    current = current.parent;
  }
  return null;
}

/** Fail closed when semantic proposal geometry is not represented by the
 * exact instance pass. Context geometry has no instance by design. */
export function requireDirect3DInstanceDescriptor(
  role: Direct3DProposalRole | null,
  instance: Direct3DInstanceDescriptor | null,
): Direct3DInstanceDescriptor | null {
  if (!role) return null;
  if (!instance) {
    throw new Direct3DCaptureError(
      'capture_failed',
      `Visible Direct 3D ${role} geometry is missing a stable instance tag.`,
    );
  }
  if (instance.semantic_class !== role) {
    throw new Direct3DCaptureError(
      'capture_failed',
      `Direct 3D instance ${instance.instance_id} does not match its semantic class.`,
    );
  }
  return instance;
}

export function isExcludedFromDirect3DCapture(object: THREE.Object3D): boolean {
  let current: THREE.Object3D | null = object;
  while (current) {
    if (current.userData?.[DIRECT_3D_CAPTURE_EXCLUDE_KEY] === true) return true;
    current = current.parent;
  }
  return false;
}

function isRenderableObject(
  object: THREE.Object3D,
): object is THREE.Object3D & { material?: THREE.Material | THREE.Material[] } {
  const typed = object as THREE.Object3D & {
    isMesh?: boolean;
    isLine?: boolean;
    isPoints?: boolean;
    isSprite?: boolean;
    material?: THREE.Material | THREE.Material[];
  };
  return Boolean(typed.isMesh || typed.isLine || typed.isPoints || typed.isSprite);
}

function isEffectivelyVisible(object: THREE.Object3D): boolean {
  let current: THREE.Object3D | null = object;
  while (current) {
    if (!current.visible) return false;
    current = current.parent;
  }
  return true;
}

export function validateDirect3DVisibleContextPixels(
  pixels: Uint8Array,
  minimumCoverage: number,
): void {
  let opaquePixels = 0;
  for (let index = 3; index < pixels.length; index += 4) {
    if (pixels[index] >= 128) opaquePixels += 1;
  }
  if (!pixels.length || opaquePixels / (pixels.length / 4) < minimumCoverage) {
    throw new Direct3DCaptureError(
      'capture_failed',
      'The surrounding map has not drawn enough visible context yet. Keep this view still, then try again. No image request was sent.',
    );
  }
}

function collectRenderableSnapshots(scene: THREE.Scene): RenderableSnapshot[] {
  const snapshots: RenderableSnapshot[] = [];
  scene.traverse((object) => {
    if (!isRenderableObject(object)) return;
    snapshots.push({
      object,
      visible: object.visible,
      effectivelyVisible: isEffectivelyVisible(object),
      material: object.material,
      role: getDirect3DProposalRole(object),
      instance: getDirect3DInstanceDescriptor(object),
      excluded: isExcludedFromDirect3DCapture(object),
    });
  });
  return snapshots;
}

function snapshotRenderer(renderer: THREE.WebGLRenderer, scene: THREE.Scene): RendererSnapshot {
  return {
    renderTarget: renderer.getRenderTarget(),
    viewport: renderer.getViewport(new THREE.Vector4()),
    scissor: renderer.getScissor(new THREE.Vector4()),
    scissorTest: renderer.getScissorTest(),
    clearColor: renderer.getClearColor(new THREE.Color()).clone(),
    clearAlpha: renderer.getClearAlpha(),
    autoClear: renderer.autoClear,
    background: scene.background,
    fog: scene.fog,
    overrideMaterial: scene.overrideMaterial,
  };
}

function restoreCaptureState(
  renderer: THREE.WebGLRenderer,
  scene: THREE.Scene,
  rendererSnapshot: RendererSnapshot,
  renderables: RenderableSnapshot[],
): void {
  for (const snapshot of renderables) {
    snapshot.object.visible = snapshot.visible;
    if (snapshot.material !== undefined) snapshot.object.material = snapshot.material;
  }
  scene.background = rendererSnapshot.background;
  scene.fog = rendererSnapshot.fog;
  scene.overrideMaterial = rendererSnapshot.overrideMaterial;
  renderer.autoClear = rendererSnapshot.autoClear;
  renderer.setClearColor(rendererSnapshot.clearColor, rendererSnapshot.clearAlpha);
  renderer.setRenderTarget(rendererSnapshot.renderTarget);
  renderer.setViewport(rendererSnapshot.viewport);
  renderer.setScissor(rendererSnapshot.scissor);
  renderer.setScissorTest(rendererSnapshot.scissorTest);
}

function assertContextAvailable(renderer: THREE.WebGLRenderer): void {
  const context = renderer.getContext();
  if (context.isContextLost()) {
    throw new Direct3DCaptureError(
      'context_lost',
      'The WebGL context was lost. Wait for the 3D scene to recover, then capture again.',
    );
  }
}

function createCaptureTarget(
  renderer: THREE.WebGLRenderer,
  width: number,
  height: number,
  pass: Direct3DRenderPass,
): THREE.WebGLRenderTarget {
  const target = new THREE.WebGLRenderTarget(width, height, {
    depthBuffer: true,
    stencilBuffer: true,
    format: THREE.RGBAFormat,
    type: THREE.UnsignedByteType,
  });
  // Packed depth and encoded normals are numeric data. Display gamma would
  // corrupt them; semantic colors and beauty retain their display encoding.
  target.texture.colorSpace = pass === 'depth' || pass === 'normal'
    ? THREE.NoColorSpace
    : renderer.outputColorSpace;
  target.texture.generateMipmaps = false;
  target.samples = getDirect3DTargetSampleCount(renderer.capabilities.isWebGL2, pass);
  return target;
}

export function getDirect3DTargetSampleCount(
  isWebGL2: boolean,
  pass: Direct3DRenderPass,
): number {
  if (!isWebGL2 || pass !== 'beauty') return 0;
  // Two samples soften the final beauty edge without the 4x multisample GPU
  // footprint that previously overlapped two 2048² capture targets.
  return 2;
}

export type Direct3DRenderPass = 'beauty' | 'class-id' | 'instance-id' | 'material-id' | 'depth' | 'normal';

function readTargetPixels(
  renderer: THREE.WebGLRenderer,
  target: THREE.WebGLRenderTarget,
  width: number,
  height: number,
): Uint8Array {
  assertContextAvailable(renderer);
  const pixels = new Uint8Array(width * height * 4);
  renderer.readRenderTargetPixels(target, 0, 0, width, height, pixels);
  assertContextAvailable(renderer);
  return pixels;
}

function flipRgbaRows(source: Uint8Array | Uint8ClampedArray, width: number, height: number): Uint8ClampedArray {
  const stride = width * 4;
  const output = new Uint8ClampedArray(source.length);
  for (let sourceY = 0; sourceY < height; sourceY += 1) {
    const targetY = height - sourceY - 1;
    output.set(source.subarray(sourceY * stride, sourceY * stride + stride), targetY * stride);
  }
  return output;
}

function rgbaToPngDataUrl(pixels: Uint8ClampedArray, width: number, height: number): string {
  if (typeof document === 'undefined') {
    throw new Direct3DCaptureError('capture_failed', 'PNG encoding requires a browser document.');
  }
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext('2d', { alpha: true });
  if (!context) {
    throw new Direct3DCaptureError('capture_failed', 'Could not create a 2D encoder for Direct 3D capture.');
  }
  const imagePixels = new Uint8ClampedArray(pixels.length);
  imagePixels.set(pixels);
  context.putImageData(new ImageData(imagePixels, width, height), 0, 0);
  const dataUrl = canvas.toDataURL('image/png');
  // Drop the temporary 2D backing store immediately; otherwise a 2048² PNG
  // encoder canvas can linger until GC and overlap the next WebGL allocation.
  canvas.width = 0;
  canvas.height = 0;
  return dataUrl;
}

function parseHexColor(hex: string): [number, number, number] {
  const value = Number.parseInt(hex.slice(1), 16);
  return [(value >> 16) & 0xff, (value >> 8) & 0xff, value & 0xff];
}

const CLASS_RGB = Object.fromEntries(
  DIRECT_3D_PROPOSAL_ROLES.map((role) => [role, parseHexColor(DIRECT_3D_CLASS_COLORS[role])]),
) as Record<Direct3DProposalRole, [number, number, number]>;

const INSTANCE_COLOR_LEVELS = Array.from({ length: 16 }, (_, index) => 24 + index * 14);
// Keep the free client gate aligned with the Pydantic request schema so a
// large scene fails before upload rather than after the paid action begins.
export const MAX_DIRECT_3D_INSTANCES = 2048;

function reverseTwelveBits(value: number): number {
  let source = value & 0xfff;
  let reversed = 0;
  for (let index = 0; index < 12; index += 1) {
    reversed = (reversed << 1) | (source & 1);
    source >>>= 1;
  }
  return reversed;
}

function instanceColorForOrdinal(ordinal: number): string {
  // Bit reversal distributes early colors across the full quantized RGB cube
  // instead of assigning visually adjacent shades to neighboring ids. The 16
  // non-black channel levels provide 4,096 exact, opaque instance colors.
  const cubeIndex = reverseTwelveBits(ordinal);
  const red = INSTANCE_COLOR_LEVELS[cubeIndex & 0xf];
  const green = INSTANCE_COLOR_LEVELS[(cubeIndex >>> 4) & 0xf];
  const blue = INSTANCE_COLOR_LEVELS[(cubeIndex >>> 8) & 0xf];
  return `#${[red, green, blue]
    .map((channel) => channel.toString(16).padStart(2, '0'))
    .join('')}`.toUpperCase();
}

function descriptorsEqual(
  left: Direct3DInstanceDescriptor,
  right: Direct3DInstanceDescriptor,
): boolean {
  return JSON.stringify(left) === JSON.stringify(right);
}

/** Build the deterministic exact-color inventory used by the instance pass.
 * Sorting makes the result independent of scene traversal order. */
export function buildDirect3DInstanceColorManifest(
  descriptors: readonly Direct3DInstanceDescriptor[],
): {
  assignments: Direct3DInstanceColorAssignment[];
  manifest: Readonly<Record<string, Direct3DInstanceDescriptor>>;
} {
  const byId = new Map<string, Direct3DInstanceDescriptor>();
  for (const value of descriptors) {
    const descriptor = normalizeInstanceDescriptor(value);
    if (!descriptor) {
      throw new Direct3DCaptureError(
        'capture_failed',
        'A Direct 3D scene instance has invalid inventory metadata.',
      );
    }
    const previous = byId.get(descriptor.instance_id);
    if (previous && !descriptorsEqual(previous, descriptor)) {
      throw new Direct3DCaptureError(
        'capture_failed',
        `Direct 3D instance ${descriptor.instance_id} has conflicting inventory metadata.`,
      );
    }
    byId.set(descriptor.instance_id, descriptor);
  }

  const sorted = [...byId.values()].sort((left, right) => (
    left.instance_id < right.instance_id ? -1 : left.instance_id > right.instance_id ? 1 : 0
  ));
  if (sorted.length > MAX_DIRECT_3D_INSTANCES) {
    throw new Direct3DCaptureError(
      'capture_failed',
      `Direct 3D capture supports at most ${MAX_DIRECT_3D_INSTANCES.toLocaleString()} visible scene instances.`,
    );
  }

  const assignments = sorted.map((descriptor, index) => ({
    color: instanceColorForOrdinal(index + 1),
    descriptor,
  }));
  const manifest = Object.freeze(Object.fromEntries(
    assignments.map(({ color, descriptor }) => [color, descriptor]),
  ) as Record<string, Direct3DInstanceDescriptor>);
  return { assignments, manifest };
}

function materialColorForRoleOrdinal(
  role: Direct3DProposalRole,
  ordinal: number,
): string {
  const roleIndex = DIRECT_3D_PROPOSAL_ROLES.indexOf(role);
  const local = Math.max(0, ordinal - 1) & 0x7ff;
  // Reserve a separate red-channel band for every semantic class. The low
  // red bits plus quantized green/blue provide 2,048 exact colors per role,
  // while keeping renderer/PNG rounding inside the owning semantic band.
  const red = 24 + roleIndex * 42 + ((local >>> 8) & 0x7) * 4;
  const green = INSTANCE_COLOR_LEVELS[(local >>> 4) & 0xf];
  const blue = INSTANCE_COLOR_LEVELS[local & 0xf];
  return `#${[red, green, blue]
    .map((channel) => channel.toString(16).padStart(2, '0'))
    .join('')}`.toUpperCase();
}

function materialStringMetadata(material: THREE.Material, key: string): string | undefined {
  const value = material.userData?.[key];
  return typeof value === 'string' && value.trim() ? value.trim() : undefined;
}

function direct3DMaterialFamilyKey(
  material: THREE.Material,
  role: Direct3DProposalRole,
): string {
  const materialFamilyId = materialStringMetadata(material, 'material_family_id')
    ?? materialStringMetadata(material, 'materialFamilyId');
  if (materialFamilyId) return `${role}:family:${materialFamilyId}`;

  const pbr = material as THREE.Material & {
    color?: THREE.Color;
    emissive?: THREE.Color;
    roughness?: number;
    metalness?: number;
    transmission?: number;
    opacity?: number;
    map?: THREE.Texture | null;
  };
  const label = (material.name || material.type || 'material').trim().toLowerCase();
  const mapLabel = (pbr.map?.name || '').trim().toLowerCase();
  return [
    role,
    label,
    material.type,
    pbr.color?.getHexString() ?? '',
    pbr.emissive?.getHexString() ?? '',
    Number.isFinite(pbr.roughness) ? pbr.roughness!.toFixed(4) : '',
    Number.isFinite(pbr.metalness) ? pbr.metalness!.toFixed(4) : '',
    Number.isFinite(pbr.transmission) ? pbr.transmission!.toFixed(4) : '',
    Number.isFinite(pbr.opacity) ? pbr.opacity!.toFixed(4) : '',
    mapLabel,
  ].join(':');
}

export function buildDirect3DMaterialColorManifest(
  snapshots: readonly RenderableSnapshot[],
): {
  assignments: Direct3DMaterialColorAssignment[];
  manifest: Readonly<Record<string, Direct3DMaterialDescriptor>>;
} {
  const materialFamilies = new Map<string, {
    materials: THREE.Material[];
    role: Direct3DProposalRole;
    materialFamilyId?: string;
    sourceSpecific: boolean;
    label: string;
  }>();
  for (const snapshot of snapshots) {
    if (!snapshot.role || !snapshot.effectivelyVisible || snapshot.excluded || !snapshot.material) continue;
    const entries = Array.isArray(snapshot.material) ? snapshot.material : [snapshot.material];
    for (const material of entries) {
      const key = direct3DMaterialFamilyKey(material, snapshot.role);
      const materialFamilyId = materialStringMetadata(material, 'material_family_id')
        ?? materialStringMetadata(material, 'materialFamilyId');
      const explicitSourceSpecific = material.userData?.source_specific === true
        || material.userData?.sourceSpecific === true
        || material.userData?.rlasm_source_specific === true;
      const current = materialFamilies.get(key);
      if (current) {
        if (!current.materials.some((entry) => entry.uuid === material.uuid)) current.materials.push(material);
        current.sourceSpecific ||= explicitSourceSpecific || Boolean(materialFamilyId);
      } else {
        materialFamilies.set(key, {
          materials: [material],
          role: snapshot.role,
          ...(materialFamilyId ? { materialFamilyId } : {}),
          sourceSpecific: explicitSourceSpecific || Boolean(materialFamilyId),
          label: (material.name || material.type || 'material').trim().slice(0, 180),
        });
      }
    }
  }
  if (materialFamilies.size > MAX_DIRECT_3D_INSTANCES) {
    throw new Direct3DCaptureError(
      'capture_failed',
      `Direct 3D capture supports at most ${MAX_DIRECT_3D_INSTANCES.toLocaleString()} visible source materials.`,
    );
  }
  const sorted = [...materialFamilies.entries()].sort(([left], [right]) => (
    left < right ? -1 : left > right ? 1 : 0
  ));
  const roleOrdinals = new Map<Direct3DProposalRole, number>();
  const assignments = sorted.flatMap(([familyKey, family], index) => {
    const ordinal = (roleOrdinals.get(family.role) ?? 0) + 1;
    roleOrdinals.set(family.role, ordinal);
    const color = materialColorForRoleOrdinal(family.role, ordinal);
    const descriptor: Direct3DMaterialDescriptor = {
      material_id: `material:${fnv1a32(familyKey).toString(16).padStart(8, '0')}`,
      label: family.label || `material-${index + 1}`,
      semantic_class: family.role,
      ...(family.materialFamilyId ? { material_family_id: family.materialFamilyId.slice(0, 180) } : {}),
      source_specific: family.sourceSpecific,
    };
    return family.materials.map((material) => ({ color, material, descriptor }));
  });
  return {
    assignments,
    manifest: Object.freeze(Object.fromEntries(
      assignments.map(({ color, descriptor }) => [color, descriptor]),
    ) as Record<string, Direct3DMaterialDescriptor>),
  };
}

export function analyzeDirect3DMaterialPixels(
  bottomUpPixels: Uint8Array | Uint8ClampedArray,
  width: number,
  height: number,
  manifest: Readonly<Record<string, Direct3DMaterialDescriptor>>,
  classIdPixels?: Uint8ClampedArray,
): Uint8ClampedArray {
  if (bottomUpPixels.length !== width * height * 4) {
    throw new Direct3DCaptureError('capture_failed', 'Direct 3D material buffer dimensions do not match.');
  }
  if (classIdPixels && classIdPixels.length !== width * height * 4) {
    throw new Direct3DCaptureError(
      'capture_failed',
      'Direct 3D class and material buffers must have matching dimensions.',
    );
  }
  const source = flipRgbaRows(bottomUpPixels, width, height);
  const output = new Uint8ClampedArray(source.length);
  const candidates = Object.entries(manifest).map(([color, descriptor]) => ({
    descriptor,
    rgb: parseHexColor(color),
  }));
  const candidatesByRole = new Map<Direct3DProposalRole, typeof candidates>();
  for (const role of DIRECT_3D_PROPOSAL_ROLES) {
    candidatesByRole.set(role, candidates.filter((candidate) => candidate.descriptor.semantic_class === role));
  }
  const roleByClassColor = new Map(DIRECT_3D_PROPOSAL_ROLES.map((role) => {
    const [red, green, blue] = CLASS_RGB[role];
    return [(red << 16) | (green << 8) | blue, role] as const;
  }));
  const nearestCache = new Map<string, typeof candidates[number] | null>();
  for (let index = 0; index < source.length; index += 4) {
    output[index + 3] = 255;
    const alpha = source[index + 3];
    if (alpha < MASK_SOLID_ALPHA || candidates.length === 0) continue;
    const alphaScale = 255 / Math.max(alpha, 1);
    const red = Math.round(Math.min(255, source[index] * alphaScale));
    const green = Math.round(Math.min(255, source[index + 1] * alphaScale));
    const blue = Math.round(Math.min(255, source[index + 2] * alphaScale));
    const cacheKey = (red << 16) | (green << 8) | blue;
    const classKey = classIdPixels
      ? (classIdPixels[index] << 16) | (classIdPixels[index + 1] << 8) | classIdPixels[index + 2]
      : null;
    const semanticRole = classKey === null ? null : roleByClassColor.get(classKey) ?? null;
    const eligibleCandidates = semanticRole ? candidatesByRole.get(semanticRole) ?? [] : candidates;
    if (eligibleCandidates.length === 0) continue;
    const scopedCacheKey = `${semanticRole ?? '*'}:${cacheKey}`;
    let nearest = nearestCache.get(scopedCacheKey);
    if (nearest === undefined) {
      nearest = null;
      let bestDistance = Number.POSITIVE_INFINITY;
      for (const candidate of eligibleCandidates) {
        const distance = (red - candidate.rgb[0]) ** 2
          + (green - candidate.rgb[1]) ** 2
          + (blue - candidate.rgb[2]) ** 2;
        if (distance < bestDistance) {
          nearest = candidate;
          bestDistance = distance;
        }
      }
      nearestCache.set(scopedCacheKey, nearest);
    }
    if (!nearest) continue;
    output[index] = nearest.rgb[0];
    output[index + 1] = nearest.rgb[1];
    output[index + 2] = nearest.rgb[2];
  }
  return output;
}

function captureCameraManifest(camera: THREE.Camera): Direct3DCameraManifest {
  const perspective = camera as THREE.PerspectiveCamera;
  const orthographic = camera as THREE.OrthographicCamera;
  return {
    projection: perspective.isPerspectiveCamera
      ? 'perspective'
      : orthographic.isOrthographicCamera ? 'orthographic' : 'other',
    projection_matrix: [...camera.projectionMatrix.elements],
    matrix_world: [...camera.matrixWorld.elements],
    position: [camera.position.x, camera.position.y, camera.position.z],
    quaternion: [camera.quaternion.x, camera.quaternion.y, camera.quaternion.z, camera.quaternion.w],
    ...('near' in camera && Number.isFinite((camera as THREE.PerspectiveCamera).near)
      ? { near: (camera as THREE.PerspectiveCamera).near } : {}),
    ...('far' in camera && Number.isFinite((camera as THREE.PerspectiveCamera).far)
      ? { far: (camera as THREE.PerspectiveCamera).far } : {}),
    ...(perspective.isPerspectiveCamera
      ? { fov: perspective.fov, aspect: perspective.aspect, zoom: perspective.zoom }
      : orthographic.isOrthographicCamera ? { zoom: orthographic.zoom } : {}),
  };
}

function closestProposalRole(red: number, green: number, blue: number): Direct3DProposalRole {
  let bestRole: Direct3DProposalRole = DIRECT_3D_PROPOSAL_ROLES[0];
  let bestDistance = Number.POSITIVE_INFINITY;
  for (const role of DIRECT_3D_PROPOSAL_ROLES) {
    const [targetRed, targetGreen, targetBlue] = CLASS_RGB[role];
    const distance = (red - targetRed) ** 2 + (green - targetGreen) ** 2 + (blue - targetBlue) ** 2;
    if (distance < bestDistance) {
      bestRole = role;
      bestDistance = distance;
    }
  }
  return bestRole;
}

export function analyzeDirect3DClassPixels(
  bottomUpPixels: Uint8Array | Uint8ClampedArray,
  width: number,
  height: number,
): CaptureAnalysis {
  if (bottomUpPixels.length !== width * height * 4) {
    throw new Direct3DCaptureError('capture_failed', 'Direct 3D class buffer dimensions do not match.');
  }

  const source = flipRgbaRows(bottomUpPixels, width, height);
  const classIdPixels = new Uint8ClampedArray(source.length);
  const maskPixels = new Uint8ClampedArray(source.length);
  const classCounts: Partial<Record<Direct3DProposalRole, number>> = {};
  let proposalPixelCount = 0;

  for (let index = 0; index < source.length; index += 4) {
    const alpha = source[index + 3];
    const solid = alpha >= MASK_SOLID_ALPHA;
    maskPixels[index] = alpha;
    maskPixels[index + 1] = alpha;
    maskPixels[index + 2] = alpha;
    maskPixels[index + 3] = 255;
    classIdPixels[index + 3] = 255;

    if (!solid) continue;

    // Readback may contain premultiplied edge values. Solid pixels normally
    // have alpha=255, but normalizing keeps classification stable on MSAA
    // resolve edges that happen to land exactly on the threshold.
    const alphaScale = 255 / Math.max(alpha, 1);
    const role = closestProposalRole(
      Math.min(255, source[index] * alphaScale),
      Math.min(255, source[index + 1] * alphaScale),
      Math.min(255, source[index + 2] * alphaScale),
    );
    const [red, green, blue] = CLASS_RGB[role];
    classIdPixels[index] = red;
    classIdPixels[index + 1] = green;
    classIdPixels[index + 2] = blue;
    classCounts[role] = (classCounts[role] ?? 0) + 1;
    proposalPixelCount += 1;
  }

  const totalPixels = width * height;
  const classCoverage: Partial<Record<Direct3DProposalRole, number>> = {};
  for (const role of DIRECT_3D_PROPOSAL_ROLES) {
    const count = classCounts[role] ?? 0;
    if (count > 0) classCoverage[role] = count / totalPixels;
  }

  return {
    classIdPixels,
    maskPixels,
    proposalPixelCount,
    contextPixelCount: totalPixels - proposalPixelCount,
    maskCoverage: proposalPixelCount / totalPixels,
    classCoverage,
  };
}

export function analyzeDirect3DInstancePixels(
  bottomUpPixels: Uint8Array | Uint8ClampedArray,
  width: number,
  height: number,
  manifest: Readonly<Record<string, Direct3DInstanceDescriptor>>,
  classIdPixels?: Uint8ClampedArray,
): InstanceCaptureAnalysis {
  if (bottomUpPixels.length !== width * height * 4) {
    throw new Direct3DCaptureError('capture_failed', 'Direct 3D instance buffer dimensions do not match.');
  }
  if (classIdPixels && classIdPixels.length !== width * height * 4) {
    throw new Direct3DCaptureError('capture_failed', 'Direct 3D class and instance buffer dimensions do not match.');
  }

  const source = flipRgbaRows(bottomUpPixels, width, height);
  const instanceIdPixels = new Uint8ClampedArray(source.length);
  const candidates = Object.entries(manifest).map(([color, descriptor]) => ({
    color,
    descriptor,
    rgb: parseHexColor(color),
  }));
  const candidatesByRole = new Map<Direct3DProposalRole, typeof candidates>();
  for (const role of DIRECT_3D_PROPOSAL_ROLES) {
    candidatesByRole.set(role, candidates.filter((candidate) => candidate.descriptor.semantic_class === role));
  }
  const roleByClassColor = new Map(DIRECT_3D_PROPOSAL_ROLES.map((role) => {
    const [red, green, blue] = CLASS_RGB[role];
    return [(red << 16) | (green << 8) | blue, role] as const;
  }));
  const nearestColorCache = new Map<string, typeof candidates[number] | null>();
  const pixelCounts: Record<string, number> = {};

  for (let index = 0; index < source.length; index += 4) {
    const alpha = source[index + 3];
    instanceIdPixels[index + 3] = 255;
    if (alpha < MASK_SOLID_ALPHA || candidates.length === 0) continue;

    const alphaScale = 255 / Math.max(alpha, 1);
    const red = Math.round(Math.min(255, source[index] * alphaScale));
    const green = Math.round(Math.min(255, source[index + 1] * alphaScale));
    const blue = Math.round(Math.min(255, source[index + 2] * alphaScale));
    const cacheKey = (red << 16) | (green << 8) | blue;
    const classKey = classIdPixels
      ? (classIdPixels[index] << 16) | (classIdPixels[index + 1] << 8) | classIdPixels[index + 2]
      : null;
    const semanticRole = classKey === null ? null : roleByClassColor.get(classKey) ?? null;
    const eligibleCandidates = semanticRole ? candidatesByRole.get(semanticRole) ?? [] : candidates;
    if (eligibleCandidates.length === 0) continue;
    const scopedCacheKey = `${semanticRole ?? '*'}:${cacheKey}`;
    let nearest = nearestColorCache.get(scopedCacheKey);
    if (nearest === undefined) {
      nearest = null;
      let bestDistance = Number.POSITIVE_INFINITY;
      for (const candidate of eligibleCandidates) {
        const distance = (red - candidate.rgb[0]) ** 2
          + (green - candidate.rgb[1]) ** 2
          + (blue - candidate.rgb[2]) ** 2;
        if (distance < bestDistance) {
          nearest = candidate;
          bestDistance = distance;
        }
      }
      nearestColorCache.set(scopedCacheKey, nearest);
    }
    if (!nearest) continue;

    instanceIdPixels[index] = nearest.rgb[0];
    instanceIdPixels[index + 1] = nearest.rgb[1];
    instanceIdPixels[index + 2] = nearest.rgb[2];
    pixelCounts[nearest.descriptor.instance_id] = (
      pixelCounts[nearest.descriptor.instance_id] ?? 0
    ) + 1;
  }

  return { instanceIdPixels, pixelCounts };
}

/** Mirror the backend's authoritative class/instance ownership check so the
 * free capture preview catches render-order disagreements before a paid action. */
export function validateDirect3DInstanceSemanticAgreement(
  classIdPixels: Uint8ClampedArray,
  instanceIdPixels: Uint8ClampedArray,
  width: number,
  height: number,
  manifest: Readonly<Record<string, Direct3DInstanceDescriptor>>,
  minimumAgreement = 0.9,
): void {
  const expectedLength = width * height * 4;
  if (
    classIdPixels.length !== expectedLength
    || instanceIdPixels.length !== expectedLength
  ) {
    throw new Direct3DCaptureError(
      'capture_failed',
      'Direct 3D class and instance buffers must have matching dimensions.',
    );
  }
  const ownership = new Map<number, {
    descriptor: Direct3DInstanceDescriptor;
    expectedClass: number;
    pixels: number;
    matches: number;
  }>();
  for (const [color, descriptor] of Object.entries(manifest)) {
    const [red, green, blue] = parseHexColor(color);
    const [classRed, classGreen, classBlue] = CLASS_RGB[descriptor.semantic_class];
    ownership.set((red << 16) | (green << 8) | blue, {
      descriptor,
      expectedClass: (classRed << 16) | (classGreen << 8) | classBlue,
      pixels: 0,
      matches: 0,
    });
  }
  for (let offset = 0; offset < expectedLength; offset += 4) {
    const instanceColor = (
      (instanceIdPixels[offset] << 16)
      | (instanceIdPixels[offset + 1] << 8)
      | instanceIdPixels[offset + 2]
    );
    const entry = ownership.get(instanceColor);
    if (!entry) continue;
    entry.pixels += 1;
    const classColor = (
      (classIdPixels[offset] << 16)
      | (classIdPixels[offset + 1] << 8)
      | classIdPixels[offset + 2]
    );
    if (classColor === entry.expectedClass) entry.matches += 1;
  }
  for (const entry of ownership.values()) {
    if (entry.pixels === 0) continue;
    const agreement = entry.matches / entry.pixels;
    if (agreement < minimumAgreement) {
      throw new Direct3DCaptureError(
        'capture_failed',
        `Direct 3D instance ${entry.descriptor.instance_id} conflicts with its semantic class `
          + `(agreement ${agreement.toFixed(3)}).`,
      );
    }
  }
}

function assertBeautyPlausible(pixels: Uint8Array, width: number, height: number): void {
  let minLuma = 255;
  let maxLuma = 0;
  let visibleSamples = 0;
  let samples = 0;
  const pixelCount = width * height;
  const sampleStep = Math.max(1, Math.floor(pixelCount / 4096));

  for (let pixel = 0; pixel < pixelCount; pixel += sampleStep) {
    const index = pixel * 4;
    const alpha = pixels[index + 3];
    const luma = 0.2126 * pixels[index] + 0.7152 * pixels[index + 1] + 0.0722 * pixels[index + 2];
    minLuma = Math.min(minLuma, luma);
    maxLuma = Math.max(maxLuma, luma);
    if (alpha >= MASK_SOLID_ALPHA) visibleSamples += 1;
    samples += 1;
  }

  if (samples === 0 || visibleSamples / samples < 0.5 || maxLuma - minLuma < 4) {
    throw new Direct3DCaptureError(
      'invalid_beauty',
      'The current 3D frame is blank or incomplete. Wait for the globe to finish loading, then try again.',
    );
  }
}

export function validateDirect3DMaskCoverage(
  coverage: number,
  proposalPixelCount: number,
  minCoverage = DEFAULT_MIN_MASK_COVERAGE,
  maxCoverage = DEFAULT_MAX_MASK_COVERAGE,
): void {
  if (proposalPixelCount < 16 || coverage < minCoverage) {
    throw new Direct3DCaptureError(
      'no_proposal_content',
      'No visible compiled 3D proposal was found in the current camera view.',
    );
  }
  if (!Number.isFinite(coverage) || coverage > maxCoverage) {
    throw new Direct3DCaptureError(
      'invalid_mask_coverage',
      'The proposal fills too much of the frame to preserve trustworthy site context. Zoom out slightly and try again.',
    );
  }
}

function hashCapture(
  width: number,
  height: number,
  maskPixels: Uint8ClampedArray,
  classIdPixels: Uint8ClampedArray,
  instanceIdPixels: Uint8ClampedArray,
  camera: THREE.Camera,
): string {
  let hash = 0x811c9dc5;
  const feed = (value: number) => {
    hash ^= value & 0xff;
    hash = Math.imul(hash, 0x01000193) >>> 0;
  };

  for (const value of [width, width >>> 8, height, height >>> 8]) feed(value);
  for (let index = 0; index < maskPixels.length; index += 4) {
    feed(maskPixels[index] >= MASK_SOLID_ALPHA ? 1 : 0);
    feed(classIdPixels[index]);
    feed(classIdPixels[index + 1]);
    feed(classIdPixels[index + 2]);
    feed(instanceIdPixels[index]);
    feed(instanceIdPixels[index + 1]);
    feed(instanceIdPixels[index + 2]);
  }
  const cameraValues = [...camera.projectionMatrix.elements, ...camera.matrixWorld.elements];
  for (const value of cameraValues) {
    const quantized = Math.round(value * 1_000_000);
    feed(quantized);
    feed(quantized >>> 8);
    feed(quantized >>> 16);
    feed(quantized >>> 24);
  }

  return `d3d-${width}x${height}-${hash.toString(16).padStart(8, '0')}`;
}

export type Direct3DSemanticMaterial = THREE.Material | THREE.Material[];

const MATERIAL_POLICY_KEYS = [
  'visible',
  'side',
  'shadowSide',
  'opacity',
  'transparent',
  'alphaHash',
  'alphaTest',
  'alphaToCoverage',
  'premultipliedAlpha',
  'blending',
  'blendSrc',
  'blendDst',
  'blendEquation',
  'blendSrcAlpha',
  'blendDstAlpha',
  'blendEquationAlpha',
  'blendColor',
  'blendAlpha',
  'depthFunc',
  'depthTest',
  'depthWrite',
  'colorWrite',
  'stencilWrite',
  'stencilWriteMask',
  'stencilFunc',
  'stencilRef',
  'stencilFuncMask',
  'stencilFail',
  'stencilZFail',
  'stencilZPass',
  'polygonOffset',
  'polygonOffsetFactor',
  'polygonOffsetUnits',
  'clipIntersection',
  'clipShadows',
  'clippingPlanes',
  'forceSinglePass',
] as const;

const MAP_ALPHA_ONLY_FRAGMENT = `
#ifdef USE_MAP
  vec4 sampledDiffuseColor = texture2D( map, vMapUv );
  diffuseColor.a *= sampledDiffuseColor.a;
#endif
`;

const PARTICLE_MAP_ALPHA_ONLY_FRAGMENT = `
#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
  #if defined( USE_POINTS_UV )
    vec2 uv = vUv;
  #else
    vec2 uv = ( uvTransform * vec3( gl_PointCoord.x, 1.0 - gl_PointCoord.y, 1 ) ).xy;
  #endif
#endif
#ifdef USE_MAP
  diffuseColor.a *= texture2D( map, uv ).a;
#endif
#ifdef USE_ALPHAMAP
  diffuseColor.a *= texture2D( alphaMap, uv ).g;
#endif
`;

type MaterialWithAlphaTextures = THREE.Material & {
  map?: THREE.Texture | null;
  alphaMap?: THREE.Texture | null;
  wireframe?: boolean;
  wireframeLinewidth?: number;
  linewidth?: number;
  linecap?: string;
  linejoin?: string;
  size?: number;
  sizeAttenuation?: boolean;
  rotation?: number;
  scale?: number;
  dashSize?: number;
  gapSize?: number;
  transmission?: number;
};

function copyMaterialPolicy(source: THREE.Material, target: THREE.Material): void {
  const sourceRecord = source as unknown as Record<string, unknown>;
  const targetRecord = target as unknown as Record<string, unknown>;
  for (const key of MATERIAL_POLICY_KEYS) {
    if (key in sourceRecord && sourceRecord[key] !== undefined) {
      targetRecord[key] = sourceRecord[key];
    }
  }
}

/** A geometry pass must depict the same visible site as beauty. A global
 * overrideMaterial loses tile demolition cuts, cutout foliage, sidedness and
 * depth policy, causing control images to resurrect occluded source buildings. */
export function createDirect3DGeometryMaterial(
  source: THREE.Material,
  pass: 'depth' | 'normal',
): THREE.Material {
  const target = pass === 'depth'
    // Canvas2D PNG encoding premultiplies alpha. RGBA depth stores fractional
    // depth bits in alpha (often zero), losing its RGB on export. RGB packing
    // keeps 24-bit depth and an opaque alpha channel through the PNG encoder.
    ? new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBDepthPacking })
    : new THREE.MeshNormalMaterial();
  copyMaterialPolicy(source, target);
  const sourceRecord = source as unknown as Record<string, unknown>;
  const targetRecord = target as unknown as Record<string, unknown>;
  for (const key of [
    'map', 'alphaMap', 'wireframe', 'wireframeLinewidth', 'flatShading',
    'displacementMap', 'displacementScale', 'displacementBias',
  ]) {
    if (sourceRecord[key] !== undefined) targetRecord[key] = sourceRecord[key];
  }
  if (pass === 'normal') {
    // Depth material has no normal/bump uniforms. Adding these properties to
    // it makes Three's common uniform refresh crash on real textured models.
    for (const key of ['normalMap', 'normalMapType', 'normalScale', 'bumpMap', 'bumpScale']) {
      if (sourceRecord[key] !== undefined) targetRecord[key] = sourceRecord[key];
    }
    // Three's normal material omits alpha chunks and their uniforms. Reuse the
    // source texture alpha only; its RGB must never tint renderer normals.
    const textures = source as MaterialWithAlphaTextures;
    for (const texture of [textures.map, textures.alphaMap]) {
      if (texture?.matrixAutoUpdate) texture.updateMatrix();
    }
    target.onBeforeCompile = (shader) => {
      shader.uniforms.map = { value: textures.map ?? null };
      shader.uniforms.mapTransform = { value: textures.map?.matrix ?? new THREE.Matrix3() };
      shader.uniforms.alphaMap = { value: textures.alphaMap ?? null };
      shader.uniforms.alphaMapTransform = { value: textures.alphaMap?.matrix ?? new THREE.Matrix3() };
      shader.uniforms.alphaTest = { value: source.alphaTest };
      shader.fragmentShader = `
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#ifdef USE_ALPHAHASH
varying vec3 vPosition;
#endif
${shader.fragmentShader}`.replace('#include <normal_fragment_begin>', `
${MAP_ALPHA_ONLY_FRAGMENT}
#include <alphamap_fragment>
#include <alphatest_fragment>
#include <alphahash_fragment>
#include <normal_fragment_begin>`);
    };
    target.customProgramCacheKey = () => 'direct3d-normal-source-alpha-v1';
  }
  inheritTileSpatialMask(source, target);
  target.name = `direct3d-${pass}-${source.name || source.type}`;
  target.needsUpdate = true;
  return target;
}

function createGeometryMaterialCache() {
  const cached = new WeakMap<THREE.Material, Map<'depth' | 'normal', THREE.Material>>();
  const created = new Set<THREE.Material>();
  const getSingle = (source: THREE.Material, pass: 'depth' | 'normal') => {
    let variants = cached.get(source);
    if (!variants) {
      variants = new Map();
      cached.set(source, variants);
    }
    const existing = variants.get(pass);
    if (existing) return existing;
    const material = createDirect3DGeometryMaterial(source, pass);
    variants.set(pass, material);
    created.add(material);
    return material;
  };
  return {
    get: (source: Direct3DSemanticMaterial, pass: 'depth' | 'normal'): Direct3DSemanticMaterial => (
      Array.isArray(source) ? source.map((material) => getSingle(material, pass)) : getSingle(source, pass)
    ),
    dispose: () => created.forEach((material) => material.dispose()),
  };
}

function preserveTextureAlphaWithoutBeautyColor(
  target: THREE.Material,
  source: MaterialWithAlphaTextures,
): void {
  const targetWithMaps = target as MaterialWithAlphaTextures;
  if ('map' in targetWithMaps && source.map) targetWithMaps.map = source.map;
  if ('alphaMap' in targetWithMaps && source.alphaMap) targetWithMaps.alphaMap = source.alphaMap;
  if (!source.map) return;

  target.onBeforeCompile = (shader) => {
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <map_fragment>', MAP_ALPHA_ONLY_FRAGMENT)
      .replace('#include <map_particle_fragment>', PARTICLE_MAP_ALPHA_ONLY_FRAGMENT);
  };
  target.customProgramCacheKey = () => 'siteforge-direct3d-semantic-alpha-v1';
}

function semanticObjectKind(object: THREE.Object3D): 'mesh' | 'line' | 'points' | 'sprite' {
  const typed = object as THREE.Object3D & { isLine?: boolean; isPoints?: boolean; isSprite?: boolean };
  if (typed.isLine) return 'line';
  if (typed.isPoints) return 'points';
  if (typed.isSprite) return 'sprite';
  return 'mesh';
}

function semanticSurfaceOwnsOpaqueId(
  source: MaterialWithAlphaTextures,
  kind: ReturnType<typeof semanticObjectKind>,
): boolean {
  if (kind !== 'mesh' || source.alphaTest > 0 || source.alphaMap) return false;
  return (source.transmission ?? 0) > 0
    || /glass|glaz|window|pane/i.test(source.name || '');
}

function createSingleDirect3DSemanticMaterial(
  source: THREE.Material,
  role: Direct3DProposalRole,
  object: THREE.Object3D,
  semanticColor = DIRECT_3D_CLASS_COLORS[role],
): THREE.Material {
  const sourceTyped = source as MaterialWithAlphaTextures;
  const color = semanticColor;
  const kind = semanticObjectKind(object);
  let target: THREE.Material;

  if (kind === 'line') {
    target = source instanceof THREE.LineDashedMaterial
      ? new THREE.LineDashedMaterial({
        color,
        linewidth: sourceTyped.linewidth,
        scale: sourceTyped.scale,
        dashSize: sourceTyped.dashSize,
        gapSize: sourceTyped.gapSize,
        toneMapped: false,
      })
      : new THREE.LineBasicMaterial({
        color,
        linewidth: sourceTyped.linewidth,
        toneMapped: false,
      });
  } else if (kind === 'points') {
    target = new THREE.PointsMaterial({
      color,
      map: sourceTyped.map,
      alphaMap: sourceTyped.alphaMap,
      size: sourceTyped.size,
      sizeAttenuation: sourceTyped.sizeAttenuation,
      fog: false,
      toneMapped: false,
    });
  } else if (kind === 'sprite') {
    target = new THREE.SpriteMaterial({
      color,
      map: sourceTyped.map,
      alphaMap: sourceTyped.alphaMap,
      rotation: sourceTyped.rotation,
      sizeAttenuation: sourceTyped.sizeAttenuation,
      fog: false,
      toneMapped: false,
    });
  } else {
    target = new THREE.MeshBasicMaterial({
      color,
      map: sourceTyped.map,
      alphaMap: sourceTyped.alphaMap,
      wireframe: sourceTyped.wireframe,
      wireframeLinewidth: sourceTyped.wireframeLinewidth,
      fog: false,
      toneMapped: false,
    });
  }

  target.name = `siteforge-direct3d-${role}-${source.name || source.type}`;
  copyMaterialPolicy(source, target);
  preserveTextureAlphaWithoutBeautyColor(target, sourceTyped);
  // Transparent architectural glazing still physically owns a surface in ID
  // space. Letting it alpha-blend with the class/material behind it makes the
  // exact-color material pass disagree with the class pass, especially at
  // close range. Cut-out foliage/cards retain their alpha policy above.
  if (semanticSurfaceOwnsOpaqueId(sourceTyped, kind)) {
    target.transparent = false;
    target.opacity = 1;
    target.depthWrite = true;
  }
  target.needsUpdate = true;
  return target;
}

/** Build a class-color material with the source material's visibility rules. */
export function createDirect3DSemanticMaterial(
  source: Direct3DSemanticMaterial,
  role: Direct3DProposalRole,
  object: THREE.Object3D,
  semanticColor = DIRECT_3D_CLASS_COLORS[role],
): Direct3DSemanticMaterial {
  if (Array.isArray(source)) {
    return source.map((material) => (
      createSingleDirect3DSemanticMaterial(material, role, object, semanticColor)
    ));
  }
  return createSingleDirect3DSemanticMaterial(source, role, object, semanticColor);
}

export function disposeDirect3DSemanticMaterial(material: Direct3DSemanticMaterial): void {
  if (Array.isArray(material)) {
    material.forEach((entry) => entry.dispose());
  } else {
    material.dispose();
  }
}

function createSemanticMaterialCache(): {
  get: (
    source: Direct3DSemanticMaterial,
    role: Direct3DProposalRole,
    object: THREE.Object3D,
    semanticColor?: string,
  ) => Direct3DSemanticMaterial;
  dispose: () => void;
} {
  const cache = new WeakMap<THREE.Material, Map<string, THREE.Material>>();
  const created = new Set<THREE.Material>();

  const getSingle = (
    source: THREE.Material,
    role: Direct3DProposalRole,
    object: THREE.Object3D,
    semanticColor = DIRECT_3D_CLASS_COLORS[role],
  ): THREE.Material => {
    const key = `${role}:${semanticColor.toUpperCase()}:${semanticObjectKind(object)}`;
    let variants = cache.get(source);
    if (!variants) {
      variants = new Map();
      cache.set(source, variants);
    }
    const existing = variants.get(key);
    if (existing) return existing;
    const material = createSingleDirect3DSemanticMaterial(source, role, object, semanticColor);
    variants.set(key, material);
    created.add(material);
    return material;
  };

  return {
    get: (source, role, object, semanticColor) => (
      Array.isArray(source)
        ? source.map((material) => getSingle(material, role, object, semanticColor))
        : getSingle(source, role, object, semanticColor)
    ),
    dispose: () => created.forEach((material) => material.dispose()),
  };
}

/**
 * Capture the current globe camera without touching the Classic polygon render
 * path. All passes use the live renderer and an off-screen render target, so
 * Google Tiles material hooks and the tile stencil pipeline remain intact.
 */
export async function captureDirect3DScene(
  renderer: THREE.WebGLRenderer,
  scene: THREE.Scene,
  camera: THREE.Camera,
  options: Direct3DCaptureOptions = {},
): Promise<Direct3DCaptureBundle> {
  assertContextAvailable(renderer);
  camera.updateMatrixWorld(true);

  const drawingBufferSize = renderer.getDrawingBufferSize(new THREE.Vector2());
  const { width, height } = computeDirect3DCaptureSize(
    drawingBufferSize.x,
    drawingBufferSize.y,
    options.maxLongEdge ?? DEFAULT_MAX_LONG_EDGE,
  );
  const renderables = collectRenderableSnapshots(scene);
  if (!renderables.some((snapshot) => snapshot.role && snapshot.effectivelyVisible && !snapshot.excluded)) {
    throw new Direct3DCaptureError(
      'no_proposal_content',
      'No visible compiled 3D proposal is mounted in the current scene.',
    );
  }
  const encounteredInstances: Direct3DInstanceDescriptor[] = [];
  for (const snapshot of renderables) {
    if (!snapshot.effectivelyVisible || snapshot.excluded || !snapshot.role) continue;
    encounteredInstances.push(requireDirect3DInstanceDescriptor(
      snapshot.role,
      snapshot.instance,
    ) as Direct3DInstanceDescriptor);
  }
  const {
    assignments: instanceAssignments,
    manifest: instanceIdManifest,
  } = buildDirect3DInstanceColorManifest(encounteredInstances);

  const rendererSnapshot = snapshotRenderer(renderer, scene);
  const semanticMaterials = createSemanticMaterialCache();
  const geometryMaterials = createGeometryMaterialCache();
  let beautyTarget: THREE.WebGLRenderTarget | null = null;
  let depthTarget: THREE.WebGLRenderTarget | null = null;
  let normalTarget: THREE.WebGLRenderTarget | null = null;
  let materialTarget: THREE.WebGLRenderTarget | null = null;
  let classTarget: THREE.WebGLRenderTarget | null = null;
  let instanceTarget: THREE.WebGLRenderTarget | null = null;
  let depthImageBase64: string | undefined;
  let normalImageBase64: string | undefined;
  let materialIdImageBase64: string | undefined;
  let materialIdManifest: Readonly<Record<string, Direct3DMaterialDescriptor>> | undefined;
  let captureFailure: Direct3DCaptureError | null = null;

  try {
    // Beauty: preserve every scene material and Google tile/stencil hook, but
    // suppress transient editor controls that are not part of the design.
    beautyTarget = createCaptureTarget(renderer, width, height, 'beauty');
    for (const snapshot of renderables) {
      snapshot.object.visible = snapshot.effectivelyVisible && !snapshot.excluded;
    }
    renderer.autoClear = true;
    renderer.setRenderTarget(beautyTarget);
    renderer.setScissorTest(false);
    renderer.setViewport(0, 0, width, height);
    renderer.render(scene, camera);
    const beautyBottomUp = readTargetPixels(renderer, beautyTarget, width, height);
    assertBeautyPlausible(beautyBottomUp, width, height);
    const beautyImageBase64 = rgbaToPngDataUrl(
      flipRgbaRows(beautyBottomUp, width, height),
      width,
      height,
    );

    // Release the multisampled beauty framebuffer before allocating the class
    // framebuffer. At 2048² this keeps the two largest GPU allocations from
    // ever overlapping, which is important on the already memory-heavy globe.
    renderer.setRenderTarget(rendererSnapshot.renderTarget);
    beautyTarget.dispose();
    beautyTarget = null;

    if (options.includeGeometryPasses) {
      // Geometry controls are renderer-space facts, not appearance guidance.
      // They use the exact same camera and visible scene as the beauty pass.
      // Targets are allocated and released serially to keep peak GPU memory
      // bounded while Google Tiles remain resident for the video route.
      scene.background = null;
      scene.fog = null;
      renderer.autoClear = true;
      renderer.setScissorTest(false);
      renderer.setViewport(0, 0, width, height);

      scene.overrideMaterial = null;
      for (const snapshot of renderables) {
        if (snapshot.material !== undefined) snapshot.object.material = geometryMaterials.get(snapshot.material, 'depth');
      }
      depthTarget = createCaptureTarget(renderer, width, height, 'depth');
      renderer.setRenderTarget(depthTarget);
      renderer.setClearColor(0xffffff, 1);
      renderer.render(scene, camera);
      depthImageBase64 = rgbaToPngDataUrl(
        flipRgbaRows(readTargetPixels(renderer, depthTarget, width, height), width, height),
        width,
        height,
      );
      renderer.setRenderTarget(rendererSnapshot.renderTarget);
      depthTarget.dispose();
      depthTarget = null;

      for (const snapshot of renderables) {
        if (snapshot.material !== undefined) snapshot.object.material = geometryMaterials.get(snapshot.material, 'normal');
      }
      normalTarget = createCaptureTarget(renderer, width, height, 'normal');
      renderer.setRenderTarget(normalTarget);
      renderer.setClearColor(new THREE.Color(0.5, 0.5, 1), 1);
      renderer.render(scene, camera);
      normalImageBase64 = rgbaToPngDataUrl(
        flipRgbaRows(readTargetPixels(renderer, normalTarget, width, height), width, height),
        width,
        height,
      );
      renderer.setRenderTarget(rendererSnapshot.renderTarget);
      normalTarget.dispose();
      normalTarget = null;

      scene.overrideMaterial = rendererSnapshot.overrideMaterial;
      for (const snapshot of renderables) {
        if (snapshot.material !== undefined) snapshot.object.material = snapshot.material;
      }
      scene.background = rendererSnapshot.background;
      scene.fog = rendererSnapshot.fog;
    }

    // Semantic proposal ID: first render context only into the class target,
    // then clear color only. Its depth buffer now contains the exact visible
    // Google Tiles ordering produced by the live stencil hooks. Class passes
    // cannot paint proposal geometry that is actually occluded by context,
    // while their own flat materials are free to establish proposal depth.
    scene.background = null;
    scene.fog = rendererSnapshot.fog;
    scene.overrideMaterial = rendererSnapshot.overrideMaterial;
    for (const snapshot of renderables) {
      snapshot.object.visible = snapshot.role === null && snapshot.effectivelyVisible && !snapshot.excluded;
      if (snapshot.material !== undefined) snapshot.object.material = snapshot.material;
    }
    renderer.autoClear = true;
    classTarget = createCaptureTarget(renderer, width, height, 'class-id');
    renderer.setRenderTarget(classTarget);
    renderer.setScissorTest(false);
    renderer.setViewport(0, 0, width, height);
    renderer.setClearColor(0x000000, 0);
    renderer.render(scene, camera);
    assertContextAvailable(renderer);

    if ((options.minVisibleContextCoverage ?? 0) > 0) {
      validateDirect3DVisibleContextPixels(
        readTargetPixels(renderer, classTarget, width, height),
        options.minVisibleContextCoverage!,
      );
    }

    scene.fog = null;
    scene.overrideMaterial = null;
    renderer.autoClear = false;
    renderer.clear(true, false, false);

    for (const role of DIRECT_3D_PROPOSAL_ROLES) {
      for (const snapshot of renderables) {
        const visible = snapshot.role === role && snapshot.effectivelyVisible && !snapshot.excluded;
        snapshot.object.visible = visible;
        if (visible && snapshot.material !== undefined) {
          snapshot.object.material = semanticMaterials.get(snapshot.material, role, snapshot.object);
        }
      }
      renderer.render(scene, camera);
      assertContextAvailable(renderer);
    }

    const classBottomUp = readTargetPixels(renderer, classTarget, width, height);
    renderer.setRenderTarget(rendererSnapshot.renderTarget);
    classTarget.dispose();
    classTarget = null;
    const analysis = analyzeDirect3DClassPixels(classBottomUp, width, height);
    validateDirect3DMaskCoverage(
      analysis.maskCoverage,
      analysis.proposalPixelCount,
      options.minMaskCoverage ?? DEFAULT_MIN_MASK_COVERAGE,
      options.maxMaskCoverage ?? DEFAULT_MAX_MASK_COVERAGE,
    );

    // Instance inventory: repeat the context depth seed in a separate target,
    // then paint every stable scene instance with its own exact color. The
    // class framebuffer is already disposed, bounding peak GPU memory to one
    // full-size semantic target at a time. The manifest was built from all
    // effectively-visible tagged renderables before rendering, so off-camera
    // and fully occluded instances remain represented with zero pixels.
    for (const snapshot of renderables) {
      snapshot.object.visible = snapshot.role === null && snapshot.effectivelyVisible && !snapshot.excluded;
      if (snapshot.material !== undefined) snapshot.object.material = snapshot.material;
    }
    scene.fog = rendererSnapshot.fog;
    scene.overrideMaterial = rendererSnapshot.overrideMaterial;
    renderer.autoClear = true;
    instanceTarget = createCaptureTarget(renderer, width, height, 'instance-id');
    renderer.setRenderTarget(instanceTarget);
    renderer.setScissorTest(false);
    renderer.setViewport(0, 0, width, height);
    renderer.setClearColor(0x000000, 0);
    renderer.render(scene, camera);
    assertContextAvailable(renderer);

    scene.fog = null;
    scene.overrideMaterial = null;
    renderer.autoClear = false;
    renderer.clear(true, false, false);

    const instanceAssignmentById = new Map(instanceAssignments.map((assignment) => (
      [assignment.descriptor.instance_id, assignment]
    )));
    // Match the class pass's role ordering exactly. A single all-instance
    // render can disagree wherever authored layers intentionally use
    // renderOrder/depthTest overrides (for example a terrain footprint under
    // its detailed building). Rendering the same role sequence makes every
    // surviving instance pixel provably owned by the class pixel beneath it.
    for (const role of DIRECT_3D_PROPOSAL_ROLES) {
      for (const snapshot of renderables) {
        const assignment = snapshot.instance
          ? instanceAssignmentById.get(snapshot.instance.instance_id)
          : undefined;
        const visible = Boolean(
          assignment
          && snapshot.role === role
          && assignment.descriptor.semantic_class === role
          && snapshot.effectivelyVisible
          && !snapshot.excluded,
        );
        snapshot.object.visible = visible;
        if (visible && snapshot.material !== undefined && assignment) {
          snapshot.object.material = semanticMaterials.get(
            snapshot.material,
            assignment.descriptor.semantic_class,
            snapshot.object,
            assignment.color,
          );
        }
      }
      renderer.render(scene, camera);
      assertContextAvailable(renderer);
    }

    const instanceBottomUp = readTargetPixels(renderer, instanceTarget, width, height);
    renderer.setRenderTarget(rendererSnapshot.renderTarget);
    instanceTarget.dispose();
    instanceTarget = null;
    const instanceAnalysis = analyzeDirect3DInstancePixels(
      instanceBottomUp,
      width,
      height,
      instanceIdManifest,
      analysis.classIdPixels,
    );
    validateDirect3DInstanceSemanticAgreement(
      analysis.classIdPixels,
      instanceAnalysis.instanceIdPixels,
      width,
      height,
      instanceIdManifest,
    );

    if (options.includeGeometryPasses) {
      const materialCapture = buildDirect3DMaterialColorManifest(renderables);
      materialIdManifest = materialCapture.manifest;
      const assignmentByUuid = new Map(materialCapture.assignments.map((assignment) => (
        [`${assignment.descriptor.semantic_class}:${assignment.material.uuid}`, assignment]
      )));
      for (const snapshot of renderables) {
        snapshot.object.visible = snapshot.role === null && snapshot.effectivelyVisible && !snapshot.excluded;
        if (snapshot.material !== undefined) snapshot.object.material = snapshot.material;
      }
      scene.fog = rendererSnapshot.fog;
      scene.overrideMaterial = rendererSnapshot.overrideMaterial;
      renderer.autoClear = true;
      materialTarget = createCaptureTarget(renderer, width, height, 'material-id');
      renderer.setRenderTarget(materialTarget);
      renderer.setScissorTest(false);
      renderer.setViewport(0, 0, width, height);
      renderer.setClearColor(0x000000, 0);
      renderer.render(scene, camera);
      scene.fog = null;
      scene.overrideMaterial = null;
      renderer.autoClear = false;
      renderer.clear(true, false, false);
      for (const role of DIRECT_3D_PROPOSAL_ROLES) {
        for (const snapshot of renderables) {
          const visible = snapshot.role === role && snapshot.effectivelyVisible && !snapshot.excluded;
          snapshot.object.visible = visible;
          if (!visible || snapshot.material === undefined) continue;
          const sources = Array.isArray(snapshot.material) ? snapshot.material : [snapshot.material];
          const replacements = sources.map((material) => {
            const assignment = assignmentByUuid.get(`${role}:${material.uuid}`);
            return assignment
              ? semanticMaterials.get(material, role, snapshot.object, assignment.color) as THREE.Material
              : material;
          });
          snapshot.object.material = Array.isArray(snapshot.material) ? replacements : replacements[0];
        }
        renderer.render(scene, camera);
        assertContextAvailable(renderer);
      }
      const materialPixels = analyzeDirect3DMaterialPixels(
        readTargetPixels(renderer, materialTarget, width, height),
        width,
        height,
        materialIdManifest,
        analysis.classIdPixels,
      );
      materialIdImageBase64 = rgbaToPngDataUrl(materialPixels, width, height);
      renderer.setRenderTarget(rendererSnapshot.renderTarget);
      materialTarget.dispose();
      materialTarget = null;
    }

    return {
      schema: DIRECT_3D_CAPTURE_SCHEMA,
      beautyImageBase64,
      proposalMaskBase64: rgbaToPngDataUrl(analysis.maskPixels, width, height),
      classIdImageBase64: rgbaToPngDataUrl(analysis.classIdPixels, width, height),
      classIdManifest: DIRECT_3D_CLASS_ID_MANIFEST,
      instanceIdImageBase64: rgbaToPngDataUrl(instanceAnalysis.instanceIdPixels, width, height),
      instanceIdManifest,
      depthImageBase64,
      instancePixelCounts: instanceAnalysis.pixelCounts,
      normalImageBase64,
      materialIdImageBase64,
      materialIdManifest,
      camera: captureCameraManifest(camera),
      width,
      height,
      proposalPixelCount: analysis.proposalPixelCount,
      contextPixelCount: analysis.contextPixelCount,
      maskCoverage: analysis.maskCoverage,
      classCoverage: analysis.classCoverage,
      fingerprint: hashCapture(
        width,
        height,
        analysis.maskPixels,
        analysis.classIdPixels,
        instanceAnalysis.instanceIdPixels,
        camera,
      ),
    };
  } catch (error) {
    captureFailure = error instanceof Direct3DCaptureError
      ? error
      : new Direct3DCaptureError(
          'capture_failed',
          'The Direct 3D scene could not be captured safely.',
          error,
        );
    throw captureFailure;
  } finally {
    let cleanupFailure: unknown;
    try {
      restoreCaptureState(renderer, scene, rendererSnapshot, renderables);
    } catch (error) {
      cleanupFailure = error;
    }
    try {
      semanticMaterials.dispose();
    } catch (error) {
      cleanupFailure ??= error;
    }
    try {
      geometryMaterials.dispose();
    } catch (error) {
      cleanupFailure ??= error;
    }
    for (const target of [beautyTarget, depthTarget, normalTarget, materialTarget, classTarget, instanceTarget]) {
      try {
        target?.dispose();
      } catch (error) {
        cleanupFailure ??= error;
      }
    }
    // Cleanup on a lost context is best-effort. Never replace the actionable
    // context_lost/capture error that caused us to enter this path.
    if (cleanupFailure !== undefined && captureFailure === null) {
      // The capture succeeded, so a cleanup failure is the only actionable
      // outcome; intentionally replace the pending return from the try block.
      // eslint-disable-next-line no-unsafe-finally
      throw new Direct3DCaptureError(
        'capture_failed',
        'The Direct 3D capture completed but renderer state could not be restored.',
        cleanupFailure,
      );
    }
  }
}
