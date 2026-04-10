/**
 * ecefToMercator.ts
 *
 * Builds a 4×4 matrix that transforms Google 3D Tiles (ECEF coordinates)
 * into Mapbox's Mercator coordinate space.
 *
 * This matrix is multiplied into the camera projection matrix:
 *   camera.projectionMatrix = mapboxMatrix × ecefToMercatorMatrix
 *
 * Based on the Mapbox GL JS custom layer pattern:
 * https://docs.mapbox.com/mapbox-gl-js/example/add-3d-model/
 */

import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import mapboxgl from 'mapbox-gl';

const DEG_TO_RAD = Math.PI / 180;

/**
 * Build a 4×4 matrix transforming ECEF coordinates to Mapbox Mercator space.
 * Multiply this into the camera projection: projMatrix × thisMatrix
 */
export function buildECEFToMercatorMatrix(lng: number, lat: number): THREE.Matrix4 {
  // 1. Get the ENU (East-North-Up) frame at this location
  //    This 4×4 matrix transforms FROM ENU TO ECEF
  //    Its translation column is the ECEF position of the reference point
  //    Its rotation columns are the ENU axes expressed in ECEF
  const enuToEcef = new THREE.Matrix4();
  WGS84_ELLIPSOID.getEastNorthUpFrame(
    lat * DEG_TO_RAD,
    lng * DEG_TO_RAD,
    0,
    enuToEcef,
  );

  // 2. Invert to get ECEF → ENU (local meters, origin at reference point)
  const ecefToEnu = enuToEcef.clone().invert();

  // 3. Get Mercator position and scale
  const mc = mapboxgl.MercatorCoordinate.fromLngLat([lng, lat], 0);
  const meterScale = mc.meterInMercatorCoordinateUnits();

  // 4. Build the Mapbox-style local transform:
  //    translate to Mercator position, then scale meters→Mercator with Y-flip
  //
  //    In Mapbox Mercator space:
  //    - X: east (same as ENU)
  //    - Y: south (OPPOSITE of ENU North) → negative scale
  //    - Z: up (same as ENU)
  const localTransform = new THREE.Matrix4()
    .makeTranslation(mc.x, mc.y, mc.z ?? 0)
    .scale(new THREE.Vector3(meterScale, -meterScale, meterScale));

  // 5. Compose: localTransform × ecefToEnu
  //    This takes ECEF → ENU meters → Mercator scaled + positioned
  return localTransform.multiply(ecefToEnu);
}
