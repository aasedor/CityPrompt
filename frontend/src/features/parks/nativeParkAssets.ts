import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
export type Asset = {url:string;sha256:string};
type Resource = {promise:Promise<void>;scene?:THREE.Group;error?:Error};
const resources = new Map<string,Resource>();
export function clearFailedNativeParkLoads() { for (const [key,value] of resources) if (value.error) resources.delete(key); window.dispatchEvent(new Event('cityprompt:retry-native-parks')); }
async function loadVerified(asset: Asset): Promise<THREE.Group> {
  const response=await fetch(asset.url,{signal:AbortSignal.timeout(10000)});
  if (!response.ok) throw new Error('The park model could not be loaded. Retry the 3D update.');
  const bytes=await response.arrayBuffer();
  const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
  if (digest!==asset.sha256 || bytes.byteLength<20 || new DataView(bytes).getUint32(0,true)!==0x46546c67) throw new Error('The park model does not match its saved revision.');
  const jsonSize=new DataView(bytes).getUint32(12,true);
  const document=JSON.parse(new TextDecoder().decode(bytes.slice(20,20+jsonSize)));
  if ([...(document.images??[]),...(document.buffers??[])].some(item=>'uri' in item)) throw new Error('The park model has unverified external assets.');
  return (await new GLTFLoader().parseAsync(bytes,'')).scene;
}
function resourceFor(asset: Asset): Resource {
  let resource=resources.get(asset.sha256);
  if (!resource) {
    resource={promise:Promise.resolve()};
    const current=resource;
    current.promise=loadVerified(asset).then(scene=>{current.scene=scene;},error=>{current.error=error;});
    resources.set(asset.sha256,current);
  }
  return resource;
}
/** Start the whole dependency closure together, before Suspense pauses rendering. */
export function verifyParkAssets(assets: Array<Asset|undefined>): void {
  const pending=assets.filter((asset):asset is Asset=>!!asset).map(resourceFor);
  const failed=pending.find(resource=>resource.error);
  if(failed)throw failed.error;
  if(pending.some(resource=>!resource.scene))throw Promise.all(pending.map(resource=>resource.promise));
}
export function verifiedScene(asset: Asset): THREE.Group {
  const resource=resourceFor(asset);
  if (resource.error) throw resource.error;
  if (!resource.scene) throw resource.promise;
  return resource.scene;
}
