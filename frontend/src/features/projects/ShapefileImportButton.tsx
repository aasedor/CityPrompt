import { useCallback, useRef, useState } from 'react';
import { Loader2, Upload } from 'lucide-react';
import toast from 'react-hot-toast';
import { useQueryClient } from '@tanstack/react-query';
import { getApiErrorMessage, shapefilesApi, siteZonesApi } from '@/services/api';
import { ZONE_TYPE_CONFIG } from '@/types';
import type { SiteZoneProperties, SiteZoneType } from '@/types';

interface ShapefileImportButtonProps {
  projectId: string;
  /** Called with the [lng, lat] centroid of all imported geometry, once persisted. */
  onImported?: (centroid: [number, number]) => void;
  className?: string;
  iconSize?: number;
}

const DEFAULT_BUTTON_CLASS =
  'flex w-full items-center justify-center gap-2 rounded-full border-2 border-[#151515] ' +
  'bg-white px-3 py-2.5 text-sm font-black uppercase text-[#151515] shadow-[4px_4px_0_0_#151515] ' +
  'transition hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-[2px_2px_0_0_#151515] ' +
  'disabled:cursor-not-allowed disabled:opacity-60';

/**
 * "Upload Shapefile" — accepts a zipped ESRI shapefile, has the backend parse +
 * reproject it to lon/lat, then creates one site zone per polygon feature.
 *
 * Zones are created sequentially (not in parallel) to avoid the concurrent
 * optimistic-cache race, then the zone query is invalidated once so the globe
 * re-renders the whole imported set together.
 */
export function ShapefileImportButton({ projectId, onImported, className, iconSize = 16 }: ShapefileImportButtonProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const queryClient = useQueryClient();

  const handleFile = useCallback(
    async (file: File) => {
      setBusy(true);
      const toastId = toast.loading(`Reading ${file.name}…`);
      try {
        const result = await shapefilesApi.parse(file);

        if (result.feature_count === 0) {
          toast.error(result.warnings[0] || 'No polygon features found in the shapefile.', { id: toastId });
          return;
        }

        let created = 0;
        let sumLng = 0;
        let sumLat = 0;
        let vertexCount = 0;

        for (const feature of result.features) {
          const zoneType = (
            feature.zone_type in ZONE_TYPE_CONFIG ? feature.zone_type : 'development_area'
          ) as SiteZoneType;
          const config = ZONE_TYPE_CONFIG[zoneType];
          await siteZonesApi.create(projectId, {
            zone_type: zoneType,
            coordinates: feature.coordinates,
            color: config.color,
            properties: {
              ...config.defaultProperties,
              ...feature.properties,
              _imported_from: file.name,
            } as SiteZoneProperties,
          });
          created += 1;
          for (const [lng, lat] of feature.coordinates) {
            sumLng += lng;
            sumLat += lat;
            vertexCount += 1;
          }
        }

        await queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });

        const centroid: [number, number] =
          vertexCount > 0 ? [sumLng / vertexCount, sumLat / vertexCount] : [0, 0];
        const skipped = result.skipped_count ? `, skipped ${result.skipped_count} non-polygon` : '';
        toast.success(
          `Imported ${created} feature${created === 1 ? '' : 's'}${skipped} · ${result.detected_crs} · ` +
            `near ${centroid[1].toFixed(4)}, ${centroid[0].toFixed(4)}`,
          { id: toastId, duration: 6000 },
        );
        if (vertexCount > 0) onImported?.(centroid);
      } catch (error) {
        toast.error(getApiErrorMessage(error, 'Shapefile import failed'), { id: toastId });
      } finally {
        setBusy(false);
        if (inputRef.current) inputRef.current.value = '';
      }
    },
    [projectId, queryClient, onImported],
  );

  return (
    <>
      <input
        ref={inputRef}
        type="file"
        accept=".zip"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) void handleFile(file);
        }}
      />
      <button
        type="button"
        disabled={busy}
        onClick={() => inputRef.current?.click()}
        title="Import a zipped ESRI shapefile (.shp + .dbf + .shx + .prj) as site zones"
        className={className ?? DEFAULT_BUTTON_CLASS}
      >
        {busy ? <Loader2 size={iconSize} className="animate-spin" /> : <Upload size={iconSize} />}
        {busy ? 'Importing…' : 'Upload Shapefile'}
      </button>
    </>
  );
}
