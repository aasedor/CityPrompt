import type { SiteZone } from "@/types";
import {
  isCommunity3DCompiled,
  resolveCommunity3DKind,
} from "@/features/community3d/community3d";
import { Camera, PerspectiveCamera, Vector3 } from "three";
import { WGS84_ELLIPSOID } from "3d-tiles-renderer";
import {
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from "@/components/viewer/mapEngine/geoUtils";
import type { Direct3DCaptureBundle } from "@/components/viewer/globe/direct3dCapture";

export type CaptureLandscapeContext = (
  boundary: number[][],
) => Promise<Direct3DCaptureBundle>;

/** Frame the whole parcel plus a real neighbourhood margin, independent of the student's zoom. */
export function frameLandscapeContext(
  camera: Camera,
  boundary: number[][],
  terrainHeight: number,
  controls?: { enabled?: boolean; pivotPoint?: Vector3 },
) {
  if (
    !(camera as PerspectiveCamera).isPerspectiveCamera ||
    boundary.length < 3 ||
    boundary.some((p) => !Number.isFinite(p[0]) || !Number.isFinite(p[1]))
  ) {
    throw new Error(
      "The site view is not ready. Open the 3D globe and try again.",
    );
  }
  const west = Math.min(...boundary.map((p) => p[0])),
    east = Math.max(...boundary.map((p) => p[0]));
  const south = Math.min(...boundary.map((p) => p[1])),
    north = Math.max(...boundary.map((p) => p[1]));
  const lng = (west + east) / 2,
    lat = (south + north) / 2;
  const width = (east - west) * metersPerDegLon(lat),
    height = (north - south) * METERS_PER_DEG_LAT;
  const margin = Math.max(35, Math.max(width, height) * 0.2);
  const perspective = camera as PerspectiveCamera;
  const halfFov = Math.tan((perspective.getEffectiveFOV() * Math.PI) / 360);
  const altitude = Math.max(
    180,
    (height + margin * 2) / (halfFov * 2),
    (width + margin * 2) / (halfFov * 2 * perspective.aspect),
  );
  const saved = {
    position: camera.position.clone(),
    quaternion: camera.quaternion.clone(),
    up: camera.up.clone(),
    pivot: controls?.pivotPoint?.clone(),
    enabled: controls?.enabled,
  };
  const surface = new Vector3(),
    up = new Vector3(),
    northAxis = new Vector3();
  WGS84_ELLIPSOID.getCartographicToPosition(
    (lat * Math.PI) / 180,
    (lng * Math.PI) / 180,
    terrainHeight,
    surface,
  );
  WGS84_ELLIPSOID.getEastNorthUpAxes(
    (lat * Math.PI) / 180,
    (lng * Math.PI) / 180,
    new Vector3(),
    northAxis,
    up,
  );
  if (controls) controls.enabled = false;
  camera.position.copy(surface).addScaledVector(up, altitude);
  camera.up.copy(northAxis);
  camera.lookAt(surface);
  camera.updateMatrixWorld();
  controls?.pivotPoint?.copy(surface);
  return () => {
    camera.position.copy(saved.position);
    camera.quaternion.copy(saved.quaternion);
    camera.up.copy(saved.up);
    camera.updateMatrixWorld();
    if (controls) {
      controls.enabled = saved.enabled;
      if (saved.pivot) controls.pivotPoint?.copy(saved.pivot);
    }
  };
}

export function landscapeContextImage(
  capture: Direct3DCaptureBundle,
  zones: SiteZone[] = [],
): string {
  const pixels = capture.width * capture.height;
  if (
    pixels <= 0 ||
    capture.contextPixelCount / pixels < 0.08 ||
    capture.proposalPixelCount <= 0
  ) {
    throw new Error(
      "The surrounding neighbourhood is not visible yet. Let the Google tiles load and try again.",
    );
  }
  const instances = Object.values(capture.instanceIdManifest ?? {});
  for (const zone of zones.filter(isCommunity3DCompiled)) {
    const kind = resolveCommunity3DKind(zone);
    if (!kind) continue;
    const visible = instances.some(
      (instance) =>
        instance.semantic_class === kind &&
        (instance.zone_id === zone.id ||
          instance.source_zone_ids?.includes(zone.id)) &&
        (!capture.instancePixelCounts ||
          (capture.instancePixelCounts[instance.instance_id] ?? 0) > 0),
    );
    if (!visible)
      throw new Error(
        "Turn on 3D models and let your whole development load before generating its landscape.",
      );
  }
  return capture.beautyImageBase64.replace(/^data:image\/[\w.+-]+;base64,/, "");
}
