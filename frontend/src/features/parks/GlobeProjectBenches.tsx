import {
  Suspense,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { useFrame } from "@react-three/fiber";
import { TilesRendererContext } from "3d-tiles-renderer/r3f";
import { Raycaster } from "three";
import type { SiteZone } from "@/types";
import { DetailModelInstances } from "./DetailModelInstances";
import type { DetailPlacement } from "./detailInstances";
import { useSharedSiteGround } from "@/components/viewer/globe/SharedSiteGroundProvider";
import { authoredCameraGround } from "@/components/viewer/globe/authoredCameraGround";
import { raycastTerrainHeightAtLatLng } from "@/components/viewer/globe/GlobeZoneLayer";
import { DIRECT_3D_CAPTURE_CONTEXT_USER_DATA } from "@/components/viewer/globe/direct3dCapture";
import type { ProjectBench, ProjectTree, ProjectProp } from "./projectBenches";

const NO_PROPS: ProjectProp[] = [];
const NO_TREES: ProjectTree[] = [];
const keyFor = (bench: ProjectBench) => `${bench.id}:${bench.lng}:${bench.lat}`;

/** No scene picking: editing belongs exclusively to the detail editor. */
export function GlobeProjectBenches({
  benches,
  trees = NO_TREES,
  props = NO_PROPS,
  zones,
  fallbackHeight,
  hiddenId,
}: {
  benches: ProjectBench[];
  trees?: ProjectTree[];
  props?: ProjectProp[];
  zones: SiteZone[];
  fallbackHeight: number;
  hiddenId?: string;
}) {
  const items = useMemo(
    () => [
      ...benches.map((b) => ({ ...b, variant: "timber-bench" as const })),
      ...trees,
      ...props,
    ].filter(item => item.id !== hiddenId),
    [benches, trees, props, hiddenId],
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
  const batches = useMemo(() => {
    const groups = new Map<string, DetailPlacement[]>();
    for (const b of items) {
      const measured =
        ground.heightAt(b.lng, b.lat) ?? sampled[keyFor(b)] ?? fallbackHeight;
      const height = authoredCameraGround(zones, b.lng, b.lat, measured);
      const group = groups.get(b.variant) ?? [];
      group.push({ ...b, height });
      groups.set(b.variant, group);
    }
    return [...groups];
  }, [items, ground, sampled, fallbackHeight, zones]);
  return (
    <group
      name="project-details"
      userData={DIRECT_3D_CAPTURE_CONTEXT_USER_DATA}
    >
      {batches.map(([asset, placements]) => (
        <Suspense key={asset} fallback={null}>
          <DetailModelInstances asset={asset} placements={placements} />
        </Suspense>
      ))}
    </group>
  );
}
