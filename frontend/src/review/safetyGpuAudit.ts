/** Local diagnostic only. This does not replace project-workflow acceptance. */
import {
  Box3, Vector3, Matrix4, Mesh, Scene, Color, PerspectiveCamera,
  AmbientLight, DirectionalLight, WebGLRenderer, type Material, type Texture,
} from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DETAIL_CATALOGUE } from '../features/parks/detailCatalogue';
import { buildDetailInstances, disposeDetailInstances } from '../features/parks/detailInstances';

export interface SafetyGpuResult {
  id: string; status: string; image?: string; error?: string;
  geometryBytes?: number; draws?: number; triangles?: number;
  textures?: number; geometries?: number; loadMs?: number;
  originalDraws?: number; repeatedDraws?: number; maxChannelDifference?: number; changedPixels?: number;
}

export async function safetyGpuAudit(update: (rows: SafetyGpuResult[]) => void) {
  const renderer = new WebGLRenderer({ antialias: true, preserveDrawingBuffer: true, logarithmicDepthBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(480, 360);
  const results: SafetyGpuResult[] = [];
  try {
    for (const asset of DETAIL_CATALOGUE.filter(a => a.safety)) {
      const geometry = new Set<Mesh['geometry']>(), materials = new Set<Material>(), textures = new Set<Texture>();
      let batch: ReturnType<typeof buildDetailInstances> | undefined;
      try {
        const start = performance.now();
        const loaded = await new GLTFLoader().loadAsync(asset.url);
        const loadMs = performance.now() - start;
        loaded.scene.traverse(object => {
          const mesh = object as Mesh;
          if (!mesh.isMesh) return;
          geometry.add(mesh.geometry);
          for (const material of Array.isArray(mesh.material) ? mesh.material : [mesh.material]) {
            materials.add(material);
            for (const value of Object.values(material)) if (value?.isTexture) textures.add(value);
          }
        });
        const buffers = new Set<ArrayBufferLike>();
        for (const g of geometry) {
          if (g.index) buffers.add(g.index.array.buffer);
          for (const attribute of Object.values(g.attributes)) {
            buffers.add(attribute.array.buffer);
          }
        }
        const bounds = new Box3().setFromObject(loaded.scene);
        const center = bounds.getCenter(new Vector3());
        const size = bounds.getSize(new Vector3());
        const distance = Math.max(size.x, size.y, size.z, 1) * 1.6;
        const scene = new Scene(); scene.background = new Color('#e7edf0');
        scene.add(new AmbientLight('#ffffff', 2));
        const light = new DirectionalLight('#ffffff', 3); light.position.set(8, 15, 12); scene.add(light);
        const camera = new PerspectiveCamera(42, 480/360, .05, 1000);
        camera.position.copy(center).add(new Vector3(.8, .7, 1).normalize().multiplyScalar(distance));
        camera.lookAt(center);
        // Camera framing never modifies the authored object pivot or metre scale.
        batch = buildDetailInstances(loaded.scene, [new Matrix4()]); scene.add(batch);
        renderer.render(scene, camera);
        const originalDraws = renderer.info.render.calls;
        const originalTriangles = renderer.info.render.triangles;
        const baseline = new Uint8Array(480*360*4), actual = new Uint8Array(baseline.length);
        const gl = renderer.getContext();
        gl.readPixels(0,0,480,360,gl.RGBA,gl.UNSIGNED_BYTE,baseline);
        scene.remove(batch); disposeDetailInstances(batch);
        batch = buildDetailInstances(loaded.scene, [new Matrix4()], true); scene.add(batch);
        renderer.render(scene, camera);
        await new Promise<void>(resolve => requestAnimationFrame(() => resolve()));
        renderer.render(scene, camera);
        if (!renderer.info.render.triangles) throw new Error('No triangles drawn');
        if (renderer.info.render.triangles !== originalTriangles) throw new Error('Triangle count changed');
        gl.readPixels(0,0,480,360,gl.RGBA,gl.UNSIGNED_BYTE,actual);
        let maxChannelDifference=0, changedPixels=0;
        for(let p=0;p<actual.length;p+=4){let changed=false;for(let c=0;c<3;c++){const d=Math.abs(actual[p+c]-baseline[p+c]);maxChannelDifference=Math.max(maxChannelDifference,d);changed ||= d>2;} if(changed)changedPixels++;}
        const optimizedDraws=renderer.info.render.calls, triangles=renderer.info.render.triangles;
        const image=renderer.domElement.toDataURL('image/png');
        const repeated=buildDetailInstances(loaded.scene,Array.from({length:100},()=>new Matrix4()),true);
        scene.remove(batch);scene.add(repeated);renderer.render(scene,camera);
        const repeatedDraws=renderer.info.render.calls;
        scene.remove(repeated);disposeDetailInstances(repeated);
        results.push({id: asset.id, status:'PASS', image:renderer.domElement.toDataURL('image/png'),
          geometryBytes:[...buffers].reduce((n,b)=>n+b.byteLength,0), loadMs,
          draws:optimizedDraws, triangles,originalDraws,repeatedDraws,maxChannelDifference,changedPixels,
          geometries:renderer.info.memory.geometries, textures:renderer.info.memory.textures});
        results[results.length-1].image=image;
      } catch (error) {
        results.push({id:asset.id,status:'FAIL',error:String(error)});
      } finally {
        if (batch) disposeDetailInstances(batch);
        geometry.forEach(g=>g.dispose()); materials.forEach(m=>m.dispose()); textures.forEach(t=>t.dispose());
        renderer.renderLists.dispose();
      }
      update([...results]);
    }
  } finally { renderer.dispose(); renderer.forceContextLoss(); }
}
