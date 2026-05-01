import { useEffect, useRef, useState } from 'react';

const TRAIL_TILE_SIZE = 32;
const TRAIL_LENGTH = 28;
const TILE_FADE_DELAY_MS = 520;
const TILE_REMOVE_DELAY_MS = 1200;
const trailColors = ['#c9ff3d', '#ff5a3d', '#0aa6a6', '#f2b84b'];

type TrailTile = {
  id: number;
  x: number;
  y: number;
  color: string;
  fading: boolean;
};

type TrailCell = {
  column: number;
  row: number;
};

function getTrailCells(previousCell: TrailCell | null, nextCell: TrailCell) {
  if (!previousCell) {
    return [nextCell];
  }

  const columnDelta = nextCell.column - previousCell.column;
  const rowDelta = nextCell.row - previousCell.row;
  const stepCount = Math.min(Math.max(Math.abs(columnDelta), Math.abs(rowDelta)), 12);
  const cells: TrailCell[] = [];

  for (let step = 1; step <= stepCount; step += 1) {
    const progress = step / stepCount;
    const cell = {
      column: Math.round(previousCell.column + columnDelta * progress),
      row: Math.round(previousCell.row + rowDelta * progress),
    };
    const previousQueuedCell = cells[cells.length - 1];

    if (
      !previousQueuedCell ||
      previousQueuedCell.column !== cell.column ||
      previousQueuedCell.row !== cell.row
    ) {
      cells.push(cell);
    }
  }

  return cells;
}

export function TileTrail() {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const timeoutIdsRef = useRef<number[]>([]);
  const lastCellRef = useRef<TrailCell | null>(null);
  const tileIdRef = useRef(0);
  const [tiles, setTiles] = useState<TrailTile[]>([]);

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    if (prefersReducedMotion.matches) {
      return undefined;
    }

    const handlePointerMove = (event: PointerEvent) => {
      if (event.pointerType === 'touch') {
        return;
      }

      const container = containerRef.current;

      if (!container) {
        return;
      }

      const bounds = container.getBoundingClientRect();
      const localX = event.clientX - bounds.left;
      const localY = event.clientY - bounds.top;

      if (localX < 0 || localY < 0 || localX > bounds.width || localY > bounds.height) {
        lastCellRef.current = null;
        return;
      }

      const column = Math.floor(localX / TRAIL_TILE_SIZE);
      const row = Math.floor(localY / TRAIL_TILE_SIZE);
      const nextCell = { column, row };
      const previousCell = lastCellRef.current;

      if (previousCell?.column === column && previousCell.row === row) {
        return;
      }

      lastCellRef.current = nextCell;
      const newTiles = getTrailCells(previousCell, nextCell).map((cell) => {
        const id = tileIdRef.current;
        tileIdRef.current += 1;

        return {
          id,
          x: cell.column * TRAIL_TILE_SIZE,
          y: cell.row * TRAIL_TILE_SIZE,
          color: trailColors[(cell.column + cell.row) % trailColors.length],
          fading: false,
        };
      });

      const newestTiles = [...newTiles].reverse();

      setTiles((currentTiles) => [
        ...newestTiles,
        ...currentTiles.filter(
          (currentTile) =>
            !newTiles.some((tile) => currentTile.x === tile.x && currentTile.y === tile.y),
        ),
      ].slice(0, TRAIL_LENGTH));

      newTiles.forEach((tile) => {
        timeoutIdsRef.current.push(
          window.setTimeout(() => {
            setTiles((currentTiles) =>
              currentTiles.map((currentTile) =>
                currentTile.id === tile.id ? { ...currentTile, fading: true } : currentTile,
              ),
            );
          }, TILE_FADE_DELAY_MS),
        );

        timeoutIdsRef.current.push(
          window.setTimeout(() => {
            setTiles((currentTiles) =>
              currentTiles.filter((currentTile) => currentTile.id !== tile.id),
            );
          }, TILE_REMOVE_DELAY_MS),
        );
      });
    };

    window.addEventListener('pointermove', handlePointerMove, { passive: true });

    return () => {
      window.removeEventListener('pointermove', handlePointerMove);
      timeoutIdsRef.current.forEach((timeoutId) => window.clearTimeout(timeoutId));
      timeoutIdsRef.current = [];
    };
  }, []);

  return (
    <div
      ref={containerRef}
      aria-hidden="true"
      data-tile-trail="true"
      className="pointer-events-none absolute inset-0 z-[1] overflow-hidden"
    >
      {tiles.map((tile, index) => (
        <span
          key={tile.id}
          data-trail-tile="true"
          className={`absolute border border-[#151515]/25 shadow-[0_0_0_1px_rgba(21,21,21,0.04)_inset] transition-opacity duration-700 ease-out will-change-[opacity,transform] dark:border-white/20 ${
            tile.fading ? 'opacity-0' : 'opacity-65'
          }`}
          style={{
            width: TRAIL_TILE_SIZE,
            height: TRAIL_TILE_SIZE,
            transform: `translate3d(${tile.x}px, ${tile.y}px, 0)`,
            backgroundColor: tile.color,
            transitionDelay: `${Math.min(index * 12, 180)}ms`,
          }}
        />
      ))}
    </div>
  );
}
