import { useEffect, useMemo } from 'react';
import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import { DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA } from '@/components/viewer/globe/direct3dCapture';
import { retainResourceForDeferredDisposal } from '@/components/viewer/globe/strictModeResourceDisposal';
import type { ReferenceLayer, ReferencePosition } from './api';
import { referenceGeometryPaths } from './referenceGeometry';
import { closedRing, studyMetadata, studyZones, studyZoneName } from './zoningStudy';
import { zoningAnchor, type ZoningOverlay } from './zoningLabels';
import { GlobeZoningLabels } from './GlobeZoningLabels';

const NO_HIT = () => {};
const RAD = Math.PI / 180;

/** Cartographic outlines, independent of proposal geometry and Google tile masks.
 * Depth testing is disabled deliberately: zoning is an inspectable map overlay,
 * not a terrain/height assertion. Third coordinates remain in the stored data.
 * The whole group is excluded from scene renders and never intercepts drawing.
 */
export function GlobeReferenceLayer({ layers, terrainHeight }: { layers: ReferenceLayer[]; terrainHeight: number }) {
  return <group name="reference-overlays" userData={DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA}>
    {layers.map((layer) => studyMetadata(layer)
      ? <StudyOverlay key={layer.id} layer={layer} terrainHeight={terrainHeight} />
      : <ReferenceOutline key={layer.id} layer={layer} terrainHeight={terrainHeight} />)}
  </group>;
}

function StudyOverlay({ layer, terrainHeight }: { layer: ReferenceLayer; terrainHeight: number }) {
  const data = useMemo<ZoningOverlay>(() => ({ bounds: layer.bounds, loadedAt: layer.created_at,
    districts: studyZones(layer).flatMap(zone => {
      const anchor = zoningAnchor(zone.rings);
      return anchor ? [{ id: zone.id, label: studyZoneName(zone), anchor, polygon: zone.rings, color: zone.color }] : [];
    }),
  }), [layer.bounds, layer.created_at, layer.feature_collection]);
  const boundary = useMemo<ZoningOverlay>(() => {
    const points = studyMetadata(layer)?.boundaryCoordinates ?? [];
    return { bounds: layer.bounds, loadedAt: layer.created_at, districts: points.length < 3 ? [] : [
      { id: 'study-site-boundary', label: '', anchor: points[0], polygon: [closedRing(points)] },
    ] };
  }, [layer.bounds, layer.created_at, layer.feature_collection]);
  return <group name={`study-layer:${layer.id}`}>
    <GlobeZoningLabels data={data} terrainHeight={terrainHeight} enabled labels lines fill fillOpacity={layer.opacity} />
    <GlobeZoningLabels data={boundary} terrainHeight={terrainHeight} enabled labels={false} lines fill={false} fillOpacity={0} />
  </group>;
}

function ReferenceOutline({ layer, terrainHeight }: { layer: ReferenceLayer; terrainHeight: number }) {
  const latitude = (layer.bounds[1] + layer.bounds[3]) * 0.5 * RAD;
  const longitude = (layer.bounds[0] + layer.bounds[2]) * 0.5 * RAD;
  const height = Number.isFinite(terrainHeight) ? terrainHeight + 1 : 1;
  const isStudy = Boolean(studyMetadata(layer));
  const geometries = useMemo(() => {
    const origin = new THREE.Vector3();
    const east = new THREE.Vector3();
    const north = new THREE.Vector3();
    const up = new THREE.Vector3();
    WGS84_ELLIPSOID.getCartographicToPosition(latitude, longitude, height, origin);
    WGS84_ELLIPSOID.getEastNorthUpAxes(latitude, longitude, east, north, up);
    const world = new THREE.Vector3();
    const local = (position: ReferencePosition): number[] => {
      WGS84_ELLIPSOID.getCartographicToPosition(position[1] * RAD, position[0] * RAD, height, world);
      world.sub(origin);
      return [world.dot(east), world.dot(north), world.dot(up)];
    };
    const lines: number[] = [];
    const points: number[] = [];
    const triangles: number[] = [];
    const colors: number[] = [];
    for (const feature of layer.feature_collection.features) {
      const paths = referenceGeometryPaths(feature.geometry);
      for (const path of paths.lines) {
        for (let index = 1; index < path.length; index++) lines.push(...local(path[index - 1]), ...local(path[index]));
      }
      for (const point of paths.points) points.push(...local(point));
      if (isStudy && feature.geometry.type === 'Polygon') {
        const rings = feature.geometry.coordinates.map(ring => {
          const closed = ring.length > 1 && ring[0][0] === ring[ring.length-1][0] && ring[0][1] === ring[ring.length-1][1];
          return (closed ? ring.slice(0,-1) : ring).map(local);
        });
        if (rings[0]?.length >= 3) {
          const contour = rings[0].map(([x,y]) => new THREE.Vector2(x,y));
          const holes = rings.slice(1).map(ring => ring.map(([x,y]) => new THREE.Vector2(x,y)));
          const vertices = rings.flat();
          const color = new THREE.Color(/^#[\da-f]{6}$/i.test(String(feature.properties.color)) ? String(feature.properties.color) : layer.color);
          for (const face of THREE.ShapeUtils.triangulateShape(contour,holes)) for (const index of face) {
            triangles.push(...vertices[index]); colors.push(color.r,color.g,color.b);
          }
        }
      }
    }
    const lineGeometry = new THREE.BufferGeometry();
    lineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(lines, 3));
    const pointGeometry = new THREE.BufferGeometry();
    pointGeometry.setAttribute('position', new THREE.Float32BufferAttribute(points, 3));
    const fillGeometry = new THREE.BufferGeometry();
    fillGeometry.setAttribute('position', new THREE.Float32BufferAttribute(triangles,3));
    fillGeometry.setAttribute('color', new THREE.Float32BufferAttribute(colors,3));
    return { lineGeometry, pointGeometry, fillGeometry };
  }, [height, latitude, isStudy, layer.color, layer.feature_collection, longitude]);
  useEffect(() => retainResourceForDeferredDisposal(geometries, (value) => {
    value.lineGeometry.dispose();
    value.pointGeometry.dispose();
    value.fillGeometry.dispose();
  }), [geometries]);
  return <EastNorthUpFrame lat={latitude} lon={longitude} height={height}>
    {geometries.fillGeometry.attributes.position.count > 0 && <mesh geometry={geometries.fillGeometry} raycast={NO_HIT} renderOrder={988} frustumCulled={false}>
      <meshBasicMaterial vertexColors transparent opacity={0.35 * layer.opacity} side={THREE.DoubleSide} depthTest={false} depthWrite={false} toneMapped={false}/>
    </mesh>}
    <lineSegments geometry={geometries.lineGeometry} raycast={NO_HIT} renderOrder={990} frustumCulled={false}>
      <lineBasicMaterial color={layer.color} opacity={layer.opacity} transparent depthTest={false} depthWrite={false} toneMapped={false} />
    </lineSegments>
    <points geometry={geometries.pointGeometry} raycast={NO_HIT} renderOrder={991} frustumCulled={false}>
      <pointsMaterial color={layer.color} size={7} sizeAttenuation={false} opacity={layer.opacity} transparent depthTest={false} depthWrite={false} toneMapped={false} />
    </points>
  </EastNorthUpFrame>;
}
