import type { WebGLRenderer } from 'three';
import { KTX2Loader, type GLTFLoader } from 'three-stdlib';

// Keep delivery independent of a checked-in transcoder binary. Production can
// override this at build time and self-host the same official Three.js files.
export const KTX2_TRANSCODER_PATH = (
  import.meta.env.VITE_KTX2_TRANSCODER_PATH
  || 'https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/libs/basis/'
);

const loaderByRenderer = new WeakMap<WebGLRenderer, KTX2Loader>();

/** Drei useGLTF extension that enables Basis Universal/KTX2 textures. */
export function createKtx2LoaderExtension(renderer: WebGLRenderer): (loader: GLTFLoader) => void {
  return (loader: GLTFLoader) => {
    let ktx2 = loaderByRenderer.get(renderer);
    if (!ktx2) {
      ktx2 = new KTX2Loader()
        .setTranscoderPath(KTX2_TRANSCODER_PATH)
        .detectSupport(renderer);
      loaderByRenderer.set(renderer, ktx2);
    }
    loader.setKTX2Loader(ktx2);
  };
}
