import * as THREE from 'three';

export const DIRECT_3D_CAPTURE_SCHEMA = 'siteforge.direct-3d-capture/v1' as const;
export const DIRECT_3D_PROPOSAL_ROLE_KEY = 'siteforgeDirect3DProposalRole';
export const DIRECT_3D_CAPTURE_EXCLUDE_KEY = 'siteforgeExcludeFromDirect3DCapture';

export const DIRECT_3D_PROPOSAL_ROLES = [
  'ground',
  'landscape',
  'street',
  'park',
  'building',
] as const;

export type Direct3DProposalRole = (typeof DIRECT_3D_PROPOSAL_ROLES)[number];

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
  beautyImageBase64: string;
  proposalMaskBase64: string;
  classIdImageBase64: string;
  classIdManifest: Readonly<Record<string, Direct3DProposalRole>>;
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
  return {
    width: capture.width,
    height: capture.height,
    maskCoverage: capture.maskCoverage,
    classCoverage: { ...capture.classCoverage },
    thumbnails: { beauty, mask, classId },
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
  excluded: boolean;
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

export function direct3DGroundRoleForCommunityKind(
  kind: 'building' | 'park' | 'street' | null | undefined,
): Direct3DProposalRole {
  if (kind === 'park' || kind === 'street') return kind;
  return 'ground';
}

export const DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA: Readonly<Record<string, boolean>> = Object.freeze({
  [DIRECT_3D_CAPTURE_EXCLUDE_KEY]: true,
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
  pass: 'beauty' | 'class-id',
): THREE.WebGLRenderTarget {
  const target = new THREE.WebGLRenderTarget(width, height, {
    depthBuffer: true,
    stencilBuffer: true,
    format: THREE.RGBAFormat,
    type: THREE.UnsignedByteType,
  });
  target.texture.colorSpace = renderer.outputColorSpace;
  target.texture.generateMipmaps = false;
  target.samples = getDirect3DTargetSampleCount(renderer.capabilities.isWebGL2, pass);
  return target;
}

export function getDirect3DTargetSampleCount(
  isWebGL2: boolean,
  pass: 'beauty' | 'class-id',
): number {
  if (!isWebGL2 || pass === 'class-id') return 0;
  // Two samples soften the final beauty edge without the 4x multisample GPU
  // footprint that previously overlapped two 2048² capture targets.
  return 2;
}

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

function createSingleDirect3DSemanticMaterial(
  source: THREE.Material,
  role: Direct3DProposalRole,
  object: THREE.Object3D,
): THREE.Material {
  const sourceTyped = source as MaterialWithAlphaTextures;
  const color = DIRECT_3D_CLASS_COLORS[role];
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
  target.needsUpdate = true;
  return target;
}

/** Build a class-color material with the source material's visibility rules. */
export function createDirect3DSemanticMaterial(
  source: Direct3DSemanticMaterial,
  role: Direct3DProposalRole,
  object: THREE.Object3D,
): Direct3DSemanticMaterial {
  if (Array.isArray(source)) {
    return source.map((material) => createSingleDirect3DSemanticMaterial(material, role, object));
  }
  return createSingleDirect3DSemanticMaterial(source, role, object);
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
  ) => Direct3DSemanticMaterial;
  dispose: () => void;
} {
  const cache = new WeakMap<THREE.Material, Map<string, THREE.Material>>();
  const created = new Set<THREE.Material>();

  const getSingle = (
    source: THREE.Material,
    role: Direct3DProposalRole,
    object: THREE.Object3D,
  ): THREE.Material => {
    const key = `${role}:${semanticObjectKind(object)}`;
    let variants = cache.get(source);
    if (!variants) {
      variants = new Map();
      cache.set(source, variants);
    }
    const existing = variants.get(key);
    if (existing) return existing;
    const material = createSingleDirect3DSemanticMaterial(source, role, object);
    variants.set(key, material);
    created.add(material);
    return material;
  };

  return {
    get: (source, role, object) => (
      Array.isArray(source)
        ? source.map((material) => getSingle(material, role, object))
        : getSingle(source, role, object)
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

  const rendererSnapshot = snapshotRenderer(renderer, scene);
  const semanticMaterials = createSemanticMaterialCache();
  let beautyTarget: THREE.WebGLRenderTarget | null = null;
  let classTarget: THREE.WebGLRenderTarget | null = null;

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

    return {
      schema: DIRECT_3D_CAPTURE_SCHEMA,
      beautyImageBase64,
      proposalMaskBase64: rgbaToPngDataUrl(analysis.maskPixels, width, height),
      classIdImageBase64: rgbaToPngDataUrl(analysis.classIdPixels, width, height),
      classIdManifest: DIRECT_3D_CLASS_ID_MANIFEST,
      width,
      height,
      proposalPixelCount: analysis.proposalPixelCount,
      contextPixelCount: analysis.contextPixelCount,
      maskCoverage: analysis.maskCoverage,
      classCoverage: analysis.classCoverage,
      fingerprint: hashCapture(width, height, analysis.maskPixels, analysis.classIdPixels, camera),
    };
  } catch (error) {
    if (error instanceof Direct3DCaptureError) throw error;
    throw new Direct3DCaptureError(
      'capture_failed',
      'The Direct 3D scene could not be captured safely.',
      error,
    );
  } finally {
    try {
      restoreCaptureState(renderer, scene, rendererSnapshot, renderables);
    } finally {
      try {
        semanticMaterials.dispose();
      } finally {
        beautyTarget?.dispose();
        classTarget?.dispose();
      }
    }
  }
}
