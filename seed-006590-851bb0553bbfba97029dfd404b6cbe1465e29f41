/**
 * Typed accessor for the shared street geometry constants (all metres).
 * The JSON is the single source of truth — scripts/_render_diagrams_toscale.py
 * reads the same file to draw the to-scale 2D diagrams.
 */
import params from './streetGeometryParams.json';

export interface RoundaboutParams {
  /** scene width used by the 2D diagram renderer */
  scene: number;
  /** inscribed circle diameter */
  ICD: number;
  /** circulatory lane width */
  CIRC: number;
  /** truck apron width */
  APRON: number;
  /** approach road width (both directions) */
  APP: number;
  /** splitter island refuge width */
  REFUGE: number;
  /** splitter island length from ICD edge */
  SLEN: number;
  /** crosswalk width */
  CW: number;
  /** crosswalk set-back from ICD edge */
  SETBK: number;
}

export interface StreetDetail3DParams {
  curbHeight_m: number;
  curbWidth_m: number;
  dashLength_m: number;
  dashGap_m: number;
  dashWidth_m: number;
  dashLift_m: number;
  apronLift_m: number;
  islandHeight_m: number;
  /** sampling interval along a centerline for draping/ribbons */
  stationStep_m: number;
}

export const ROUNDABOUT_PARAMS = params.roundabout as RoundaboutParams;
export const PROTECTED_INTERSECTION_PARAMS = params.protectedIntersection;
export const CURB_EXTENSION_PARAMS = params.curbExtension;
export const STREET_DETAIL_3D = params.streetDetail3D as StreetDetail3DParams;
