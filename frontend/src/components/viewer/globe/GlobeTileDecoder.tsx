import { useEffect, useMemo, useState } from 'react';
import { TilesPlugin } from '3d-tiles-renderer/r3f';
import { GLTFExtensionsPlugin } from '3d-tiles-renderer/plugins';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';

/** Keep tile decodes alive across camera, selection and loading-state updates. */
export function GlobeTileDecoder() {
  const [loader, setLoader] = useState<DRACOLoader | null>(null);
  const args = useMemo(() => [{ dracoLoader: loader, autoDispose: false }], [loader]);

  useEffect(() => {
    const decoder = new DRACOLoader().setDecoderPath(
      'https://www.gstatic.com/draco/versioned/decoders/1.5.7/',
    );
    setLoader(decoder);
    // Own disposal here, including StrictMode's setup/cleanup/setup cycle.
    // Plugin replacement must not terminate workers with pending tile jobs.
    return () => { decoder.dispose(); };
  }, []);

  return loader ? <TilesPlugin
    plugin={GLTFExtensionsPlugin}
    args={args}
  /> : null;
}
