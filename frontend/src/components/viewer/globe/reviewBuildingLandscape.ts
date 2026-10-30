import * as THREE from 'three';
import polygonClipping, { type MultiPolygon, type Pair } from 'polygon-clipping';
import type { Building, SiteZone } from '@/types';
import { rectangleDimensions } from '@/features/pickPlace/geometry';
import { authoredHomePlotFrame, preservesAuthoredPlotAxes } from '@/features/legoAssembly/detachedPlot';
import { isNativeClayPlan } from '@/features/legoAssembly/nativeClayPlacement';
import { computeLegoStackYaw, extractLegoRecipe, legoInstanceTransform } from './legoGlobePlacement';
import { computeFootprintFrame } from './buildingPlacement';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '../mapEngine/geoUtils';
import { getResidualLandscapeRecipe, residualLandscapeBounds } from './residualLandscape';
import { assetForZone } from '@/features/pickPlace/catalogue';

type GroundFinish = { boundary: SiteZone; texture: THREE.Texture | null };
type NativeRect = readonly [number, number, number, number];
type GroundContract = { centre: readonly [number, number]; paths: NativeRect[]; curbs: NativeRect[]; foundationOnly?: boolean };
const rectangle = ([x0, z0, x1, z1]: NativeRect): Pair[] => [[x0, z0], [x1, z0], [x1, z1], [x0, z1], [x0, z0]];

/** Measured from the v010 authoring script's site(), porch_and_stair() and
 * complete GLB bounds. Coordinates are the original GLB's native X/Z metres.
 * This is a site finish, not permission to recolour other clay candidates. */
const CITY_HALL_GROUND = {
  centre: [-2.5, 5] as const,
  paths: [[-3.2, 27.4, 3.2, 35], [-27.5, 27.4, 28.5, 29],
    [-27.5, -25, -25.9, 29], [23.3, -25, 24.9, 29], [-27.5, -21, 28.5, -19.4]] as NativeRect[],
  beds: [[-22, 30.5, -6, 32], [6, 30.5, 23, 32]] as NativeRect[],
  curbs: [[-30.5, 28.88, 25.5, 29], [-27.5, -25, -27.38, 35]] as NativeRect[],
};

/** v006 site() uses a 7 m display road south/west of the hotel. That road is
 * part of its source illustration, rather than a student-authored street.
 * Keep its 3 m walks, narrower rear/east paths and the porte-cochere approach.
 * Dimensions are from the locked family_hotel_baronial.py at 0dea20a092. */
const RAILWAY_HOTEL_GROUND = {
  centre: [-2, 3] as const,
  beds: [] as NativeRect[],
  paths: [[-15.1, 29, -8.1, 39], [-34, 29, 37, 32], [-34, -33, -31, 29],
    [29, -27, 31, 29], [-31, -27, 31, -25]] as NativeRect[],
  curbs: [[-34, 31.88, 37, 32], [-34, -33, -33.88, 32]] as NativeRect[],
};

export function reviewBuildingLandscapeContract(zone: Pick<SiteZone, 'properties'>) {
  const p = zone.properties;
  if (p?.development_selected_variant_id === 'scottish_baronial_granite_tower'
    && p.pick_place_model_revision === 'clay-baronial-railway-hotel-clay-v006') return RAILWAY_HOTEL_GROUND;
  return p?.building_archetype_id === 'montreal_second_empire_civic'
    && p.development_selected_variant_id === 'montreal_civic_city_hall'
    && p.pick_place_model_revision === 'clay-second-empire-city-hall-clay-v010'
    ? CITY_HALL_GROUND : null;
}

/** Only registered, revision-resolved RLASM buildings opt into foundation
 * finishing. Uploaded models, unknown saved revisions and architectural paving
 * never acquire this policy by colour or a loose material-name match. */
function groundContract(source: THREE.Object3D | undefined, zone: SiteZone): GroundContract | null {
  const hall = reviewBuildingLandscapeContract(zone);
  if (hall) return hall;
  const asset = assetForZone(zone);
  if (!source || !asset || asset.model.method !== 'RLASM 6.1') return null;
  const bounds = new THREE.Box3().setFromObject(source, true);
  if (bounds.isEmpty()) return null;
  return { centre: [(bounds.min.x + bounds.max.x) / 2, (bounds.min.z + bounds.max.z) / 2],
    paths: [], curbs: [], foundationOnly: true };
}

export interface ReviewBuildingLandscapePlacement {
  /** Original GLB metres -> local ENU, including centring and saved instance transforms. */
  matrix: THREE.Matrix4;
  origin: Pair;
}

/** Use the same saved placement as the compiled renderer. The backend can
 * turn a fixed landmark by 90 degrees when a plot becomes deeper than wide;
 * neither its lawn phase nor its beds may assume that plot yaw is model yaw. */
export function reviewBuildingLandscapePlacement(zone: SiteZone, building?: Building, source?: THREE.Object3D,
  instanceIndex = 0): ReviewBuildingLandscapePlacement | null {
  const contract = groundContract(source, zone), frame = computeFootprintFrame(zone.coordinates);
  if (!contract || !frame) return null;
  let yaw = rectangleDimensions(zone.coordinates).degrees * Math.PI / 180;
  const instanceMatrix = new THREE.Matrix4();
  const originOffset = new THREE.Matrix4();
  if (building) {
    const recipe = extractLegoRecipe(building);
    if (!recipe || !recipe.instances[instanceIndex]) return null;
    const authored = preservesAuthoredPlotAxes(zone.properties) ? authoredHomePlotFrame(zone.coordinates) : undefined;
    yaw = authored ? authored.yawRad + (building.rotation_degrees ?? 0) * Math.PI / 180
      : computeLegoStackYaw(frame.bearingRad, recipe.target, building.rotation_degrees);
    const transform = legoInstanceTransform(recipe.instances[instanceIndex]);
    instanceMatrix.compose(new THREE.Vector3(...transform.position),
      new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), transform.rotationYRad),
      new THREE.Vector3(...transform.scale));
    originOffset.makeTranslation(...frame.rectCenterLocal, 0);
  }
  const centred = !building || isNativeClayPlan(extractLegoRecipe(building)!);
  const bounds = source ? new THREE.Box3().setFromObject(source, true) : null;
  const centre = bounds && !bounds.isEmpty() ? bounds.getCenter(new THREE.Vector3())
    : new THREE.Vector3(contract.centre[0], 0, contract.centre[1]);
  const floor = bounds && !bounds.isEmpty() ? bounds.min.y : 0;
  return { origin: [frame.centroidLng, frame.centroidLat], matrix: originOffset
    .multiply(new THREE.Matrix4().makeRotationZ(yaw))
    .multiply(new THREE.Matrix4().makeRotationX(Math.PI / 2))
    .multiply(instanceMatrix)
    .multiply(centred ? new THREE.Matrix4().makeTranslation(-centre.x, -floor, -centre.z) : new THREE.Matrix4()) };
}

/** Prepare an owned runtime clone. Only explicit near-grade ground materials
 * change; the source GLB, stair/stone geometry and complete bounds stay intact.
 * Split broad ground triangles at path edges, so a large source triangle can
 * carry both the site lawn and a continuous paved entrance approach. */
export function prepareReviewBuildingLandscape(source: THREE.Object3D, zone: SiteZone,
  ground: GroundFinish | null, placement = reviewBuildingLandscapePlacement(zone, undefined, source)): {
    clone: THREE.Object3D; ownedGeometries: THREE.BufferGeometry[]; ownedMaterials: THREE.Material[];
  } {
  const clone = source.clone(true), ownedGeometries: THREE.BufferGeometry[] = [], ownedMaterials: THREE.Material[] = [];
  const contract = groundContract(source, zone);
  if (!contract || !ground?.texture || !placement) return { clone, ownedGeometries, ownedMaterials };
  const paths = contract.paths.length
    ? polygonClipping.union([rectangle(contract.paths[0])], ...contract.paths.slice(1).map(r => [rectangle(r)])) : null;
  const texture = ground.texture;
  const grass = new THREE.MeshStandardMaterial({ map: texture, roughness: 1, side: THREE.DoubleSide });
  grass.name = 'site-matched-authored-ground';
  grass.userData.siteMatchedAuthoredGround = true;
  const bounds = residualLandscapeBounds(ground.boundary.coordinates), east = metersPerDegLon(placement.origin[1]);
  const width = Math.max(.01, (bounds.east - bounds.west) * east);
  const depth = Math.max(.01, (bounds.north - bounds.south) * METERS_PER_DEG_LAT);
  const recipe = getResidualLandscapeRecipe(ground.boundary), short = Math.min(width, depth);
  const repeatX = recipe ? 1 : Math.max(4, width / short * 4), repeatY = recipe ? 1 : Math.max(4, depth / short * 4);
  const uvAt = (point: THREE.Vector3): Pair => {
    const plan = point.clone().applyMatrix4(placement.matrix);
    return [((placement.origin[0] - bounds.west) * east + plan.x) / width * repeatX,
      ((placement.origin[1] - bounds.south) * METERS_PER_DEG_LAT + plan.y) / depth * repeatY];
  };
  clone.updateMatrixWorld(true);
  clone.traverse(object => {
    const mesh = object as THREE.Mesh;
    if (!mesh.isMesh || Array.isArray(mesh.material)) return;
    if (contract.foundationOnly) {
      if (mesh.material.name !== 'CLAY_FOUNDATION') return;
      const bounds = new THREE.Box3().setFromObject(mesh, true);
      // The complete mesh must be a shallow ground pad. Shared foundation
      // materials on steps, walls, raised terraces and roofs stay architectural.
      if (bounds.min.y < -.0001 || bounds.max.y > .3501) return;
    }
    const curb = mesh.material.name === 'CLAY_STONE';
    const limit = contract.foundationOnly ? .3501 : curb ? .1201 : mesh.material.name === 'CLAY_FOUNDATION' ? .1601
      : mesh.material.name === 'CLAY_CONCRETE' || mesh.material.name === 'CLAY_PLANTING' ? .0401 : null;
    if (limit === null) return;
    const original = mesh.geometry, index = original.getIndex(), p = original.getAttribute('position');
    const n = original.getAttribute('normal'), uv = original.getAttribute('uv');
    const positions: number[] = [], normals: number[] = [], uvs: number[] = [];
    const geometry = new THREE.BufferGeometry();
    let changed = false;
    const count = index?.count ?? p.count;
    for (let i = 0; i < count; i += 3) {
      const ids = [0, 1, 2].map(k => index ? index.getX(i + k) : i + k);
      const local = ids.map(id => new THREE.Vector3().fromBufferAttribute(p, id));
      const native = local.map(point => point.clone().applyMatrix4(mesh.matrixWorld));
      const append = (points: THREE.Vector3[], materialIndex: number) => {
        const start = positions.length / 3;
        const triangle = new THREE.Triangle(...local as [THREE.Vector3, THREE.Vector3, THREE.Vector3]);
        for (const [vertex, point] of points.entries()) {
          const unchanged = points === native;
          const localPoint = unchanged ? local[vertex] : mesh.worldToLocal(point.clone());
          const bary = unchanged ? new THREE.Vector3(Number(vertex === 0), Number(vertex === 1), Number(vertex === 2))
            : triangle.getBarycoord(localPoint, new THREE.Vector3())!;
          positions.push(...localPoint.toArray());
          const normal = n ? ids.map(id => new THREE.Vector3().fromBufferAttribute(n, id))
            .reduce((sum, value, k) => sum.addScaledVector(value, bary.getComponent(k)), new THREE.Vector3()) : triangle.getNormal(new THREE.Vector3());
          normals.push(...normal.normalize().toArray());
          if (materialIndex === 1) uvs.push(...uvAt(point));
          else uvs.push(uv ? uv.getX(ids[0]) * bary.x + uv.getX(ids[1]) * bary.y + uv.getX(ids[2]) * bary.z : 0,
            uv ? uv.getY(ids[0]) * bary.x + uv.getY(ids[1]) * bary.y + uv.getY(ids[2]) * bary.z : 0);
        }
        const previous = geometry.groups[geometry.groups.length - 1];
        if (previous?.materialIndex === materialIndex) previous.count += points.length;
        else geometry.addGroup(start, points.length, materialIndex);
      };
      const measuredCurb = !curb || contract.curbs.some(([x0, z0, x1, z1]) => native.every(v =>
        v.x >= x0 - .0001 && v.x <= x1 + .0001 && v.z >= z0 - .0001 && v.z <= z1 + .0001));
      if (!measuredCurb || Math.min(...native.map(v => v.y)) < -.0001 || Math.max(...native.map(v => v.y)) > limit) {
        append(native, 0); continue;
      }
      changed = true;
      if (!paths) { append(native, 1); continue; }
      const flat = Math.max(...native.map(v => v.y)) - Math.min(...native.map(v => v.y)) < .00001;
      if (!flat) { append(native, 1); continue; }
      const ring: Pair[] = [...native.map(v => [v.x, v.z] as Pair), [native[0].x, native[0].z]];
      const emit = (polygons: MultiPolygon, materialIndex: number) => {
        for (const [outer, ...holes] of polygons) {
          const contour = outer.slice(0, -1).map(v => new THREE.Vector2(...v));
          const inner = holes.map(hole => hole.slice(0, -1).map(v => new THREE.Vector2(...v)));
          const vertices = [...contour, ...inner.flat()];
          for (const face of THREE.ShapeUtils.triangulateShape(contour, inner)) {
            const points = face.map(k => new THREE.Vector3(vertices[k].x, native[0].y, vertices[k].y));
            // triangulateShape operates in X/Z; preserve the original cap normal.
            if (new THREE.Triangle(...points as [THREE.Vector3, THREE.Vector3, THREE.Vector3]).getNormal(new THREE.Vector3())
              .dot(new THREE.Triangle(...native as [THREE.Vector3, THREE.Vector3, THREE.Vector3]).getNormal(new THREE.Vector3())) < 0) points.reverse();
            append(points, materialIndex);
          }
        }
      };
      emit(polygonClipping.intersection([ring], paths), 0);
      emit(polygonClipping.difference([ring], paths), 1);
    }
    if (!changed) { geometry.dispose(); return; }
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
    geometry.computeBoundingBox(); geometry.computeBoundingSphere();
    mesh.geometry = geometry;
    mesh.material = [mesh.material, grass];
    ownedGeometries.push(geometry);
  });
  if (ownedGeometries.length) ownedMaterials.push(grass);
  else grass.dispose();
  return { clone, ownedGeometries, ownedMaterials };
}
