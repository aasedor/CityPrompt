import {
  Suspense,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { useFrame } from "@react-three/fiber";
import { EastNorthUpFrame, TilesRendererContext } from "3d-tiles-renderer/r3f";
import { Raycaster } from "three";
import type { SiteZone } from "@/types";
import { RusticDetail } from "@/components/viewer/globe/GlobeNeighborhoodParkPilot";
import { useSharedSiteGround } from "@/components/viewer/globe/SharedSiteGroundProvider";
import { authoredCameraGround } from "@/components/viewer/globe/authoredCameraGround";
import { raycastTerrainHeightAtLatLng } from "@/components/viewer/globe/GlobeZoneLayer";
import { direct3DProposalUserData } from "@/components/viewer/globe/direct3dCapture";
import type { ProjectBench, ProjectTree } from "./projectBenches";

const zeroGround = () => 0;
const NO_TREES: ProjectTree[] = [];
const keyFor = (bench: ProjectBench) => `${bench.id}:${bench.lng}:${bench.lat}`;

/** No scene picking: editing belongs exclusively to the detail editor. */
export function GlobeProjectBenches({
  benches,
  trees = NO_TREES,
  zones,
  fallbackHeight,
}: {
  benches: ProjectBench[];
  trees?: ProjectTree[];
  zones: SiteZone[];
  fallbackHeight: number;
}) {
  const items = useMemo(
    () => [
      ...benches.map((b) => ({ ...b, variant: "timber-bench" as const })),
      ...trees,
    ],
    [benches, trees],
  );
  const ground = useSharedSiteGround(),
    tiles = useContext(TilesRendererContext);
  const [sampled, setSampled] = useState<Record<string, number>>({});
  const next = useRef(0),
    ray = useRef(new Raycaster());
  useEffect(() => {
    next.current = 0;
    setSampled({});
  }, [items]);
  useEffect(() => {
    const reset = () => {
      next.current = 0;
    };
    tiles?.addEventListener("tiles-load-end", reset);
    return () => tiles?.removeEventListener("tiles-load-end", reset);
  }, [tiles]);
  useFrame(() => {
    // At most two terrain probes in a frame; shared prepared ground needs none.
    const batch: Record<string, number> = {};
    for (let n = 0; n < 2 && next.current < items.length; n++) {
      const b = items[next.current++];
      if (ground.heightAt(b.lng, b.lat) !== null) continue;
      const h = tiles?.group
        ? raycastTerrainHeightAtLatLng(b.lng, b.lat, tiles.group, ray.current)
        : null;
      if (h !== null && Number.isFinite(h)) batch[keyFor(b)] = h;
    }
    if (Object.keys(batch).length)
      setSampled((previous) => ({ ...previous, ...batch }));
  });
  return (
    <group
      name="project-details"
      userData={direct3DProposalUserData("landscape")}
    >
      {items.map((b) => {
        const measured =
          ground.heightAt(b.lng, b.lat) ?? sampled[keyFor(b)] ?? fallbackHeight;
        const height = authoredCameraGround(zones, b.lng, b.lat, measured);
        return (
          <EastNorthUpFrame
            key={b.id}
            lat={(b.lat * Math.PI) / 180}
            lon={(b.lng * Math.PI) / 180}
            height={height}
          >
            <Suspense fallback={null}>
              <RusticDetail
                asset={b.variant}
                point={{ x: 0, y: 0 }}
                yaw={(b.angle * Math.PI) / 180}
                terrainZ={zeroGround}
                ignorePicking
              />
            </Suspense>
          </EastNorthUpFrame>
        );
      })}
    </group>
  );
}
