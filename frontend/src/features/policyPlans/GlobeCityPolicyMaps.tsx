import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
} from "react";
import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { WGS84_ELLIPSOID } from "3d-tiles-renderer";
import { DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA } from "@/components/viewer/globe/direct3dCapture";
import { retainResourceForDeferredDisposal } from "@/components/viewer/globe/strictModeResourceDisposal";
import { CITY_PLAN_ASSETS, type PlanTile } from "./citywidePlans";
import type { CityPolicyMapsState } from "./useCityPolicyMaps";
import { cityPlanTileGeometry, opaqueMapPixel } from "./cityPlanGeometry";

export type CityPolicyMapHandle = {
  pick: (x: number, y: number, camera: THREE.Camera) => string | null;
};
export type GlobeCityPolicyProps = Pick<
  CityPolicyMapsState,
  | "layers"
  | "imageFailed"
  | "retryVersion"
  | "inspect"
  | "selected"
  | "clearSelection"
>;
const NO_HIT = () => {};

export const GlobeCityPolicyMaps = forwardRef<
  CityPolicyMapHandle,
  GlobeCityPolicyProps & { terrainHeight: number }
>(function GlobeCityPolicyMaps(
  { layers, terrainHeight, imageFailed, retryVersion },
  ref,
) {
  const group = useRef<THREE.Group>(null);
  const raycaster = useMemo(() => new THREE.Raycaster(), []);
  const pixel = useMemo(() => {
    const canvas = document.createElement("canvas");
    canvas.width = canvas.height = 1;
    return canvas.getContext("2d", { willReadFrequently: true });
  }, []);
  useImperativeHandle(
    ref,
    () => ({
      pick: (x, y, camera) => {
        if (!group.current || !pixel) return null;
        raycaster.setFromCamera(new THREE.Vector2(x, y), camera);
        const hits: THREE.Intersection<THREE.Object3D>[] = [];
        group.current.updateWorldMatrix(true, true);
        group.current.traverse((object) => {
          if (
            !(object instanceof THREE.Mesh) ||
            !object.visible ||
            !object.userData.cityPolicyId
          )
            return;
          for (
            let parent: THREE.Object3D | null = object;
            parent;
            parent = parent.parent
          )
            if (!parent.visible) return;
          THREE.Mesh.prototype.raycast.call(object, raycaster, hits);
        });
        // Match the displayed layer stack, not distance to Google buildings beneath.
        hits.sort(
          (a, b) =>
            b.object.renderOrder - a.object.renderOrder ||
            a.distance - b.distance,
        );
        for (const hit of hits) {
          const material = (hit.object as THREE.Mesh)
            .material as THREE.MeshBasicMaterial;
          const image = material.map?.image as HTMLImageElement | undefined;
          if (
            hit.uv &&
            image &&
            material.opacity > 0 &&
            opaqueMapPixel(image, hit.uv, pixel)
          )
            return hit.object.userData.cityPolicyId as string;
        }
        return null;
      },
    }),
    [pixel, raycaster],
  );
  return (
    <group
      ref={group}
      name="city-policy-maps"
      userData={DIRECT_3D_CAPTURE_EXCLUDE_USER_DATA}
    >
      {layers.map(
        (layer, index) =>
          layer.enabled &&
          layer.opacity > 0 &&
          layer.data && (
            <RasterMap
              key={`${layer.map.id}:${retryVersion[layer.map.id] ?? 0}`}
              layer={layer}
              terrainHeight={terrainHeight}
              order={970 + index}
              onError={imageFailed}
            />
          ),
      )}
    </group>
  );
});

function useMapTexture(
  url: string | undefined,
  mapId: string,
  onError: (id: string) => void,
) {
  const [loaded, setLoaded] = useState<{
    url: string;
    texture: THREE.Texture;
  }>();
  useEffect(() => {
    if (!url) return;
    let cancelled = false;
    const texture = new THREE.TextureLoader().load(
      url,
      (value) => {
        if (cancelled) {
          value.dispose();
          return;
        }
        value.colorSpace = THREE.SRGBColorSpace;
        value.generateMipmaps = true;
        value.minFilter = THREE.LinearMipmapLinearFilter;
        setLoaded({ url, texture: value });
      },
      undefined,
      () => {
        if (!cancelled) onError(mapId);
      },
    );
    return () => {
      cancelled = true;
      texture.dispose();
    };
  }, [url, mapId, onError]);
  return loaded && loaded.url === url ? loaded.texture : undefined;
}

type LoadedLayer = GlobeCityPolicyProps["layers"][number];
function RasterMap({
  layer,
  terrainHeight,
  order,
  onError,
}: {
  layer: LoadedLayer;
  terrainHeight: number;
  order: number;
  onError: (id: string) => void;
}) {
  const data = layer.data!;
  const height = (Number.isFinite(terrainHeight) ? terrainHeight : 0) + 2;
  const origin = useMemo(
    () =>
      WGS84_ELLIPSOID.getCartographicToPosition(
        (((data.bounds[1] + data.bounds[3]) / 2) * Math.PI) / 180,
        (((data.bounds[0] + data.bounds[2]) / 2) * Math.PI) / 180,
        height,
        new THREE.Vector3(),
      ),
    [data.bounds, height],
  );
  const overview = useMapTexture(
    `${CITY_PLAN_ASSETS}/${data.id}/${data.overview}`,
    data.id,
    onError,
  );
  const geometry = useMemo(
    () =>
      data.tiles.map((tile) =>
        cityPlanTileGeometry(tile, data.gridSize, height, origin, true),
      ),
    [data, height, origin],
  );
  useEffect(
    () =>
      retainResourceForDeferredDisposal(geometry, (values) =>
        values.forEach((value) => value.dispose()),
      ),
    [geometry],
  );
  const size = useThree((state) => state.size);
  const [visible, setVisible] = useState<{ index: number; detail: boolean }[]>(
    [],
  );
  const last = useRef(0),
    signature = useRef("");
  const scratch = useMemo(
    () => ({
      frustum: new THREE.Frustum(),
      matrix: new THREE.Matrix4(),
      sphere: new THREE.Sphere(),
      center: new THREE.Vector3(),
    }),
    [],
  );
  useFrame(({ camera, clock }) => {
    if (clock.elapsedTime - last.current < 0.25) return;
    last.current = clock.elapsedTime;
    scratch.frustum.setFromProjectionMatrix(
      scratch.matrix.multiplyMatrices(
        camera.projectionMatrix,
        camera.matrixWorldInverse,
      ),
    );
    const next: typeof visible = [];
    geometry.forEach((value, index) => {
      scratch.sphere.copy(value.boundingSphere!);
      scratch.sphere.center.add(origin);
      if (!scratch.frustum.intersectsSphere(scratch.sphere)) return;
      const distance = Math.max(
        1,
        camera.position.distanceTo(scratch.sphere.center),
      );
      const pixelDiameter =
        (scratch.sphere.radius / distance) *
        size.height *
        Math.abs(camera.projectionMatrix.elements[5]);
      next.push({ index, detail: pixelDiameter > 240 });
    });
    const key = next
      .map((item) => `${item.index}:${Number(item.detail)}`)
      .join(",");
    if (key !== signature.current) {
      signature.current = key;
      setVisible(next);
    }
  });
  return (
    <group name={`city-policy:${data.id}`} position={origin}>
      {overview &&
        visible.map(({ index, detail }) => (
          <RasterTile
            key={data.tiles[index].id}
            tile={data.tiles[index]}
            geometry={geometry[index]}
            overview={overview}
            detail={detail}
            mapId={data.id}
            opacity={layer.opacity}
            order={order}
            onError={onError}
          />
        ))}
    </group>
  );
}

function RasterTile({
  tile,
  geometry,
  overview,
  detail,
  mapId,
  opacity,
  order,
  onError,
}: {
  tile: PlanTile;
  geometry: THREE.BufferGeometry;
  overview: THREE.Texture;
  detail: boolean;
  mapId: string;
  opacity: number;
  order: number;
  onError: (id: string) => void;
}) {
  const texture = useMapTexture(
    detail ? `${CITY_PLAN_ASSETS}/${mapId}/${tile.id}.webp` : undefined,
    mapId,
    onError,
  );
  const detailGeometry = useMemo(() => {
    const result = geometry.clone(),
      uv = result.attributes.uv;
    for (let i = 0; i < uv.count; i++)
      uv.setXY(
        i,
        (uv.getX(i) - tile.rect[0]) / (tile.rect[2] - tile.rect[0]),
        1 - (1 - uv.getY(i) - tile.rect[1]) / (tile.rect[3] - tile.rect[1]),
      );
    return result;
  }, [geometry, tile.rect]);
  useEffect(
    () =>
      retainResourceForDeferredDisposal(detailGeometry, (value) =>
        value.dispose(),
      ),
    [detailGeometry],
  );
  return (
    <mesh
      name={`city-policy-tile:${mapId}:${tile.id}`}
      geometry={texture ? detailGeometry : geometry}
      raycast={NO_HIT}
      renderOrder={order}
      userData={{ cityPolicyId: mapId }}
      frustumCulled={false}
    >
      <meshBasicMaterial
        map={texture ?? overview}
        transparent
        opacity={opacity}
        depthTest={false}
        depthWrite={false}
        side={THREE.DoubleSide}
        toneMapped={false}
      />
    </mesh>
  );
}
