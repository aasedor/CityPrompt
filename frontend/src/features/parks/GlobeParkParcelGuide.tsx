import { useMemo } from "react";
import { Line } from "@react-three/drei";
import { EastNorthUpFrame } from "3d-tiles-renderer/r3f";
import { useSharedSiteGround } from "@/components/viewer/globe/SharedSiteGroundProvider";
import {
  metersPerDegLon,
  METERS_PER_DEG_LAT,
} from "@/components/viewer/mapEngine/geoUtils";
import type { SiteZone } from "@/types";
import { resolvePreparedSiteTerrainForZone } from "@/components/viewer/globe/sitePreparationSurface";
import { DIRECT_3D_CAPTURE_EXCLUDE_KEY } from "@/components/viewer/globe/direct3dCapture";
import { nativeParkFootprint, readNativePark } from "./nativeParkRegistry";

/** Editing guide only, excluded during walking and captures by its caller. */
export function GlobeParkParcelGuide({
  zone,
  zones,
  fallbackHeight,
}: {
  zone: SiteZone;
  zones: SiteZone[];
  fallbackHeight: number;
}) {
  const ground = useSharedSiteGround();
  const guide = useMemo(() => {
    const native = readNativePark(zone);
    if (!native) return null;
    const { longitude: lng, latitude: lat } = native.selection.frame;
    const points = (ring: number[][]): [number, number, number][] =>
      [...ring, ring[0]].map((p) => [
        (p[0] - lng) * metersPerDegLon(lat),
        (p[1] - lat) * METERS_PER_DEG_LAT,
        0.15,
      ]);
    return {
      lng,
      lat,
      parcel: points(zone.coordinates),
      layout: points(nativeParkFootprint(native.selection, native.layout)),
    };
  }, [zone]);
  if (!guide) return null;
  return (
    <EastNorthUpFrame
      lat={(guide.lat * Math.PI) / 180}
      lon={(guide.lng * Math.PI) / 180}
      height={
        resolvePreparedSiteTerrainForZone(
          zone,
          zones,
          ground.heightAt(guide.lng, guide.lat) ?? fallbackHeight,
        ) ?? fallbackHeight
      }
    >
      <group
        name="park-parcel-edit-guide"
        userData={{ [DIRECT_3D_CAPTURE_EXCLUDE_KEY]: true }}
        renderOrder={10000}
      >
        <Line
          points={guide.parcel}
          color="#f59e0b"
          lineWidth={3}
          dashed
          dashSize={2}
          gapSize={1}
          depthTest={false}
          depthWrite={false}
          transparent
          raycast={() => {}}
        />
        <Line
          points={guide.layout}
          color="#067a66"
          lineWidth={3}
          depthTest={false}
          depthWrite={false}
          transparent
          raycast={() => {}}
        />
      </group>
    </EastNorthUpFrame>
  );
}
