import { useContext, useEffect, useMemo, useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { EastNorthUpFrame, TilesRendererContext } from "3d-tiles-renderer/r3f";
import { DoubleSide, Raycaster } from "three";
import { useSharedSiteGround } from "@/components/viewer/globe/SharedSiteGroundProvider";
import { raycastTerrainHeightAtLatLng } from "@/components/viewer/globe/GlobeZoneLayer";
import { DIRECT_3D_CAPTURE_CONTEXT_USER_DATA } from "@/components/viewer/globe/direct3dCapture";
import { pavingGroundHeights } from "./pavingGround";
import { createStreetSurfaceAlbedoTexture } from "@/components/viewer/globe/streetSurfaceMaterials";
import type { SiteZone } from "@/types";
import {
  pavingGeometry,
  PAVING_MATERIALS,
  type PavingSurface,
} from "./pavingSurfaces";

const pointKey = (p: number[]) => `${p[0]}:${p[1]}`;
function Surface({
  surface,
  heights,
}: {
  surface: PavingSurface;
  heights: number[];
}) {
  const geometry = useMemo(
    () => pavingGeometry(surface.coordinates, heights),
    [surface.coordinates, heights],
  );
  useEffect(() => () => geometry.dispose(), [geometry]);
  const texture = useMemo(
    () =>
      createStreetSurfaceAlbedoTexture(
        surface.material === "brick" ? "unit_pavers" : surface.material,
        { size: 128, seed: "project-paving", anisotropy: 4 },
      ),
    [surface.material],
  );
  useEffect(() => () => texture.dispose(), [texture]);
  const [lng, lat] = surface.coordinates[0];
  return (
    <EastNorthUpFrame
      lat={(lat * Math.PI) / 180}
      lon={(lng * Math.PI) / 180}
      height={heights[0]}
    >
      <mesh
        geometry={geometry}
        renderOrder={103}
        raycast={() => {}}
        receiveShadow
      >
        <meshStandardMaterial
          color={
            surface.material === "brick"
              ? PAVING_MATERIALS.brick.color
              : "#ffffff"
          }
          map={texture}
          roughness={0.95}
          side={DoubleSide}
          polygonOffset
          polygonOffsetFactor={-2}
          polygonOffsetUnits={-2}
        />
      </mesh>
    </EastNorthUpFrame>
  );
}

/** No selection or obstruction: a thin surface treatment, not new terrain. */
export function GlobePavingSurfaces({
  surfaces,
  fallbackHeight,
  zones,
}: {
  surfaces: PavingSurface[];
  fallbackHeight: number;
  zones: SiteZone[];
}) {
  const ground = useSharedSiteGround(),
    tiles = useContext(TilesRendererContext);
  const points = useMemo(
    () => [
      ...new Map(
        surfaces.flatMap((s) => s.coordinates).map((p) => [pointKey(p), p]),
      ).values(),
    ],
    [surfaces],
  );
  const [sampled, setSampled] = useState<Record<string, number>>({});
  const next = useRef(0),
    ray = useRef(new Raycaster());
  useEffect(() => {
    next.current = 0;
    setSampled({});
  }, [points]);
  useEffect(() => {
    const reset = () => {
      next.current = 0;
    };
    tiles?.addEventListener("tiles-load-end", reset);
    return () => tiles?.removeEventListener("tiles-load-end", reset);
  }, [tiles]);
  useFrame(() => {
    const batch: Record<string, number> = {};
    for (let n = 0; n < 2 && next.current < points.length; n++) {
      const p = points[next.current++];
      if (ground.heightAt(p[0], p[1]) !== null) continue;
      const height = tiles?.group
        ? raycastTerrainHeightAtLatLng(p[0], p[1], tiles.group, ray.current)
        : null;
      if (height !== null && Number.isFinite(height))
        batch[pointKey(p)] = height;
    }
    if (Object.keys(batch).length) setSampled((old) => ({ ...old, ...batch }));
  });
  const layouts = useMemo(
    () =>
      surfaces.map((surface) => ({
        surface,
        heights: pavingGroundHeights(
          surface.coordinates,
          zones,
          (p) =>
            ground.heightAt(p[0], p[1]) ??
            sampled[pointKey(p)] ??
            fallbackHeight,
        ),
      })),
    [surfaces, ground, sampled, fallbackHeight, zones],
  );
  return (
    <group
      name="project-paving"
      // Metadata-authored surfaces stay visible, but are not zone instances.
      userData={DIRECT_3D_CAPTURE_CONTEXT_USER_DATA}
    >
      {layouts.map((p) => (
        <Surface key={p.surface.id} {...p} />
      ))}
    </group>
  );
}
