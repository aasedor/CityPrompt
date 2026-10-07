import { useEffect, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA } from '@/components/viewer/globe/direct3dCapture';
import { retainResourceForDeferredDisposal } from '@/components/viewer/globe/strictModeResourceDisposal';
import type { ZoningOverlay } from './zoningLabels';
import { GlobeZoningSurface } from './GlobeZoningSurface';
import type { ZoningPreferences } from './zoningAppearance';

const NO_HIT = () => {};
const RAD = Math.PI / 180;

/** Display-only cartography: excluded from captures, raycasting and terrain masks. */
type Props = ZoningPreferences & { data?: ZoningOverlay; terrainHeight: number };

export function GlobeZoningLabels(props: Props) {
  // Off removes the entire overlay, including its per-frame label work.
  return props.enabled && props.data ? <ActiveZoningMap {...props} data={props.data} /> : null;
}

function ActiveZoningMap({ data, labels, lines, fill, fillOpacity, terrainHeight }: Props & { data: ZoningOverlay }) {
  const sprites = useMemo(() => {
    const group = new THREE.Group();
    group.name = 'zoning-labels';
    group.userData = DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA;
    if (!data || !labels) return group;
    for (const district of data.districts) {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      if (!context) continue;
      // Draw at 2x resolution; keep the label's size stable as the camera moves.
      context.font = '600 26px Inter, system-ui, sans-serif';
      const labelLines: string[] = [];
      for (const code of district.label.split(' / ')) {
        const last = labelLines.length - 1;
        const combined = last >= 0 ? `${labelLines[last]} / ${code}` : code;
        if (last >= 0 && context.measureText(combined).width <= 340) labelLines[last] = combined;
        else labelLines.push(code);
      }
      canvas.width = Math.ceil(Math.max(...labelLines.map(line => context.measureText(line).width))) + 28;
      canvas.height = labelLines.length * 32 + 16;
      // Planning-map lettering with a fine paper halo. No floating pin/badge
      // background: the district colour and the Google context carry the map.
      context.font = '600 26px Inter, system-ui, sans-serif';
      context.textAlign = 'center'; context.textBaseline = 'middle'; context.fillStyle = '#23362e';
      context.strokeStyle = 'rgba(255,253,242,0.96)'; context.lineWidth = 4; context.lineJoin = 'round';
      labelLines.forEach((line, index) => {
        const y = 24 + index * 32;
        context.strokeText(line, canvas.width / 2, y);
        context.fillText(line, canvas.width / 2, y);
      });
      const texture = new THREE.CanvasTexture(canvas);
      texture.colorSpace = THREE.SRGBColorSpace;
      const material = new THREE.SpriteMaterial({ map: texture, depthTest: false, depthWrite: false, toneMapped: false });
      const sprite = new THREE.Sprite(material);
      sprite.name = `district-label:${district.id}:${district.label}`;
      sprite.userData = { widthPx: canvas.width / 2, heightPx: canvas.height / 2 };
      sprite.raycast = NO_HIT;
      sprite.renderOrder = 995;
      WGS84_ELLIPSOID.getCartographicToPosition(district.anchor[1] * RAD, district.anchor[0] * RAD, (Number.isFinite(terrainHeight) ? terrainHeight : 0) + 2, sprite.position);
      group.add(sprite);
    }
    return group;
  }, [data, labels, terrainHeight]);
  useEffect(() => retainResourceForDeferredDisposal(sprites, group => {
    for (const child of group.children) {
      const material = (child as THREE.Sprite).material;
      material.map?.dispose(); material.dispose();
    }
  }), [sprites]);
  const projected = useMemo(() => new THREE.Vector3(), []);
  const cameraLocal = useMemo(() => new THREE.Vector3(), []);
  useFrame(({ camera, size }) => {
    // Screen-space collision cells keep dense blocks readable when zoomed out.
    const occupied = new Set<string>();
    for (const child of sprites.children) {
      cameraLocal.copy(child.position).applyMatrix4(camera.matrixWorldInverse);
      projected.copy(child.position).project(camera);
      child.visible = cameraLocal.z < 0 && projected.z >= -1 && projected.z <= 1 && Math.abs(projected.x) < 1 && Math.abs(projected.y) < 1;
      if (!child.visible) continue;
      const { widthPx, heightPx } = child.userData;
      const x = (projected.x + 1) * size.width / 2, y = (projected.y + 1) * size.height / 2;
      const cells: string[] = [];
      for (let ix = Math.floor((x - widthPx / 2 - 3) / 24); ix <= Math.floor((x + widthPx / 2 + 3) / 24); ix++) {
        for (let iy = Math.floor((y - heightPx / 2 - 3) / 24); iy <= Math.floor((y + heightPx / 2 + 3) / 24); iy++) cells.push(`${ix}:${iy}`);
      }
      if (cells.some(cell => occupied.has(cell))) { child.visible = false; continue; }
      cells.forEach(cell => occupied.add(cell));
      const unitsPerPixel = camera instanceof THREE.PerspectiveCamera
        ? 2 * -cameraLocal.z / camera.projectionMatrix.elements[5] / size.height
        : 2 / camera.projectionMatrix.elements[5] / size.height;
      child.scale.set(widthPx * unitsPerPixel, heightPx * unitsPerPixel, 1);
    }
  });
  return <group name="zoning-label-overlay" userData={DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA}>
    <GlobeZoningSurface data={data} terrainHeight={terrainHeight} lines={lines} fill={fill} fillOpacity={fillOpacity} />
    <primitive object={sprites} />
  </group>;
}
