import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { LineSegments2 } from 'three/examples/jsm/lines/LineSegments2.js';
import { LineSegmentsGeometry } from 'three/examples/jsm/lines/LineSegmentsGeometry.js';
import { LineMaterial } from 'three/examples/jsm/lines/LineMaterial.js';
import { transportStyle, type TransportCategory, type TransportSnapshot } from './transportVectors';

const RAD = Math.PI / 180, LIFT = .2;
const NO_HIT = () => {};
export type GroundNode = { lng: number; lat: number; height: number | null; position: THREE.Vector3; update: Array<() => void>; epoch: number };
export type TransportObject = LineSegments2 | THREE.Mesh;

/** Geographic vertical, never a ray from the viewing camera. Only visible tile
 * meshes are eligible: an unloaded/hidden parent LOD is not the shown ground. */
export function sampleGeographicSurface(lng: number, lat: number, roots: THREE.Object3D[], ray = new THREE.Raycaster()): number | null {
  const start = WGS84_ELLIPSOID.getCartographicToPosition(lat * RAD, lng * RAD, 50000, new THREE.Vector3());
  const down = WGS84_ELLIPSOID.getCartographicToNormal(lat * RAD, lng * RAD, new THREE.Vector3()).negate();
  ray.set(start, down); ray.far = 100000;
  for (const hit of ray.intersectObjects(roots, true)) {
    let visible = true, attached = false;
    // TilesGroup's optimized raycaster can also inspect cached tile scenes.
    // A detached scene may retain visible=true and an obsolete world transform.
    for (let p: THREE.Object3D | null = hit.object; p; p = p.parent) {
      if (!p.visible) { visible = false; break; }
      if (roots.includes(p)) attached = true;
    }
    if (visible && attached) {
      const height = WGS84_ELLIPSOID.getPositionElevation(hit.point);
      // Loading/coarse Google tiles occasionally produce kilometre-scale
      // outliers (observed -27 km and +3.4 km in central Calgary). Reject those
      // measurements; never replace them with an invented flat elevation.
      // This generous plausibility envelope applies only to Calgary, leaving
      // imported layers in other regions free to follow their own elevations.
      const inCalgary = lng >= -114.35 && lng <= -113.85 && lat >= 50.8 && lat <= 51.22;
      if (Number.isFinite(height) && (!inCalgary || (height >= 500 && height <= 2000))) return height;
    }
  }
  return null;
}

/** Batched geometry with small mutable patches. Unknown segments are collapsed
 * until both ends have terrain evidence; existing samples survive missing tiles. */
export function buildGroundedTransport(data: TransportSnapshot, mapId: string, order: number) {
  const origin = WGS84_ELLIPSOID.getCartographicToPosition(51.05 * RAD, -114.07 * RAD, 0, new THREE.Vector3());
  const nodes: GroundNode[] = [], lookup = new Map<string, GroundNode>(), objects: TransportObject[] = [];
  const nodeAt = (lng: number, lat: number) => {
    const key = `${lng.toFixed(8)},${lat.toFixed(8)}`;
    let node = lookup.get(key);
    if (!node) {
      node = { lng, lat, height: null, position: WGS84_ELLIPSOID.getCartographicToPosition(lat * RAD, lng * RAD, 1100, new THREE.Vector3()).sub(origin), update: [], epoch: -1 };
      lookup.set(key, node); nodes.push(node);
    }
    return node;
  };
  type Batch = { segments: Array<[GroundNode, GroundNode]>; ids: string[]; triangles: Array<[GroundNode, GroundNode, GroundNode]>; pointIds: string[] };
  const batches = new Map<TransportCategory, Batch>();
  for (const feature of data.features) {
    const category = feature.properties.category;
    let batch = batches.get(category);
    if (!batch) { batch = { segments: [], ids: [], triangles: [], pointIds: [] }; batches.set(category, batch); }
    if (feature.geometry.type === 'Point') {
      const [lng, lat] = feature.geometry.coordinates, center = nodeAt(lng, lat);
      const radius = category === 'service-stop' ? 6 : category === 'transit-centre' ? 17 : 28;
      const ring = Array.from({ length: 16 }, (_, i) => nodeAt(lng + Math.cos(i * Math.PI / 8) * radius / (111320 * Math.cos(lat * RAD)), lat + Math.sin(i * Math.PI / 8) * radius / 111320));
      ring.forEach((node, i) => { batch!.triangles.push([center, node, ring[(i + 1) % ring.length]]); batch!.pointIds.push(feature.id); });
    } else {
      const lines = feature.geometry.type === 'LineString' ? [feature.geometry.coordinates] : feature.geometry.coordinates;
      for (const line of lines) for (let i = 1; i < line.length; i++) {
        const a = line[i - 1], b = line[i];
        const distance = Math.hypot((b[0] - a[0]) * 111320 * Math.cos(a[1] * RAD), (b[1] - a[1]) * 111320);
        if (distance < .001) continue;
        const count = Math.max(1, Math.ceil(distance / 10));
        let previous = nodeAt(a[0], a[1]);
        for (let n = 1; n <= count; n++) {
          const next = nodeAt(a[0] + (b[0] - a[0]) * n / count, a[1] + (b[1] - a[1]) * n / count);
          batch.segments.push([previous, next]); batch.ids.push(feature.id); previous = next;
        }
      }
    }
  }
  const dirty = new Set<THREE.BufferGeometry>();
  const chunksByKey = new Map<string, { center: THREE.Vector3; nodes: GroundNode[] }>();
  for (const node of nodes) {
    const key = `${Math.floor(node.lng * 500)},${Math.floor(node.lat * 1000)}`;
    let chunk = chunksByKey.get(key);
    if (!chunk) { chunk = { center: node.position.clone().add(origin), nodes: [] }; chunksByKey.set(key, chunk); }
    chunk.nodes.push(node);
  }
  const prepare = (object: TransportObject, ids: string[], offset: number) => {
    object.userData = { cityPolicyId: mapId, transportIds: ids, policyRaycast: object.raycast.bind(object) };
    object.raycast = NO_HIT; object.renderOrder = order + offset; object.frustumCulled = false;
    // Broad static bounds enclose every possible Calgary surface elevation, so
    // picking requires no city-wide bounds rebuild after each small patch.
    object.geometry.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 150000);
    object.geometry.boundingBox = new THREE.Box3(new THREE.Vector3(-150000, -150000, -150000), new THREE.Vector3(150000, 150000, 150000));
    objects.push(object);
  };
  for (const [category, batch] of batches) {
    const style = transportStyle(category);
    if (batch.segments.length) {
      const geometry = new LineSegmentsGeometry().setPositions(new Float32Array(batch.segments.length * 6));
      const grounded = new THREE.InstancedBufferAttribute(new Float32Array(batch.segments.length), 1);
      geometry.setAttribute('instanceGrounded', grounded);
      const material = new LineMaterial({ color: style.color, linewidth: 4, transparent: true, depthTest: true, depthWrite: false, toneMapped: false, dashed: style.dashed, dashSize: 30, gapSize: 20 });
      // A collapsed segment is not a safe hidden line: the wide-line shader
      // normalizes its zero direction and can produce screen-spanning spikes.
      // Cull unknown instances before any perspective/line-width calculations.
      material.onBeforeCompile = shader => {
        shader.vertexShader = 'attribute float instanceGrounded;\n' + shader.vertexShader.replace(
          'void main() {', 'void main() { if (instanceGrounded < 0.5) { gl_Position = vec4(2.0, 2.0, 2.0, 1.0); return; }');
      };
      material.customProgramCacheKey = () => 'grounded-transport-v1';
      const object = new LineSegments2(geometry, material);
      const start = geometry.getAttribute('instanceStart'), end = geometry.getAttribute('instanceEnd');
      // Initial geographic distances keep dash phase independent of tile loading.
      const distances = new Float32Array(batch.segments.length * 2); let distance = 0;
      batch.segments.forEach(([a, b], i) => {
        distances[i * 2] = distance; distance += a.position.distanceTo(b.position); distances[i * 2 + 1] = distance;
        const update = () => {
          if (a.height === null || b.height === null) return;
          start.setXYZ(i, a.position.x, a.position.y, a.position.z); end.setXYZ(i, b.position.x, b.position.y, b.position.z);
          grounded.setX(i, 1); grounded.addUpdateRange(i, 1); grounded.needsUpdate = true;
          (start as THREE.InterleavedBufferAttribute).data.addUpdateRange(i * 6, 6);
          start.needsUpdate = true; end.needsUpdate = true; dirty.add(geometry);
        };
        a.update.push(update); b.update.push(update);
      });
      const distanceBuffer = new THREE.InstancedInterleavedBuffer(distances, 2, 1);
      geometry.setAttribute('instanceDistanceStart', new THREE.InterleavedBufferAttribute(distanceBuffer, 1, 0));
      geometry.setAttribute('instanceDistanceEnd', new THREE.InterleavedBufferAttribute(distanceBuffer, 1, 1));
      prepare(object, batch.ids, 0);
    }
    if (batch.triangles.length) {
      const geometry = new THREE.BufferGeometry(), positions = new THREE.BufferAttribute(new Float32Array(batch.triangles.length * 9), 3);
      geometry.setAttribute('position', positions);
      const material = new THREE.MeshBasicMaterial({ color: style.color, transparent: true, depthTest: true, depthWrite: false, toneMapped: false, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
      batch.triangles.forEach((triangle, i) => {
        const update = () => {
          if (triangle.some(n => n.height === null)) return;
          triangle.forEach((n, j) => positions.setXYZ(i * 3 + j, n.position.x, n.position.y, n.position.z));
          positions.addUpdateRange(i * 9, 9);
          positions.needsUpdate = true; dirty.add(geometry);
        };
        triangle.forEach(n => n.update.push(update));
      });
      prepare(new THREE.Mesh(geometry, material), batch.pointIds, .5);
    }
  }
  return { origin, nodes, chunks: [...chunksByKey.values()], objects, dirty,
    setHeight(node: GroundNode, height: number | null) {
      if (height === null || !Number.isFinite(height) || node.height === height) return;
      node.height = height;
      WGS84_ELLIPSOID.getCartographicToPosition(node.lat * RAD, node.lng * RAD, height + LIFT, node.position).sub(origin);
      node.update.forEach(update => update());
    },
    dispose() { objects.forEach(o => { o.geometry.dispose(); (o.material as THREE.Material).dispose(); }); },
  };
}
