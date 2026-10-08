import { AmbientLight, Box3, Color, DirectionalLight, Mesh, OrthographicCamera, Scene, Vector3, WebGLRenderer, type Material, Texture } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { detailAsset } from './detailCatalogue';

// One short-lived WebGL context for the entire catalogue, never one per card.
let renderer: WebGLRenderer | undefined;
let release: ReturnType<typeof setTimeout> | undefined;
let queue: Promise<unknown> = Promise.resolve();
const images = new Map<string, Promise<string>>();
export function detailThumbnail(id: string): Promise<string> {
  const cached = images.get(id);
  if (cached) return cached;
  const task = queue.then(async () => {
    const { scene: model } = await new GLTFLoader().loadAsync(detailAsset(id).url);
    try {
      if (release) clearTimeout(release);
      renderer ??= new WebGLRenderer({ alpha: false, antialias: true });
      renderer.setSize(320, 210);
      const scene = new Scene(); scene.background = new Color('#f1f5f9');
      scene.add(model, new AmbientLight(0xffffff, 2));
      const light = new DirectionalLight(0xffffff, 3); light.position.set(5, 10, 8); scene.add(light);
      const bounds = new Box3().setFromObject(model), size = bounds.getSize(new Vector3()), center = bounds.getCenter(new Vector3());
      const radius = size.length() / 2 || 1, aspect = 320 / 210;
      const camera = new OrthographicCamera(-radius * aspect, radius * aspect, radius, -radius, radius * 0.01, radius * 20);
      camera.position.copy(center).add(new Vector3(1.4, 1, 1.8).normalize().multiplyScalar(radius * 4));
      camera.lookAt(center); camera.updateProjectionMatrix();
      renderer.render(scene, camera);
      return renderer.domElement.toDataURL('image/webp', 0.85);
    } finally {
      const materials = new Set<Material>(), textures = new Set<Texture>();
      model.traverse(object => { if (object instanceof Mesh) { object.geometry.dispose();
        (Array.isArray(object.material) ? object.material : [object.material]).forEach(m => materials.add(m)); } });
      materials.forEach(m => { Object.values(m).forEach(v => { if (v instanceof Texture) textures.add(v); }); m.dispose(); });
      textures.forEach(t => t.dispose());
      release = setTimeout(() => { renderer?.dispose(); renderer?.forceContextLoss(); renderer = undefined; }, 1500);
    }
  });
  queue = task.catch(() => {});
  images.set(id, task);
  task.catch(() => images.delete(id));
  return task;
}
