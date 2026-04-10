/**
 * TilesAttributionOverlay.tsx
 *
 * Displays Google's required copyright attribution text when
 * Photorealistic 3D Tiles are active. Required by Google TOS.
 */

interface TilesAttributionOverlayProps {
  text: string;
}

export function TilesAttributionOverlay({ text }: TilesAttributionOverlayProps) {
  if (!text) return null;

  return (
    <div className="absolute bottom-2 right-2 z-20 max-w-xs rounded bg-black/60 px-2 py-1 backdrop-blur-sm">
      <p className="text-[10px] leading-tight text-white/70">{text}</p>
    </div>
  );
}
