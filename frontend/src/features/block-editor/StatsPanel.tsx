import { useBlockEditorStore } from '@/store/blockEditorStore';

export function StatsPanel() {
  const { editedLayout, zone } = useBlockEditorStore();
  if (!editedLayout || !zone) return null;

  const buildings = editedLayout.buildings;
  const totalArea = buildings.reduce((sum, b) => sum + b.width_m * b.depth_m, 0);

  // Zone area estimate from coordinates
  const coords = zone.coordinates;
  let zoneArea = 0;
  let zoneWidthM = 0;
  let zoneDepthM = 0;
  if (coords.length >= 3) {
    const mlon = 111320 * Math.abs(Math.cos((coords[0][1] * Math.PI) / 180));
    const mlat = 111320;
    const mCoords = coords.map((c) => [(c[0] - coords[0][0]) * mlon, (c[1] - coords[0][1]) * mlat]);
    const xs = mCoords.map((c) => c[0]);
    const ys = mCoords.map((c) => c[1]);
    zoneWidthM = Math.max(...xs) - Math.min(...xs);
    zoneDepthM = Math.max(...ys) - Math.min(...ys);
    for (let i = 0; i < coords.length; i++) {
      const j = (i + 1) % coords.length;
      zoneArea += mCoords[i][0] * mCoords[j][1] - mCoords[j][0] * mCoords[i][1];
    }
    zoneArea = Math.abs(zoneArea) / 2;
  }

  const coverage = zoneArea > 0 ? ((totalArea / zoneArea) * 100).toFixed(1) : '?';
  const density = zoneArea > 0 ? ((buildings.length / (zoneArea / 10000))).toFixed(1) : '?';

  return (
    <div className="absolute bottom-4 left-4 rounded-xl border border-white/[0.08] bg-primary-950/90 backdrop-blur-xl px-4 py-3 shadow-xl">
      <div className="flex items-center gap-6 text-[11px]">
        <Stat label="Zone" value={`${Math.round(zoneWidthM)}\u00D7${Math.round(zoneDepthM)}m`} />
        <Stat label="Blocks" value={String(buildings.length)} />
        <Stat label="Coverage" value={`${coverage}%`} />
        <Stat label="Density" value={`${density}/ha`} />
        <Stat label="Built area" value={`${Math.round(totalArea).toLocaleString()} m\u00B2`} />
        {editedLayout.roads.length > 0 && (
          <Stat label="Roads" value={String(editedLayout.roads.length)} />
        )}
        {editedLayout.green_spaces.length > 0 && (
          <Stat label="Green" value={String(editedLayout.green_spaces.length)} />
        )}
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-neutral-500 text-[9px] uppercase tracking-wider">{label}</div>
      <div className="text-white font-semibold tabular-nums">{value}</div>
    </div>
  );
}
