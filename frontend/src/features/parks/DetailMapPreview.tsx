import { Suspense, useEffect, useState } from 'react';
import { useThree } from '@react-three/fiber';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import type { SiteZone } from '@/types';
import { DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA } from '@/components/viewer/globe/direct3dCapture';
import { useSharedSiteGround } from '@/components/viewer/globe/SharedSiteGroundProvider';
import { authoredCameraGround } from '@/components/viewer/globe/authoredCameraGround';
import { detailAsset } from './detailCatalogue';
import { DetailModelInstances } from './DetailModelInstances';
import type { useDetailPlacement } from './useDetailPlacement';

export type DetailInteraction = ReturnType<typeof useDetailPlacement>;

export function DetailMapPreview({ interaction, zones, surfaceAt, fallbackHeight }: {
  interaction: DetailInteraction; zones: SiteZone[];
  fallbackHeight: number;
  surfaceAt: (x: number, y: number) => { lngLat: [number, number]; height: number } | null;
}) {
  const canvas = useThree(state => state.gl.domElement);
  const ground = useSharedSiteGround();
  const [hover, setHover] = useState<{ lngLat: [number, number]; height: number } | null>(null);
  const follows = Boolean(interaction.selected || interaction.moving);
  useEffect(() => {
    setHover(null);
    if (!follows) return;
    let frame = 0;
    const move = (event: PointerEvent) => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const rect = canvas.getBoundingClientRect();
        setHover(surfaceAt((event.clientX - rect.left) / rect.width * 2 - 1,
          -(event.clientY - rect.top) / rect.height * 2 + 1));
      });
    };
    const leave = () => { cancelAnimationFrame(frame); setHover(null); };
    canvas.addEventListener('pointermove', move); canvas.addEventListener('pointerleave', leave);
    return () => { cancelAnimationFrame(frame); canvas.removeEventListener('pointermove', move); canvas.removeEventListener('pointerleave', leave); };
  }, [canvas, follows, surfaceAt]);
  const item = interaction.editing;
  const asset = interaction.selected ?? item?.variant;
  const point = follows ? hover : item ? { lngLat: [item.lng, item.lat] as [number, number], height: fallbackHeight } : null;
  if (!asset || !point) return null;
  const [lng, lat] = point.lngLat;
  const height = authoredCameraGround(zones, lng, lat, ground.heightAt(lng, lat) ?? point.height);
  const radius = Math.max(0.7, detailAsset(asset).dimensions[0] / 2);
  return <group userData={DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA}>
    {/* An existing edited object stays in captures; an unplaced cursor ghost does not. */}
    <group userData={item ? {} : DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA}>
      <Suspense fallback={null}><DetailModelInstances asset={asset} placements={[{ id: 'detail-preview:cursor', lng, lat, height, angle: interaction.angle }]} /></Suspense>
    </group>
    <group userData={DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA}>
      <EastNorthUpFrame lat={lat * Math.PI / 180} lon={lng * Math.PI / 180} height={height + 0.12}>
        <mesh raycast={() => {}} renderOrder={10000}><ringGeometry args={[radius, radius + 0.1, 40]} /><meshBasicMaterial color="#caff34" depthTest={false} depthWrite={false} side={2} /></mesh>
      </EastNorthUpFrame>
    </group>
  </group>;
}
