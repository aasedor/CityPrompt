/**
 * Procedural Style Mapper
 *
 * Translates archetype aesthetic category + styleProfile descriptors into
 * concrete numeric/color parameters for Three.js procedural building generation.
 *
 * The archetype system stores style information as natural-language descriptors
 * (e.g. "Modernist facade rhythm"). This module maps those to renderable values.
 */

import type { StyleProfile } from './aestheticCatalog';

// ---------------------------------------------------------------------------
// Output type — everything the procedural renderer needs
// ---------------------------------------------------------------------------

export interface ProceduralBuildingStyle {
  // Facade
  wallColor: string;
  wallRoughness: number;
  wallMetalness: number;
  accentColor: string;
  trimColor: string;

  // Windows
  windowColor: string;
  windowOpacity: number;
  windowWidth: number;
  windowHeight: number;
  windowSpacing: number;       // center-to-center
  windowEdgeMargin: number;
  windowRecessed: boolean;
  windowFrameColor: string;

  // Ground floor
  groundFloorStorefront: boolean;
  storefrontHeight: number;
  groundFloorColor: string;

  // Rhythm / bays
  facadeBayWidth: number;
  hasVerticalMullions: boolean;
  hasFacadeBanding: boolean;
  bandingHeight: number;
  bandingColor: string;

  // Roof
  roofForm: 'flat' | 'gabled' | 'hipped' | 'mansard' | 'stepped';
  roofColor: string;
  parapetHeight: number;
  corniceWeight: 'none' | 'light' | 'heavy';
  corniceColor: string;

  // Massing
  hasPodium: boolean;
  podiumFloors: number;
  podiumSetback: number;

  // Balconies
  hasBalconies: boolean;
  balconyProbability: number;

  // Material texture type for getProceduralTexture()
  textureType: string;

  // Floor height override (0 = use default)
  preferredFloorHeight: number;
}

// ---------------------------------------------------------------------------
// Per-category style definitions
// ---------------------------------------------------------------------------

type CategoryStyleDef = Omit<ProceduralBuildingStyle, 'facadeBayWidth'> & {
  facadeBayWidth?: number;
};

const CATEGORY_STYLES: Record<string, CategoryStyleDef> = {
  brownstone_rowhouse: {
    wallColor: '#a0704e',
    wallRoughness: 0.8,
    wallMetalness: 0.02,
    accentColor: '#5c3a1e',
    trimColor: '#e8ddd0',
    windowColor: '#b8d8f0',
    windowOpacity: 0.55,
    windowWidth: 1.0,
    windowHeight: 1.8,
    windowSpacing: 2.8,
    windowEdgeMargin: 1.2,
    windowRecessed: true,
    windowFrameColor: '#f0ece4',
    groundFloorStorefront: false,
    storefrontHeight: 3.2,
    groundFloorColor: '#8b6d4a',
    hasVerticalMullions: false,
    hasFacadeBanding: true,
    bandingHeight: 0.12,
    bandingColor: '#c0a882',
    roofForm: 'flat',
    roofColor: '#5a4a3a',
    parapetHeight: 0.6,
    corniceWeight: 'heavy',
    corniceColor: '#c8b8a0',
    hasPodium: false,
    podiumFloors: 0,
    podiumSetback: 0,
    hasBalconies: false,
    balconyProbability: 0,
    textureType: 'brick',
    preferredFloorHeight: 3.2,
  },

  historical: {
    wallColor: '#c4a67a',
    wallRoughness: 0.75,
    wallMetalness: 0.02,
    accentColor: '#8b6e4e',
    trimColor: '#e8ddd0',
    windowColor: '#a8cce0',
    windowOpacity: 0.5,
    windowWidth: 1.1,
    windowHeight: 1.6,
    windowSpacing: 3.0,
    windowEdgeMargin: 1.3,
    windowRecessed: true,
    windowFrameColor: '#d4c8b8',
    groundFloorStorefront: true,
    storefrontHeight: 3.5,
    groundFloorColor: '#9a8060',
    hasVerticalMullions: false,
    hasFacadeBanding: true,
    bandingHeight: 0.15,
    bandingColor: '#b8a88a',
    roofForm: 'hipped',
    roofColor: '#6b5a48',
    parapetHeight: 0.4,
    corniceWeight: 'heavy',
    corniceColor: '#d0c0a8',
    hasPodium: false,
    podiumFloors: 0,
    podiumSetback: 0,
    hasBalconies: true,
    balconyProbability: 0.4,
    textureType: 'brick',
    preferredFloorHeight: 3.5,
  },

  contemporary_urban: {
    wallColor: '#c8c0b8',
    wallRoughness: 0.5,
    wallMetalness: 0.1,
    accentColor: '#606060',
    trimColor: '#a0a0a0',
    windowColor: '#8cbbd6',
    windowOpacity: 0.5,
    windowWidth: 1.4,
    windowHeight: 1.8,
    windowSpacing: 2.8,
    windowEdgeMargin: 1.0,
    windowRecessed: false,
    windowFrameColor: '#404040',
    groundFloorStorefront: true,
    storefrontHeight: 3.8,
    groundFloorColor: '#505050',
    hasVerticalMullions: true,
    hasFacadeBanding: false,
    bandingHeight: 0.1,
    bandingColor: '#808080',
    roofForm: 'flat',
    roofColor: '#707070',
    parapetHeight: 0.8,
    corniceWeight: 'light',
    corniceColor: '#909090',
    hasPodium: true,
    podiumFloors: 2,
    podiumSetback: 1.5,
    hasBalconies: true,
    balconyProbability: 0.6,
    textureType: 'concrete',
    preferredFloorHeight: 3.2,
  },

  modernist: {
    wallColor: '#d0ccc8',
    wallRoughness: 0.4,
    wallMetalness: 0.1,
    accentColor: '#3a3a3a',
    trimColor: '#808080',
    windowColor: '#90c0e0',
    windowOpacity: 0.45,
    windowWidth: 1.8,
    windowHeight: 2.0,
    windowSpacing: 2.4,
    windowEdgeMargin: 0.8,
    windowRecessed: false,
    windowFrameColor: '#303030',
    groundFloorStorefront: true,
    storefrontHeight: 4.0,
    groundFloorColor: '#404040',
    hasVerticalMullions: true,
    hasFacadeBanding: true,
    bandingHeight: 0.08,
    bandingColor: '#707070',
    roofForm: 'flat',
    roofColor: '#606060',
    parapetHeight: 0.5,
    corniceWeight: 'none',
    corniceColor: '#808080',
    hasPodium: false,
    podiumFloors: 0,
    podiumSetback: 0,
    hasBalconies: false,
    balconyProbability: 0.2,
    textureType: 'concrete',
    preferredFloorHeight: 3.5,
  },

  classical: {
    wallColor: '#e8e0d0',
    wallRoughness: 0.65,
    wallMetalness: 0.02,
    accentColor: '#a09070',
    trimColor: '#f0ece0',
    windowColor: '#a0c0d8',
    windowOpacity: 0.5,
    windowWidth: 1.2,
    windowHeight: 2.0,
    windowSpacing: 3.2,
    windowEdgeMargin: 1.5,
    windowRecessed: true,
    windowFrameColor: '#c0b8a8',
    groundFloorStorefront: false,
    storefrontHeight: 4.2,
    groundFloorColor: '#b8a888',
    hasVerticalMullions: false,
    hasFacadeBanding: true,
    bandingHeight: 0.2,
    bandingColor: '#d0c8b8',
    roofForm: 'hipped',
    roofColor: '#8a7a68',
    parapetHeight: 0.8,
    corniceWeight: 'heavy',
    corniceColor: '#d8d0c0',
    hasPodium: true,
    podiumFloors: 1,
    podiumSetback: 0,
    hasBalconies: true,
    balconyProbability: 0.5,
    textureType: 'concrete',
    preferredFloorHeight: 4.0,
  },

  industrial_brick: {
    wallColor: '#b06840',
    wallRoughness: 0.85,
    wallMetalness: 0.02,
    accentColor: '#4a4a50',
    trimColor: '#808088',
    windowColor: '#a0b8c8',
    windowOpacity: 0.5,
    windowWidth: 1.6,
    windowHeight: 2.2,
    windowSpacing: 3.0,
    windowEdgeMargin: 1.0,
    windowRecessed: false,
    windowFrameColor: '#404048',
    groundFloorStorefront: true,
    storefrontHeight: 4.5,
    groundFloorColor: '#8a6040',
    hasVerticalMullions: false,
    hasFacadeBanding: false,
    bandingHeight: 0.1,
    bandingColor: '#606068',
    roofForm: 'flat',
    roofColor: '#505050',
    parapetHeight: 0.4,
    corniceWeight: 'light',
    corniceColor: '#707078',
    hasPodium: false,
    podiumFloors: 0,
    podiumSetback: 0,
    hasBalconies: false,
    balconyProbability: 0,
    textureType: 'brick',
    preferredFloorHeight: 4.0,
  },

  scandinavian_nordic: {
    wallColor: '#e8e4dc',
    wallRoughness: 0.55,
    wallMetalness: 0.05,
    accentColor: '#a08060',
    trimColor: '#d0c8b8',
    windowColor: '#b0d0e8',
    windowOpacity: 0.45,
    windowWidth: 1.3,
    windowHeight: 1.8,
    windowSpacing: 2.6,
    windowEdgeMargin: 1.0,
    windowRecessed: false,
    windowFrameColor: '#a08060',
    groundFloorStorefront: false,
    storefrontHeight: 3.2,
    groundFloorColor: '#c0b8a8',
    hasVerticalMullions: false,
    hasFacadeBanding: false,
    bandingHeight: 0.06,
    bandingColor: '#c8c0b0',
    roofForm: 'gabled',
    roofColor: '#404040',
    parapetHeight: 0,
    corniceWeight: 'none',
    corniceColor: '#c0b8a8',
    hasPodium: false,
    podiumFloors: 0,
    podiumSetback: 0,
    hasBalconies: true,
    balconyProbability: 0.5,
    textureType: 'wood',
    preferredFloorHeight: 3.0,
  },

  mediterranean: {
    wallColor: '#f0e0c8',
    wallRoughness: 0.7,
    wallMetalness: 0.01,
    accentColor: '#b85c30',
    trimColor: '#e0d0b0',
    windowColor: '#90b8d0',
    windowOpacity: 0.5,
    windowWidth: 1.0,
    windowHeight: 1.6,
    windowSpacing: 2.8,
    windowEdgeMargin: 1.2,
    windowRecessed: true,
    windowFrameColor: '#c0a880',
    groundFloorStorefront: true,
    storefrontHeight: 3.5,
    groundFloorColor: '#c8b898',
    hasVerticalMullions: false,
    hasFacadeBanding: true,
    bandingHeight: 0.1,
    bandingColor: '#d8c8a8',
    roofForm: 'hipped',
    roofColor: '#c07040',
    parapetHeight: 0.3,
    corniceWeight: 'light',
    corniceColor: '#d8c8a8',
    hasPodium: false,
    podiumFloors: 0,
    podiumSetback: 0,
    hasBalconies: true,
    balconyProbability: 0.7,
    textureType: 'concrete',
    preferredFloorHeight: 3.2,
  },

  futuristic: {
    wallColor: '#c0c8d0',
    wallRoughness: 0.2,
    wallMetalness: 0.4,
    accentColor: '#40a0d0',
    trimColor: '#a0a8b0',
    windowColor: '#80c0f0',
    windowOpacity: 0.35,
    windowWidth: 2.0,
    windowHeight: 2.4,
    windowSpacing: 2.2,
    windowEdgeMargin: 0.6,
    windowRecessed: false,
    windowFrameColor: '#404858',
    groundFloorStorefront: true,
    storefrontHeight: 4.5,
    groundFloorColor: '#303840',
    hasVerticalMullions: true,
    hasFacadeBanding: true,
    bandingHeight: 0.06,
    bandingColor: '#50a8d8',
    roofForm: 'flat',
    roofColor: '#404858',
    parapetHeight: 1.0,
    corniceWeight: 'none',
    corniceColor: '#606878',
    hasPodium: true,
    podiumFloors: 2,
    podiumSetback: 2.0,
    hasBalconies: true,
    balconyProbability: 0.4,
    textureType: 'metal',
    preferredFloorHeight: 3.5,
  },

  art_deco: {
    wallColor: '#d8d0c0',
    wallRoughness: 0.55,
    wallMetalness: 0.1,
    accentColor: '#c0a040',
    trimColor: '#e8e0c8',
    windowColor: '#a0c0d8',
    windowOpacity: 0.5,
    windowWidth: 1.2,
    windowHeight: 2.0,
    windowSpacing: 2.8,
    windowEdgeMargin: 1.2,
    windowRecessed: true,
    windowFrameColor: '#b09830',
    groundFloorStorefront: true,
    storefrontHeight: 4.5,
    groundFloorColor: '#a09060',
    hasVerticalMullions: true,
    hasFacadeBanding: true,
    bandingHeight: 0.15,
    bandingColor: '#c8b870',
    roofForm: 'stepped',
    roofColor: '#8a7a60',
    parapetHeight: 1.2,
    corniceWeight: 'heavy',
    corniceColor: '#c0a840',
    hasPodium: true,
    podiumFloors: 3,
    podiumSetback: 2.0,
    hasBalconies: false,
    balconyProbability: 0.1,
    textureType: 'concrete',
    preferredFloorHeight: 3.5,
  },

  traditional_vernacular: {
    wallColor: '#d0b898',
    wallRoughness: 0.8,
    wallMetalness: 0.02,
    accentColor: '#6a5040',
    trimColor: '#e0d0b8',
    windowColor: '#a0c0d0',
    windowOpacity: 0.55,
    windowWidth: 0.9,
    windowHeight: 1.4,
    windowSpacing: 2.8,
    windowEdgeMargin: 1.2,
    windowRecessed: true,
    windowFrameColor: '#f0e8d8',
    groundFloorStorefront: false,
    storefrontHeight: 3.0,
    groundFloorColor: '#b0a080',
    hasVerticalMullions: false,
    hasFacadeBanding: false,
    bandingHeight: 0.1,
    bandingColor: '#c0a888',
    roofForm: 'gabled',
    roofColor: '#6a5848',
    parapetHeight: 0,
    corniceWeight: 'light',
    corniceColor: '#c8b898',
    hasPodium: false,
    podiumFloors: 0,
    podiumSetback: 0,
    hasBalconies: false,
    balconyProbability: 0,
    textureType: 'wood',
    preferredFloorHeight: 3.0,
  },

  minimalist: {
    wallColor: '#f0ece8',
    wallRoughness: 0.35,
    wallMetalness: 0.05,
    accentColor: '#202020',
    trimColor: '#d0d0d0',
    windowColor: '#90c8e8',
    windowOpacity: 0.4,
    windowWidth: 1.6,
    windowHeight: 2.2,
    windowSpacing: 2.4,
    windowEdgeMargin: 0.8,
    windowRecessed: false,
    windowFrameColor: '#202020',
    groundFloorStorefront: true,
    storefrontHeight: 3.8,
    groundFloorColor: '#303030',
    hasVerticalMullions: false,
    hasFacadeBanding: false,
    bandingHeight: 0.04,
    bandingColor: '#e0e0e0',
    roofForm: 'flat',
    roofColor: '#404040',
    parapetHeight: 0.4,
    corniceWeight: 'none',
    corniceColor: '#d0d0d0',
    hasPodium: false,
    podiumFloors: 0,
    podiumSetback: 0,
    hasBalconies: true,
    balconyProbability: 0.3,
    textureType: 'concrete',
    preferredFloorHeight: 3.2,
  },

  parisian: {
    wallColor: '#e8dcc8',
    wallRoughness: 0.6,
    wallMetalness: 0.02,
    accentColor: '#4a4a5a',
    trimColor: '#f0e8d8',
    windowColor: '#a0b8d0',
    windowOpacity: 0.5,
    windowWidth: 1.1,
    windowHeight: 2.0,
    windowSpacing: 2.6,
    windowEdgeMargin: 1.0,
    windowRecessed: true,
    windowFrameColor: '#e0d8c8',
    groundFloorStorefront: true,
    storefrontHeight: 4.0,
    groundFloorColor: '#c0b098',
    hasVerticalMullions: false,
    hasFacadeBanding: true,
    bandingHeight: 0.18,
    bandingColor: '#d8d0c0',
    roofForm: 'mansard',
    roofColor: '#5a5a68',
    parapetHeight: 0.3,
    corniceWeight: 'heavy',
    corniceColor: '#d8d0c0',
    hasPodium: false,
    podiumFloors: 0,
    podiumSetback: 0,
    hasBalconies: true,
    balconyProbability: 0.85,
    textureType: 'concrete',
    preferredFloorHeight: 3.5,
  },

  mountain_alpine: {
    wallColor: '#c8b898',
    wallRoughness: 0.8,
    wallMetalness: 0.02,
    accentColor: '#5a4030',
    trimColor: '#a07848',
    windowColor: '#a8c8e0',
    windowOpacity: 0.55,
    windowWidth: 0.9,
    windowHeight: 1.3,
    windowSpacing: 2.6,
    windowEdgeMargin: 1.2,
    windowRecessed: true,
    windowFrameColor: '#8a6840',
    groundFloorStorefront: false,
    storefrontHeight: 3.2,
    groundFloorColor: '#908070',
    hasVerticalMullions: false,
    hasFacadeBanding: false,
    bandingHeight: 0.1,
    bandingColor: '#a08868',
    roofForm: 'gabled',
    roofColor: '#5a4838',
    parapetHeight: 0,
    corniceWeight: 'light',
    corniceColor: '#a08868',
    hasPodium: false,
    podiumFloors: 0,
    podiumSetback: 0,
    hasBalconies: true,
    balconyProbability: 0.6,
    textureType: 'wood',
    preferredFloorHeight: 3.0,
  },

  transit_oriented_contemporary: {
    wallColor: '#b8b8c0',
    wallRoughness: 0.45,
    wallMetalness: 0.15,
    accentColor: '#d06020',
    trimColor: '#808890',
    windowColor: '#88b8d8',
    windowOpacity: 0.45,
    windowWidth: 1.5,
    windowHeight: 2.0,
    windowSpacing: 2.4,
    windowEdgeMargin: 0.8,
    windowRecessed: false,
    windowFrameColor: '#404850',
    groundFloorStorefront: true,
    storefrontHeight: 4.2,
    groundFloorColor: '#404850',
    hasVerticalMullions: true,
    hasFacadeBanding: true,
    bandingHeight: 0.08,
    bandingColor: '#808890',
    roofForm: 'flat',
    roofColor: '#505860',
    parapetHeight: 0.6,
    corniceWeight: 'none',
    corniceColor: '#707880',
    hasPodium: true,
    podiumFloors: 2,
    podiumSetback: 1.5,
    hasBalconies: true,
    balconyProbability: 0.5,
    textureType: 'metal',
    preferredFloorHeight: 3.2,
  },

  glass_tower_modern: {
    wallColor: '#a0b0c0',
    wallRoughness: 0.1,
    wallMetalness: 0.6,
    accentColor: '#304050',
    trimColor: '#607080',
    windowColor: '#80b0d8',
    windowOpacity: 0.3,
    windowWidth: 2.2,
    windowHeight: 2.6,
    windowSpacing: 2.4,
    windowEdgeMargin: 0.5,
    windowRecessed: false,
    windowFrameColor: '#304050',
    groundFloorStorefront: true,
    storefrontHeight: 5.0,
    groundFloorColor: '#304050',
    hasVerticalMullions: true,
    hasFacadeBanding: true,
    bandingHeight: 0.06,
    bandingColor: '#506070',
    roofForm: 'flat',
    roofColor: '#304050',
    parapetHeight: 1.0,
    corniceWeight: 'none',
    corniceColor: '#506070',
    hasPodium: true,
    podiumFloors: 3,
    podiumSetback: 3.0,
    hasBalconies: false,
    balconyProbability: 0.1,
    textureType: 'glass',
    preferredFloorHeight: 3.8,
  },

  civic_monumental: {
    wallColor: '#d8d0c0',
    wallRoughness: 0.55,
    wallMetalness: 0.05,
    accentColor: '#8a8070',
    trimColor: '#e8e0d0',
    windowColor: '#98b8d0',
    windowOpacity: 0.5,
    windowWidth: 1.4,
    windowHeight: 2.4,
    windowSpacing: 3.5,
    windowEdgeMargin: 2.0,
    windowRecessed: true,
    windowFrameColor: '#c0b8a8',
    groundFloorStorefront: false,
    storefrontHeight: 5.0,
    groundFloorColor: '#b0a890',
    hasVerticalMullions: false,
    hasFacadeBanding: true,
    bandingHeight: 0.25,
    bandingColor: '#c8c0b0',
    roofForm: 'hipped',
    roofColor: '#708068',
    parapetHeight: 1.0,
    corniceWeight: 'heavy',
    corniceColor: '#d0c8b8',
    hasPodium: true,
    podiumFloors: 1,
    podiumSetback: 0,
    hasBalconies: false,
    balconyProbability: 0,
    textureType: 'concrete',
    preferredFloorHeight: 4.5,
  },

  japanese_contemporary: {
    wallColor: '#e0dcd8',
    wallRoughness: 0.4,
    wallMetalness: 0.08,
    accentColor: '#3a3a38',
    trimColor: '#b0a898',
    windowColor: '#98c0d8',
    windowOpacity: 0.4,
    windowWidth: 1.2,
    windowHeight: 1.8,
    windowSpacing: 2.4,
    windowEdgeMargin: 0.8,
    windowRecessed: false,
    windowFrameColor: '#303030',
    groundFloorStorefront: true,
    storefrontHeight: 3.5,
    groundFloorColor: '#404040',
    hasVerticalMullions: true,
    hasFacadeBanding: false,
    bandingHeight: 0.05,
    bandingColor: '#b0a898',
    roofForm: 'flat',
    roofColor: '#404040',
    parapetHeight: 0.3,
    corniceWeight: 'none',
    corniceColor: '#b0a898',
    hasPodium: false,
    podiumFloors: 0,
    podiumSetback: 0,
    hasBalconies: true,
    balconyProbability: 0.3,
    textureType: 'concrete',
    preferredFloorHeight: 3.0,
  },

  eco_urban_green_architecture: {
    wallColor: '#c8d0c0',
    wallRoughness: 0.6,
    wallMetalness: 0.05,
    accentColor: '#4a8040',
    trimColor: '#a0b098',
    windowColor: '#90c8d0',
    windowOpacity: 0.45,
    windowWidth: 1.4,
    windowHeight: 1.8,
    windowSpacing: 2.6,
    windowEdgeMargin: 1.0,
    windowRecessed: false,
    windowFrameColor: '#506048',
    groundFloorStorefront: true,
    storefrontHeight: 3.8,
    groundFloorColor: '#506048',
    hasVerticalMullions: false,
    hasFacadeBanding: true,
    bandingHeight: 0.1,
    bandingColor: '#6a9060',
    roofForm: 'flat',
    roofColor: '#4a8040',
    parapetHeight: 0.6,
    corniceWeight: 'light',
    corniceColor: '#88a880',
    hasPodium: true,
    podiumFloors: 2,
    podiumSetback: 1.0,
    hasBalconies: true,
    balconyProbability: 0.7,
    textureType: 'wood',
    preferredFloorHeight: 3.2,
  },

  coastal_resort_contemporary: {
    wallColor: '#f0ece8',
    wallRoughness: 0.5,
    wallMetalness: 0.05,
    accentColor: '#4088a0',
    trimColor: '#d0dce0',
    windowColor: '#90c8e0',
    windowOpacity: 0.4,
    windowWidth: 1.5,
    windowHeight: 2.0,
    windowSpacing: 2.6,
    windowEdgeMargin: 1.0,
    windowRecessed: false,
    windowFrameColor: '#607880',
    groundFloorStorefront: true,
    storefrontHeight: 3.5,
    groundFloorColor: '#b0c0c8',
    hasVerticalMullions: false,
    hasFacadeBanding: false,
    bandingHeight: 0.08,
    bandingColor: '#c0d0d8',
    roofForm: 'flat',
    roofColor: '#e0d8d0',
    parapetHeight: 0.5,
    corniceWeight: 'none',
    corniceColor: '#c0d0d8',
    hasPodium: false,
    podiumFloors: 0,
    podiumSetback: 0,
    hasBalconies: true,
    balconyProbability: 0.8,
    textureType: 'concrete',
    preferredFloorHeight: 3.2,
  },
};

// Default fallback style
const DEFAULT_STYLE: ProceduralBuildingStyle = {
  wallColor: '#c0b8ac',
  wallRoughness: 0.6,
  wallMetalness: 0.05,
  accentColor: '#606060',
  trimColor: '#d0c8b8',
  windowColor: '#87ceeb',
  windowOpacity: 0.6,
  windowWidth: 1.2,
  windowHeight: 1.4,
  windowSpacing: 3.5,
  windowEdgeMargin: 1.5,
  windowRecessed: false,
  windowFrameColor: '#808080',
  groundFloorStorefront: false,
  storefrontHeight: 3.5,
  groundFloorColor: '#a0a0a0',
  hasVerticalMullions: false,
  hasFacadeBanding: false,
  bandingHeight: 0.1,
  bandingColor: '#b0b0b0',
  facadeBayWidth: 3.5,
  roofForm: 'flat',
  roofColor: '#707070',
  parapetHeight: 0.3,
  corniceWeight: 'light',
  corniceColor: '#c0b8ac',
  hasPodium: false,
  podiumFloors: 0,
  podiumSetback: 0,
  hasBalconies: false,
  balconyProbability: 0,
  textureType: '',
  preferredFloorHeight: 0,
};

// ---------------------------------------------------------------------------
// Height tendency → floor count estimation
// ---------------------------------------------------------------------------

export function estimateFloorCount(
  heightTendency: string | undefined,
  buildingHeight: number,
  floorHeight: number,
): number {
  if (buildingHeight > 0 && floorHeight > 0) {
    return Math.max(1, Math.round(buildingHeight / floorHeight));
  }
  // Fallback from tendency
  const tendency = (heightTendency || '').toLowerCase();
  if (tendency.includes('high')) return 12;
  if (tendency.includes('mid')) return 5;
  return 3;
}

// ---------------------------------------------------------------------------
// Main mapper — resolves category + styleProfile → ProceduralBuildingStyle
// ---------------------------------------------------------------------------

/**
 * Extract the aesthetic category key from a styleProfile or zone properties.
 * The styleProfile field values follow the pattern "Category Name facade rhythm",
 * "Category Name roof expression", etc. We extract the category name and normalize it.
 */
function extractCategoryFromProfile(profile: StyleProfile): string | undefined {
  // Try facadeRhythm, windowStyle, or roofForm — they all follow "Category facade rhythm" pattern
  const sources = [profile.facadeRhythm, profile.windowStyle, profile.roofForm];
  for (const source of sources) {
    if (!source) continue;
    // Remove the descriptor suffix to get category name
    const cleaned = source
      .replace(/\s*facade rhythm$/i, '')
      .replace(/\s*window proportioning$/i, '')
      .replace(/\s*roof expression$/i, '')
      .replace(/\s*material palette$/i, '')
      .trim()
      .toLowerCase()
      .replace(/[\s/]+/g, '_');
    if (cleaned && CATEGORY_STYLES[cleaned]) return cleaned;
  }
  return undefined;
}

export function mapStyleToGeometry(
  categoryId?: string,
  styleProfile?: StyleProfile,
): ProceduralBuildingStyle {
  // Try explicit category first, then try to infer from styleProfile
  let resolvedCategory = categoryId;
  if (!resolvedCategory && styleProfile) {
    resolvedCategory = extractCategoryFromProfile(styleProfile);
  }

  const catStyle = resolvedCategory ? CATEGORY_STYLES[resolvedCategory] : undefined;
  if (!catStyle) return { ...DEFAULT_STYLE };

  return {
    ...DEFAULT_STYLE,
    ...catStyle,
    facadeBayWidth: catStyle.facadeBayWidth ?? catStyle.windowSpacing,
  };
}

/**
 * Check if a massing profile implies a podium/tower form.
 */
export function massingImpliesPodium(massing?: string): boolean {
  if (!massing) return false;
  const lower = massing.toLowerCase();
  return (
    lower.includes('high-rise') ||
    lower.includes('high-density') ||
    lower.includes('tower') ||
    lower.includes('tod ')
  );
}

/**
 * Check if a massing profile implies a low-rise / townhouse form.
 */
export function massingImpliesLowRise(massing?: string): boolean {
  if (!massing) return false;
  const lower = massing.toLowerCase();
  return (
    lower.includes('townhouse') ||
    lower.includes('rowhouse') ||
    lower.includes('detached') ||
    lower.includes('lodge') ||
    lower.includes('chalet') ||
    lower.includes('low density')
  );
}
