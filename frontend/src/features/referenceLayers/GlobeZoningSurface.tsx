import { useEffect, useLayoutEffect, useMemo } from 'react';
import { useThree } from '@react-three/fiber';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import * as THREE from 'three';
import { LineSegments2 } from 'three/examples/jsm/lines/LineSegments2.js';
import { LineSegmentsGeometry } from 'three/examples/jsm/lines/LineSegmentsGeometry.js';
import { LineMaterial } from 'three/examples/jsm/lines/LineMaterial.js';
import { retainResourceForDeferredDisposal } from '@/components/viewer/globe/strictModeResourceDisposal';
import { zoningSurfaceGeometry } from './zoningSurfaceGeometry';
import type { ZoningOverlay } from './zoningLabels';

const NO_HIT = () => {};

export function GlobeZoningSurface({ data, terrainHeight, lines, fill, fillOpacity }: {
  data: ZoningOverlay; terrainHeight: number; lines: boolean; fill: boolean; fillOpacity: number;
}) {
  const size = useThree(state => state.size);
  const resources = useMemo(() => {
    const geometry = zoningSurfaceGeometry(data, terrainHeight);
    const lineGeometry = new LineSegmentsGeometry();
    if (geometry.lines.length) lineGeometry.setPositions(geometry.lines);
    const material = new THREE.MeshBasicMaterial({ vertexColors: true, transparent: true, side: THREE.DoubleSide, depthTest: false, depthWrite: false, toneMapped: false });
    const halo = new LineMaterial({ color: '#fffbee', linewidth: 2.8, transparent: true, opacity: 0.7, depthTest: false, depthWrite: false, toneMapped: false });
    const edge = new LineMaterial({ color: '#3d403a', linewidth: 1.15, transparent: true, opacity: 0.95, depthTest: false, depthWrite: false, toneMapped: false });
    const mesh = new THREE.Mesh(geometry.fill, material);
    const casing = new LineSegments2(lineGeometry, halo), outline = new LineSegments2(lineGeometry, edge);
    mesh.name = 'calgary-land-use-fill'; casing.name = 'calgary-land-use-boundary-halo'; outline.name = 'calgary-land-use-boundaries';
    for (const [index, object] of [mesh, casing, outline].entries()) {
      object.raycast = NO_HIT; object.frustumCulled = false; object.renderOrder = 988 + index;
    }
    const group = new THREE.Group(); group.name = 'calgary-land-use-surface';
    group.add(mesh, casing, outline);
    return { ...geometry, lineGeometry, material, halo, edge, mesh, casing, outline, group };
  }, [data, terrainHeight]);
  useLayoutEffect(() => {
    resources.material.opacity = fillOpacity;
    resources.mesh.visible = fill && fillOpacity > 0 && resources.fill.attributes.position.count > 0;
    resources.casing.visible = resources.outline.visible = lines && resources.lines.length > 0;
    resources.halo.resolution.set(size.width, size.height);
    resources.edge.resolution.set(size.width, size.height);
  }, [resources, fill, lines, fillOpacity, size.width, size.height]);
  useEffect(() => retainResourceForDeferredDisposal(resources, value => {
    value.fill.dispose(); value.lineGeometry.dispose();
    value.material.dispose(); value.halo.dispose(); value.edge.dispose();
  }), [resources]);
  return <EastNorthUpFrame lat={resources.lat} lon={resources.lon} height={resources.height}>
    <primitive object={resources.group} />
  </EastNorthUpFrame>;
}
