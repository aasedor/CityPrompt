import type { ParkGroundGuide } from './parkGroundProfiles';

export type CricketPavilionStyle =
  | 'thatched_tudor'
  | 'municipal_clubhouse'
  | 'maidan_pavilion'
  | 'caribbean_grandstand';

export type CricketPerimeterStyle =
  | 'white_picket'
  | 'chainlink'
  | 'low_concrete_wall'
  | 'painted_timber';

export interface CricketGroundAssetProfile {
  variantIndex: number;
  variantId: string;
  label: string;
  pavilionStyle: CricketPavilionStyle;
  perimeterStyle: CricketPerimeterStyle;
  outfieldColor: string;
  pitchColor: string;
  structurePrimary: string;
  structureSecondary: string;
  roofColor: string;
  accentColor: string;
  suppressGenericMicrodetails: true;
}
export interface CricketGroundProgramFrame {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
  width: number;
  height: number;
}

export interface CricketGroundLayout {
  center: { x: number; y: number };
  rotationRad: number;
  radiusX: number;
  radiusY: number;
  pitchLengthM: number;
  pitchWidthM: number;
  wicketOffsetM: number;
  sightScreenOffsetM: number;
  pavilion: {
    x: number;
    y: number;
    widthM: number;
    depthM: number;
    facingSign: 1 | -1;
  };
}

type CricketZone = {
  properties?: unknown;
};

const CRICKET_PROFILES: readonly CricketGroundAssetProfile[] = Object.freeze([
  Object.freeze({
    variantIndex: 0,
    variantId: 'cricket_pitch_oval_v0',
    label: 'Village Green',
    pavilionStyle: 'thatched_tudor',
    perimeterStyle: 'white_picket',
    outfieldColor: '#527c3f',
    pitchColor: '#b9a56e',
    structurePrimary: '#ece5d2',
    structureSecondary: '#4c3729',
    roofColor: '#8b7145',
    accentColor: '#f4f1e6',
    suppressGenericMicrodetails: true,
  }),
  Object.freeze({
    variantIndex: 1,
    variantId: 'cricket_pitch_oval_v1',
    label: 'Municipal Oval',
    pavilionStyle: 'municipal_clubhouse',
    perimeterStyle: 'chainlink',
    outfieldColor: '#56864b',
    pitchColor: '#a99e75',
    structurePrimary: '#9b5c43',
    structureSecondary: '#8da1a8',
    roofColor: '#4e5c61',
    accentColor: '#eef1eb',
    suppressGenericMicrodetails: true,
  }),
  Object.freeze({
    variantIndex: 2,
    variantId: 'cricket_pitch_oval_v2',
    label: 'South Asian Ground',
    pavilionStyle: 'maidan_pavilion',
    perimeterStyle: 'low_concrete_wall',
    outfieldColor: '#69804e',
    pitchColor: '#a9875e',
    structurePrimary: '#a9613f',
    structureSecondary: '#d4c7a7',
    roofColor: '#777b78',
    accentColor: '#e28037',
    suppressGenericMicrodetails: true,
  }),
  Object.freeze({
    variantIndex: 3,
    variantId: 'cricket_pitch_oval_v3',
    label: 'Caribbean Beach Pitch',
    pavilionStyle: 'caribbean_grandstand',
    perimeterStyle: 'painted_timber',
    outfieldColor: '#6c9b59',
    pitchColor: '#c5aa72',
    structurePrimary: '#3d91a0',
    structureSecondary: '#f1ca57',
    roofColor: '#d65e4a',
    accentColor: '#f1f0df',
    suppressGenericMicrodetails: true,
  }),
]);

function normalizeId(value: unknown): string {
  return String(value ?? '').trim().toLowerCase().replace(/-/g, '_');
}

function variantIndex(value: unknown): number {
  const match = normalizeId(value).match(/(?:_variant_|_v)([0-3])$/);
  return match ? Number(match[1]) : 0;
}

export function resolveCricketGroundAssetProfile(
  zone: CricketZone,
): CricketGroundAssetProfile | null {
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const archetypeId = normalizeId(
    props.green_space_archetype_id ?? props.plaza_archetype_id,
  );
  if (!archetypeId.startsWith('cricket_pitch_oval')) return null;
  const index = variantIndex(
    props.green_space_selected_variant_id ?? props.plaza_selected_variant_id,
  );
  return CRICKET_PROFILES[index] ?? CRICKET_PROFILES[0];
}

function rotateLocalPoint(
  localX: number,
  localY: number,
  center: { x: number; y: number },
  rotationRad: number,
): { x: number; y: number } {
  const cos = Math.cos(rotationRad);
  const sin = Math.sin(rotationRad);
  return {
    x: center.x + localX * cos - localY * sin,
    y: center.y + localX * sin + localY * cos,
  };
}

/** Build one deterministic, metric cricket program from the drape guide.
 * The regulation pitch remains exact even when an undersized parcel uses a
 * compact semantic oval. Pavilion and screens are always outside the playing
 * objects they support, never random scatter candidates. */
export function buildCricketGroundLayout(
  guide: ParkGroundGuide,
  frame: CricketGroundProgramFrame,
): CricketGroundLayout {
  const center = {
    x: frame.minX + frame.width * guide.x,
    y: frame.maxY - frame.height * guide.y,
  };
  const fieldWidth = Math.max(30, guide.widthM ?? guide.width * frame.width);
  const fieldHeight = Math.max(24, guide.heightM ?? guide.height * frame.height);
  const radiusX = Math.max(15, Math.min(fieldWidth / 2, frame.width * 0.46));
  const radiusY = Math.max(12, Math.min(fieldHeight / 2, frame.height * 0.42));
  const rotationRad = -((guide.rotationDeg ?? 0) * Math.PI) / 180;
  const pitchLengthM = Math.min(22.56, radiusX * 1.45);
  const pitchWidthM = Math.min(3.05, radiusY * 0.3);
  const wicketOffsetM = Math.min(10.06, pitchLengthM / 2 - 0.8);
  const sightScreenOffsetM = Math.min(
    radiusX - 2.2,
    Math.max(wicketOffsetM + 7.5, pitchLengthM / 2 + 6.5),
  );

  const pavilionWidthM = Math.min(15, Math.max(10, frame.width * 0.16));
  const desiredDepthM = Math.min(6.5, Math.max(4.2, frame.height * 0.08));
  const localNorthEdge = rotateLocalPoint(0, radiusY, center, rotationRad);
  const localSouthEdge = rotateLocalPoint(0, -radiusY, center, rotationRad);
  const northSpace = Math.max(0, frame.maxY - localNorthEdge.y);
  const southSpace = Math.max(0, localSouthEdge.y - frame.minY);
  const facingSign: 1 | -1 = northSpace >= southSpace ? 1 : -1;
  const availableDepthM = Math.max(northSpace, southSpace);
  const pavilionDepthM = Math.min(desiredDepthM, Math.max(3.2, availableDepthM - 0.8));
  const localPavilion = rotateLocalPoint(
    0,
    facingSign * (radiusY + pavilionDepthM / 2 + 0.45),
    center,
    rotationRad,
  );

  return {
    center,
    rotationRad,
    radiusX,
    radiusY,
    pitchLengthM,
    pitchWidthM,
    wicketOffsetM,
    sightScreenOffsetM,
    pavilion: {
      x: localPavilion.x,
      y: localPavilion.y,
      widthM: pavilionWidthM,
      depthM: pavilionDepthM,
      facingSign,
    },
  };
}
