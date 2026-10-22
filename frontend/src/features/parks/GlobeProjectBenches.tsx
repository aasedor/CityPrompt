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
import { Html } from '@react-three/drei';
import type { SiteZone } from "@/types";
import { DetailModelInstances } from "./DetailModelInstances";
import { PeopleModelInstances } from '@/features/people/PeopleModel';
import type { DetailPlacement } from "./detailInstances";
import { useSharedSiteGround } from "@/components/viewer/globe/SharedSiteGroundProvider";
import { authoredCameraGround } from "@/components/viewer/globe/authoredCameraGround";
import { raycastTerrainHeightAtLatLng } from "@/components/viewer/globe/GlobeZoneLayer";
import { PROJECT_DETAILS_CAPTURE_USER_DATA } from "@/components/viewer/globe/direct3dCapture";
import type { ProjectBench, ProjectTree, ProjectProp } from "./projectBenches";
import { detailAsset } from './detailCatalogue';
import { detailPlacementSupport } from './safetyPlacement';
import { useSafetySurfaceVersion } from './safetySupport';

const NO_PROPS: ProjectProp[] = [];
const NO_TREES: ProjectTree[] = [];
const keyFor = (bench: ProjectBench) => `${bench.id}:${bench.lng}:${bench.lat}`;

/** Shared instances remain visible and pickable while a detail is selected. */
export function GlobeProjectBenches({
  benches,
  trees = NO_TREES,
  props = NO_PROPS,
  zones,
  fallbackHeight,
  editing,
}: {
  benches: ProjectBench[];
  trees?: ProjectTree[];
  props?: ProjectProp[];
  zones: SiteZone[];
  fallbackHeight: number;
  editing?: { id: string; angle: number };
}) {
  const items = useMemo(
    () => [
      ...benches.map((b) => ({ ...b, variant: "timber-bench" as const })),
      ...trees,
      ...props,
    ],
    [benches, trees, props],
  );
  const ground = useSharedSiteGround(),
    tiles = useContext(TilesRendererContext);
  const surfaceVersion=useSafetySurfaceVersion();
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
  const {batches,unsupported} = useMemo(() => {
    // A new registered road snapshot invalidates cached support resolutions.
    void surfaceVersion;
    const groups = new Map<string, DetailPlacement[]>();
    const unsupported:string[]=[];
    for (const b of items) {
      const measured =
        ground.heightAt(b.lng, b.lat) ?? sampled[keyFor(b)] ?? fallbackHeight;
      const asset = detailAsset(b.variant);
      const support=(asset.safety || asset.people)?detailPlacementSupport(b.variant,b,zones.map(zone=>zone.id)):null;
      if(support&&!support.ok){unsupported.push(b.id);continue;}
      const height = support?.ok && support.height!==undefined ? support.height : authoredCameraGround(zones, b.lng, b.lat, measured);
      const group = groups.get(b.variant) ?? [];
      group.push({ ...b, height, angle: editing?.id === b.id ? editing.angle : b.angle });
      groups.set(b.variant, group);
    }
    return {batches:[...groups],unsupported};
  }, [items, ground, sampled, fallbackHeight, zones, surfaceVersion, editing?.id, editing?.angle]);
  return (
    <group
      name="project-details"
      userData={PROJECT_DETAILS_CAPTURE_USER_DATA}
    >
      {unsupported.map(id=><group key={id} userData={{detailSupportUnavailable:true,streetGroundStatus:'unavailable',streetGroundZoneId:`detail:${id}`}}/>)}
      {unsupported.length>0&&<Html fullscreen style={{pointerEvents:'none'}}><div role="alert" style={{position:'absolute',bottom:90,left:280,maxWidth:330,padding:12,background:'#fff7db',color:'#713f12',border:'1px solid #d6a643',borderRadius:10,fontSize:13}}>
        {unsupported.length} safety {unsupported.length===1?'item needs':'items need'} a compatible level road surface. Use Add details → Arrange details to move or remove them. Their saved positions are preserved.
      </div></Html>}
      {batches.map(([asset, placements]) => (
        <Suspense key={asset} fallback={null}>
          {detailAsset(asset).people
            ? <PeopleModelInstances asset={asset} placements={placements} selectedId={editing?.id} />
            : <DetailModelInstances asset={asset} placements={placements} selectedId={editing?.id} />}
        </Suspense>
      ))}
    </group>
  );
}
