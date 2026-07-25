import * as THREE from 'three';

/** Surface identities are semantic rather than visual-variant names. A later
 * family recipe can tint or replace one material without changing the metric
 * street-section geometry that selected it. */
export type StreetSurfaceMaterialKind =
  | 'asphalt'
  | 'parking_asphalt'
  | 'concrete'
  | 'unit_pavers'
  | 'planting_grass'
  | 'buffer_stone';

export interface StreetSurfaceSemantics {
  kind?: string;
  sourceType?: string;
  surface?: string;
  label?: string;
}

export interface StreetSurfaceMaterialSpec {
  kind: StreetSurfaceMaterialKind;
  /** The procedural image covers this many metres in both texture axes. */
  metersPerTile: number;
  roughness: number;
  metalness: number;
}

export interface StreetSurfaceTextureOptions {
  seed?: string;
  size?: number;
  anisotropy?: number;
}

export interface StreetSurfaceMaterialOptions extends StreetSurfaceTextureOptions {
  tint?: THREE.ColorRepresentation;
  roughness?: number;
  metalness?: number;
}

export interface StreetSurfaceMaterialResources {
  kind: StreetSurfaceMaterialKind;
  spec: StreetSurfaceMaterialSpec;
  albedo: THREE.DataTexture;
  material: THREE.MeshStandardMaterial;
  /** Idempotently releases every Three.js resource owned by this bundle. */
  dispose: () => void;
}

/** Appearance variants may change finish while preserving the locked metric
 * cross-section. European setts are the one intentional semantic override:
 * the same motor/parking/path/sidewalk bands become stone paving instead of
 * asphalt or concrete. */
export function resolveStreetAppearanceMaterialKind(
  baseKind: StreetSurfaceMaterialKind,
  appearanceKitId: string | undefined,
  bandKind: string | undefined,
): StreetSurfaceMaterialKind {
  if (
    appearanceKitId === 'european_cobblestone_v1'
    && ['motor', 'parking', 'path', 'sidewalk'].includes(normalize(bandKind))
  ) return 'buffer_stone';
  return baseKind;
}

/** Convert an absolute palette swatch into a restrained multiplicative tint.
 * Normalizing the brightest channel avoids crushing calibrated procedural
 * albedo to black; blending toward white retains aggregate and joint detail. */
export function createStreetSurfacePaletteTint(
  value: THREE.ColorRepresentation,
): THREE.Color {
  const color = new THREE.Color(value);
  const brightest = Math.max(color.r, color.g, color.b, 1e-6);
  color.setRGB(color.r / brightest, color.g / brightest, color.b / brightest);
  return color.lerp(new THREE.Color(1, 1, 1), 0.55);
}

export const STREET_SURFACE_MATERIAL_SPECS: Readonly<
  Record<StreetSurfaceMaterialKind, StreetSurfaceMaterialSpec>
> = Object.freeze({
  asphalt: Object.freeze({
    kind: 'asphalt', metersPerTile: 4, roughness: 0.93, metalness: 0,
  }),
  parking_asphalt: Object.freeze({
    kind: 'parking_asphalt', metersPerTile: 5, roughness: 0.96, metalness: 0,
  }),
  concrete: Object.freeze({
    kind: 'concrete', metersPerTile: 3, roughness: 0.91, metalness: 0,
  }),
  unit_pavers: Object.freeze({
    kind: 'unit_pavers', metersPerTile: 1.2, roughness: 0.9, metalness: 0,
  }),
  planting_grass: Object.freeze({
    kind: 'planting_grass', metersPerTile: 3, roughness: 0.99, metalness: 0,
  }),
  buffer_stone: Object.freeze({
    kind: 'buffer_stone', metersPerTile: 2, roughness: 0.95, metalness: 0,
  }),
});

function normalize(value: unknown): string {
  return String(value ?? '').toLowerCase().trim().replace(/[\s/-]+/g, '_');
}

function includesAny(value: string, terms: readonly string[]): boolean {
  return terms.some((term) => value.includes(term));
}

/** Resolve catalog/profile prose to one reproducible surface family.
 * Explicit material words win over broad band kinds: a motor/shared band
 * authored as brick must remain pavers instead of being flattened to asphalt. */
export function resolveStreetSurfaceMaterialKind(
  semantics: StreetSurfaceSemantics,
): StreetSurfaceMaterialKind {
  const kind = normalize(semantics.kind);
  const sourceType = normalize(semantics.sourceType);
  const surface = normalize(semantics.surface);
  const label = normalize(semantics.label);
  const description = `${surface} ${label} ${sourceType}`;

  if (includesAny(description, [
    'brick', 'cobble', 'sett', 'unit_pav', 'paver', 'paving', 'herringbone',
  ])) return 'unit_pavers';
  if (includesAny(description, ['concrete', 'cement'])) return 'concrete';
  if (
    ['planting', 'median'].includes(kind)
    || includesAny(sourceType, ['boulevard', 'planting', 'median', 'bioswale'])
    || includesAny(description, ['grass', 'lawn', 'turf', 'meadow', 'soil', 'vegetat'])
  ) return 'planting_grass';
  if (
    ['buffer', 'shoulder'].includes(kind)
    || includesAny(sourceType, ['buffer', 'shoulder', 'ditch'])
    || includesAny(description, ['stone', 'granite', 'limestone', 'gravel', 'aggregate'])
  ) return 'buffer_stone';
  if (kind === 'parking' || includesAny(sourceType, ['parking'])) {
    return 'parking_asphalt';
  }
  if (kind === 'sidewalk') return 'concrete';
  return 'asphalt';
}

function fnv1a(value: string): number {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

/** Position-addressed noise stays deterministic even if pixel generation is
 * later parallelized or individual material branches change loop order. */
function noise(seed: number, x: number, y: number, channel = 0): number {
  let value = seed
    ^ Math.imul(x + 1, 374761393)
    ^ Math.imul(y + 1, 668265263)
    ^ Math.imul(channel + 1, 2246822519);
  value = Math.imul(value ^ (value >>> 13), 1274126177);
  value ^= value >>> 16;
  return (value >>> 0) / 0xffffffff;
}

function byte(value: number): number {
  return Math.max(0, Math.min(255, Math.round(value)));
}

function writePixel(
  data: Uint8Array,
  offset: number,
  color: readonly [number, number, number],
): void {
  data[offset] = byte(color[0]);
  data[offset + 1] = byte(color[1]);
  data[offset + 2] = byte(color[2]);
  data[offset + 3] = 255;
}

function asphaltPixel(
  seed: number,
  x: number,
  y: number,
  parking: boolean,
): [number, number, number] {
  const fine = (noise(seed, x, y) - 0.5) * (parking ? 22 : 17);
  const coarse = (noise(seed, Math.floor(x / 7), Math.floor(y / 7), 1) - 0.5) * 8;
  const aggregate = noise(seed, x, y, 2);
  const fleck = aggregate > 0.986 ? 24 : aggregate < 0.012 ? -18 : 0;
  const base = parking ? [88, 88, 85] : [75, 78, 79];
  return [
    base[0] + fine + coarse + fleck,
    base[1] + fine + coarse + fleck,
    base[2] + fine * 0.9 + coarse + fleck,
  ];
}

function concretePixel(seed: number, x: number, y: number, size: number): [number, number, number] {
  const slab = Math.max(8, Math.floor(size / 2));
  const joint = x % slab <= 1 || y % slab <= 1;
  const pores = noise(seed, x, y, 2);
  const variation = (noise(seed, x, y) - 0.5) * 12 + (pores > 0.99 ? -23 : 0);
  const base = joint ? [151, 150, 145] : [190, 188, 180];
  return [base[0] + variation, base[1] + variation, base[2] + variation * 0.8];
}

function paverPixel(seed: number, x: number, y: number): [number, number, number] {
  // Alternating horizontal/vertical two-brick groups form a deterministic
  // basket/herringbone-like unit-paver read at both oblique and aerial scale.
  const unit = 8;
  const groupX = Math.floor(x / (unit * 2));
  const groupY = Math.floor(y / (unit * 2));
  const horizontal = (groupX + groupY) % 2 === 0;
  const localX = x % (unit * 2);
  const localY = y % (unit * 2);
  const mortar = horizontal
    ? localY % unit <= 1 || localX <= 1
    : localX % unit <= 1 || localY <= 1;
  if (mortar) {
    const mortarNoise = (noise(seed, x, y) - 0.5) * 10;
    return [104 + mortarNoise, 97 + mortarNoise, 87 + mortarNoise];
  }
  const tileX = horizontal ? Math.floor(localX / (unit * 2)) : Math.floor(localX / unit);
  const tileY = horizontal ? Math.floor(localY / unit) : Math.floor(localY / (unit * 2));
  const tileVariation = (noise(seed, groupX * 2 + tileX, groupY * 2 + tileY, 3) - 0.5) * 28;
  const grain = (noise(seed, x, y, 4) - 0.5) * 9;
  return [158 + tileVariation + grain, 92 + tileVariation * 0.55 + grain, 66 + grain];
}

function grassPixel(seed: number, x: number, y: number): [number, number, number] {
  const fine = (noise(seed, x, y) - 0.5) * 24;
  const patch = (noise(seed, Math.floor(x / 9), Math.floor(y / 9), 1) - 0.5) * 18;
  const blade = noise(seed, x, y, 2) > 0.965 ? 16 : 0;
  return [67 + fine * 0.45 + patch, 102 + fine + patch + blade, 54 + fine * 0.5 + patch * 0.4];
}

function stonePixel(seed: number, x: number, y: number, size: number): [number, number, number] {
  const course = Math.max(8, Math.floor(size / 4));
  const row = Math.floor(y / course);
  const shiftedX = x + (row % 2) * Math.floor(course / 2);
  const joint = y % course <= 1 || shiftedX % (course * 2) <= 1;
  const variation = (noise(seed, x, y) - 0.5) * 17;
  const base = joint ? [112, 109, 102] : [157, 153, 142];
  return [base[0] + variation, base[1] + variation, base[2] + variation * 0.8];
}

function normalizeTextureSize(value: number | undefined): number {
  const size = value ?? 128;
  if (!Number.isInteger(size) || size < 16 || size > 1024 || (size & (size - 1)) !== 0) {
    throw new RangeError('Street surface texture size must be a power of two from 16 to 1024.');
  }
  return size;
}

/** Build one owned, deterministic albedo tile. Metric ribbon UVs are already
 * expressed in metres, so repeat converts them to the material's reviewed
 * physical tile size. No cache is retained; callers own and dispose it. */
export function createStreetSurfaceAlbedoTexture(
  kind: StreetSurfaceMaterialKind,
  options: StreetSurfaceTextureOptions = {},
): THREE.DataTexture {
  const spec = STREET_SURFACE_MATERIAL_SPECS[kind];
  const size = normalizeTextureSize(options.size);
  const seedText = options.seed ?? 'siteforge-street-v1';
  const seed = fnv1a(`${kind}:${seedText}`);
  const data = new Uint8Array(size * size * 4);

  for (let y = 0; y < size; y += 1) {
    for (let x = 0; x < size; x += 1) {
      const pixel = (() => {
        switch (kind) {
          case 'asphalt': return asphaltPixel(seed, x, y, false);
          case 'parking_asphalt': return asphaltPixel(seed, x, y, true);
          case 'concrete': return concretePixel(seed, x, y, size);
          case 'unit_pavers': return paverPixel(seed, x, y);
          case 'planting_grass': return grassPixel(seed, x, y);
          case 'buffer_stone': return stonePixel(seed, x, y, size);
        }
      })();
      writePixel(data, (y * size + x) * 4, pixel);
    }
  }

  const texture = new THREE.DataTexture(
    data,
    size,
    size,
    THREE.RGBAFormat,
    THREE.UnsignedByteType,
  );
  texture.name = `street-${kind}-${seedText}`;
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(1 / spec.metersPerTile, 1 / spec.metersPerTile);
  texture.anisotropy = Math.max(4, Math.floor(options.anisotropy ?? 4));
  texture.magFilter = THREE.LinearFilter;
  texture.minFilter = THREE.LinearMipmapLinearFilter;
  texture.generateMipmaps = true;
  texture.unpackAlignment = 1;
  texture.userData = {
    ...texture.userData,
    streetSurfaceKind: kind,
    metersPerTile: spec.metersPerTile,
  };
  texture.needsUpdate = true;
  return texture;
}

/** Allocate a material and its owned albedo texture with an explicit,
 * idempotent disposal boundary suitable for React memo/effect integration. */
export function createStreetSurfaceMaterialResources(
  kindOrSemantics: StreetSurfaceMaterialKind | StreetSurfaceSemantics,
  options: StreetSurfaceMaterialOptions = {},
): StreetSurfaceMaterialResources {
  const kind = typeof kindOrSemantics === 'string'
    ? kindOrSemantics
    : resolveStreetSurfaceMaterialKind(kindOrSemantics);
  const spec = STREET_SURFACE_MATERIAL_SPECS[kind];
  const albedo = createStreetSurfaceAlbedoTexture(kind, options);
  const material = new THREE.MeshStandardMaterial({
    name: `street-${kind}-material`,
    map: albedo,
    color: options.tint ?? '#ffffff',
    roughness: options.roughness ?? spec.roughness,
    metalness: options.metalness ?? spec.metalness,
    side: THREE.DoubleSide,
  });
  let disposed = false;
  const dispose = () => {
    if (disposed) return;
    disposed = true;
    material.dispose();
    albedo.dispose();
  };
  return { kind, spec, albedo, material, dispose };
}
