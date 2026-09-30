import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import { Html, Line } from '@react-three/drei';
import { metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import type { PublicRoadSuggestion } from './publicRoadSuggestions';

export function PublicRoadSuggestionMarker({ suggestion, height }: { suggestion: PublicRoadSuggestion; height: number }) {
  const [lng, lat] = suggestion.endpoint;
  const points = suggestion.edge.map(p => [(p[0] - lng) * metersPerDegLon(lat), (p[1] - lat) * 111320, .3] as [number, number, number]);
  return <EastNorthUpFrame lat={lat * Math.PI / 180} lon={lng * Math.PI / 180} height={height}>
    <Line points={points} color="#22d3ee" lineWidth={5} depthTest={false} raycast={() => null} />
    <Html center position={[0, 0, 4]} zIndexRange={[25, 20]} style={{ pointerEvents: 'none', width: 240 }}>
      <div role="status" className="rounded-lg border-2 border-cyan-400 bg-slate-950 p-2 text-center text-xs text-white shadow-lg">
        <strong>Connect to {suggestion.road.label}</strong><br />
        Estimated mapped edge · Check alignment<br />Finish route to accept · Hold Alt to skip
      </div>
    </Html>
  </EastNorthUpFrame>;
}
