/**
 * useGlobeCamera.ts — Camera positioning utilities for the 3D globe.
 *
 * Sets camera position in ECEF coordinates to view a specific lat/lng.
 */

import { useCallback, useRef } from 'react';
import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { computeCentroid, haversineDistance } from '../mapEngine/geoUtils';

const DEG_TO_RAD = Math.PI / 180;

export function useGlobeCamera() {
  const controlsRef = useRef<any>(null);
  const cameraRef = useRef<THREE.Camera | null>(null);

  /**
   * Position the camera above a lat/lng at a given altitude.
   * Works by computing the ECEF position and setting camera directly.
   */
  const flyToLatLng = useCallback((
    lat: number,
    lng: number,
    altitudeMeters: number = 500,
  ) => {
    const camera = cameraRef.current;
    if (!camera) return;

    // Get the ECEF position on the surface
    const surfacePos = new THREE.Vector3();
    WGS84_ELLIPSOID.getCartographicToPosition(
      lat * DEG_TO_RAD,
      lng * DEG_TO_RAD,
      0,
      surfacePos,
    );

    // Get the surface normal (up direction at this point)
    const normal = new THREE.Vector3();
    WGS84_ELLIPSOID.getCartographicToNormal(
      lat * DEG_TO_RAD,
      lng * DEG_TO_RAD,
      normal,
    );

    // Camera position = surface + altitude along normal
    // Also offset slightly to get an oblique view (not straight down)
    const cameraPos = surfacePos.clone().add(
      normal.clone().multiplyScalar(altitudeMeters)
    );

    // Add a slight offset for oblique viewing angle (~60 degrees from vertical)
    // Move the camera slightly south and east of the target point
    const east = new THREE.Vector3();
    const north = new THREE.Vector3();
    WGS84_ELLIPSOID.getEastNorthUpAxes(
      lat * DEG_TO_RAD,
      lng * DEG_TO_RAD,
      east,
      north,
      new THREE.Vector3(),
    );

    // Offset camera position for oblique view
    const obliqueOffset = altitudeMeters * 0.7; // Tan(~35deg) for a nice oblique
    cameraPos.add(north.multiplyScalar(-obliqueOffset)); // Move south
    cameraPos.add(east.multiplyScalar(obliqueOffset * 0.3)); // Slight east offset

    camera.position.copy(cameraPos);
    camera.lookAt(surfacePos);
    camera.updateMatrixWorld();

    // Also set the controls pivot point if available
    if (controlsRef.current) {
      if (controlsRef.current.pivotPoint) {
        controlsRef.current.pivotPoint.copy(surfacePos);
      }
      if (controlsRef.current.update) {
        controlsRef.current.update();
      }
    }
  }, []);

  /**
   * Position camera to see a zone's bounding extent.
   */
  const flyToZone = useCallback((coords: number[][]) => {
    if (coords.length === 0) return;

    const [cLng, cLat] = computeCentroid(coords);

    // Compute max distance from centroid to determine altitude
    let maxDist = 0;
    for (const c of coords) {
      const d = haversineDistance([cLng, cLat], c);
      if (d > maxDist) maxDist = d;
    }

    // Altitude based on zone extent, minimum 200m
    const altitude = Math.max(maxDist * 3, 200);

    flyToLatLng(cLat, cLng, altitude);
  }, [flyToLatLng]);

  return {
    controlsRef,
    cameraRef,
    flyToLatLng,
    flyToZone,
  };
}
