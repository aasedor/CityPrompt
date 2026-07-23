/**
 * Google3DGlobe.tsx
 *
 * Standalone Google Earth-style 3D globe using React Three Fiber
 * and 3d-tiles-renderer. No Mapbox — pure Google Photorealistic 3D Tiles.
 */

import { Canvas } from '@react-three/fiber';
import {
  TilesRenderer,
  TilesPlugin,
  GlobeControls,
  TilesAttributionOverlay,
} from '3d-tiles-renderer/r3f';
import {
  GoogleCloudAuthPlugin,
  TileCompressionPlugin,
  UpdateOnChangePlugin,
  UnloadTilesPlugin,
  TilesFadePlugin,
} from '3d-tiles-renderer/plugins';

const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

export function Google3DGlobe() {
  if (!API_KEY) {
    return (
      <div className="flex h-full items-center justify-center bg-gray-900 text-white">
        <p>Missing VITE_GOOGLE_MAPS_API_KEY in .env</p>
      </div>
    );
  }

  return (
    <div className="relative h-full w-full bg-black">
      <Canvas
        camera={{ position: [0, 0, 4e7], near: 1, far: 1e11 }}
        gl={{ antialias: true, logarithmicDepthBuffer: true }}
      >
        <TilesRenderer>
          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
          <TilesPlugin plugin={GoogleCloudAuthPlugin} args={{ apiToken: API_KEY, useRecommendedSettings: true } as any} />
          <TilesPlugin plugin={TileCompressionPlugin} />
          <TilesPlugin plugin={UpdateOnChangePlugin} />
          <TilesPlugin plugin={UnloadTilesPlugin} />
          <TilesPlugin plugin={TilesFadePlugin} />
          <GlobeControls />
          <TilesAttributionOverlay />
        </TilesRenderer>
      </Canvas>
    </div>
  );
}
