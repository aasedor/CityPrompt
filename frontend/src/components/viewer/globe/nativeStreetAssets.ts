import { Group } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
export interface StreetAsset { url: string; sha256: string }
type Resource = { promise: Promise<void>; scene?: Group; error?: Error };
const resources = new Map<string, Resource>();
export function clearFailedNativeStreetLoads() {
  for (const [key, resource] of resources) if (resource.error) resources.delete(key);
  window.dispatchEvent(new Event('cityprompt:retry-native-streets'));
}
async function load(asset: StreetAsset): Promise<Group> {
  const response = await fetch(asset.url, { signal: AbortSignal.timeout(10000) });
  if (!response.ok) throw new Error('A street component could not be loaded. Choose Retry 3D update.');
  const bytes = await response.arrayBuffer();
  const digest = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), b => b.toString(16).padStart(2, '0')).join('');
  const view = new DataView(bytes);
  if (digest !== asset.sha256 || bytes.byteLength < 20 || view.getUint32(0,true) !== 0x46546c67
    || view.getUint32(4,true) !== 2 || view.getUint32(8,true) !== bytes.byteLength
    || view.getUint32(16,true) !== 0x4e4f534a || view.getUint32(12,true) > bytes.byteLength-20) {
    throw new Error('A street component does not match its saved revision.');
  }
  const document = JSON.parse(new TextDecoder().decode(bytes.slice(20,20+view.getUint32(12,true))));
  if ([...(document.images ?? []), ...(document.buffers ?? [])].some(item => 'uri' in item)) {
    throw new Error('The street component has unverified external assets.');
  }
  return (await new GLTFLoader().parseAsync(bytes, '')).scene;
}
function resourceFor(asset: StreetAsset): Resource {
  const key = `${asset.sha256}:${asset.url}`;
  let resource = resources.get(key);
  if (!resource) {
    resource = { promise: Promise.resolve() };
    const current = resource;
    current.promise = load(asset).then(scene => { current.scene=scene; }, error => { current.error=error; });
    resources.set(key, current);
  }
  return resource;
}
export function verifyStreetAssets(assets: StreetAsset[]): void {
  const pending = assets.map(resourceFor);
  const failed = pending.find(resource => resource.error);
  if (failed) throw failed.error;
  if (pending.some(resource => !resource.scene)) throw Promise.all(pending.map(resource => resource.promise));
}
export function verifiedStreetScene(asset: StreetAsset): Group {
  const resource=resourceFor(asset);
  if (resource.error) throw resource.error;
  if (!resource.scene) throw resource.promise;
  return resource.scene;
}
