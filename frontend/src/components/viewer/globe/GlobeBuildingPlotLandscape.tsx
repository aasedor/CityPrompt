import { useEffect, useMemo } from 'react';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import * as THREE from 'three';
import type { MultiPolygon } from 'polygon-clipping';
import type { SiteZone } from '@/types';
import { buildingPlotLandscapes, type BuildingPlotLandscape } from './buildingPlotLandscape';
import { createSitePreparationTexture } from './sitePreparationSurface';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';
import { direct3DInstanceUserData, direct3DProposalUserData, direct3DZoneInstanceDescriptor } from './direct3dCapture';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { residualLandscapeBounds } from './residualLandscape';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '../mapEngine/geoUtils';

function surfaceGeometry(polygons: MultiPolygon, height: number) {
  const shapes = polygons.map(([outer, ...holes]) => {
    const shape = new THREE.Shape(outer.map(p => new THREE.Vector2(...p)));
    shape.holes = holes.map(ring => new THREE.Path(ring.map(p => new THREE.Vector2(...p))));
    return shape;
  });
  const geometry = new THREE.ShapeGeometry(shapes);
  geometry.translate(0, 0, height);
  const positions = geometry.getAttribute('position'), uv = geometry.getAttribute('uv');
  for (let i = 0; i < positions.count; i++) uv.setXY(i, positions.getX(i) / 6, positions.getY(i) / 6);
  return geometry;
}

function PlotGarden({ plan, boundary }: { plan: BuildingPlotLandscape; boundary: SiteZone }) {
  const resources = useMemo(() => {
    const surface = surfaceGeometry(plan.surface, .035), beds = surfaceGeometry(plan.beds, .043);
    // Uncompiled sites use the boundary's exact texture and geographic phase.
    // Compiled sites already paint through lots; no second lawn covers that surface.
    const texture = createSitePreparationTexture(boundary.id, 256, 'grass');
    const bounds = residualLandscapeBounds(boundary.coordinates);
    const spanX = (bounds.east - bounds.west) * metersPerDegLon(plan.origin[1]);
    const spanY = (bounds.north - bounds.south) * METERS_PER_DEG_LAT;
    const repeatsX = Math.max(4, spanX / Math.max(.01, Math.min(spanX, spanY)) * 4);
    const repeatsY = Math.max(4, spanY / Math.max(.01, Math.min(spanX, spanY)) * 4);
    const pos = surface.getAttribute('position'), uv = surface.getAttribute('uv');
    for (let i = 0; i < pos.count; i++) uv.setXY(i,
      ((plan.origin[0] - bounds.west) * metersPerDegLon(plan.origin[1]) + pos.getX(i)) / Math.max(.01, spanX) * repeatsX,
      ((plan.origin[1] - bounds.south) * METERS_PER_DEG_LAT + pos.getY(i)) / Math.max(.01, spanY) * repeatsY);
    const flowers = plan.design.planting === 'flowering' || plan.design.planting === 'mixed';
    const grasses = plan.design.planting === 'grasses';
    const shrubGeometry = new THREE.IcosahedronGeometry(1, 1);
    const shrubMaterial = new THREE.MeshStandardMaterial({ roughness: 1 });
    const shrubs = new THREE.InstancedMesh(shrubGeometry, shrubMaterial, plan.shrubs.length * (flowers ? 4 : 3));
    shrubs.name = 'building-garden-low-planting';
    shrubs.raycast = () => {};
    const matrix = new THREE.Matrix4(), rotation = new THREE.Quaternion();
    let instance = 0;
    for (const [x, y] of plan.shrubs) {
      const lobes = [[-.12, 0, .20], [.13, .06, .22], [0, -.12, .29]];
      for (const [j, p] of lobes.entries()) {
        shrubs.setMatrixAt(instance, matrix.compose(new THREE.Vector3(x + p[0], y + p[1], grasses ? .28 : p[2]), rotation,
          grasses ? new THREE.Vector3(.12, .1, .25) : new THREE.Vector3(.25, .23, .21)));
        shrubs.setColorAt(instance++, new THREE.Color(plan.design.foliage).multiplyScalar(j === 1 ? 1.1 : .85));
      }
      if (flowers) {
        shrubs.setMatrixAt(instance, matrix.compose(new THREE.Vector3(x + .06, y - .02, .475), rotation, new THREE.Vector3(.13, .12, .08)));
        shrubs.setColorAt(instance++, new THREE.Color(plan.style === 'civic' ? '#af9ab6' : '#dedac0'));
      }
    }
    shrubs.computeBoundingSphere();
    return { surface, beds, texture, shrubs, shrubGeometry, shrubMaterial };
  }, [plan, boundary]);
  useEffect(() => retainResourceForDeferredDisposal(resources, r => {
    r.surface.dispose(); r.beds.dispose(); r.texture.dispose(); r.shrubs.dispose(); r.shrubGeometry.dispose(); r.shrubMaterial.dispose();
  }), [resources]);
  return <EastNorthUpFrame lat={plan.origin[1] * Math.PI / 180} lon={plan.origin[0] * Math.PI / 180} height={plan.height}>
    <group name={`building-plot-landscape-${plan.zoneId}`} userData={{ buildingPlotLandscape: plan.style, landscapeDesign: plan.design,
      ...direct3DProposalUserData('landscape'),
      ...direct3DInstanceUserData(direct3DZoneInstanceDescriptor(plan.zoneId, 'landscape')) }}>
      {plan.drawSurface && <mesh geometry={resources.surface} renderOrder={102} raycast={() => null}>
        <meshStandardMaterial map={resources.texture} roughness={1} />
      </mesh>}
      {plan.beds.length > 0 && <mesh geometry={resources.beds} renderOrder={103} raycast={() => null}>
        <meshStandardMaterial color={plan.design.bed} roughness={1}/>
      </mesh>}
      {/* A dispose prop on this primitive would overwrite InstancedMesh.dispose.
          The effect above owns its buffers and geometry. */}
      {plan.shrubs.length > 0 && <primitive object={resources.shrubs}/>}
    </group>
  </EastNorthUpFrame>;
}

/** Model-owned landscaping remains visible in clean captures. It uses the same
 * prepared datum as the building and never raycasts roofs or changes terrain. */
export function GlobeBuildingPlotLandscape({ zones, terrainHeight }: { zones: SiteZone[]; terrainHeight: number }) {
  const plans = useMemo(() => buildingPlotLandscapes(zones, terrainHeight), [zones, terrainHeight]);
  const boundary = getActiveSiteBoundary(zones);
  return boundary ? <>{plans.map(plan => <PlotGarden key={plan.zoneId} plan={plan} boundary={boundary}/>)}</> : null;
}
