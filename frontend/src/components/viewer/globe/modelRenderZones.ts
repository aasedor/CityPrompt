import type { Building, SiteZone } from '@/types';

const GENERATED_MODEL_ZONE_COLOR = '#8b5cf6';

/**
 * AI rendering is normally driven by editable planning zones. A generated
 * model can legitimately outlive its source zone, however: its persisted
 * Building footprint is still authoritative geometry and is what the user
 * can see on the globe. Materialize that footprint as a transient render zone
 * so model-only scenes remain renderable without recreating a colored zone.
 */
export function withModeledBuildingRenderZones(
  siteZones: SiteZone[],
  buildings: Building[],
  modeledBuildingIds: ReadonlySet<string>,
  projectId: string,
): SiteZone[] {
  if (modeledBuildingIds.size === 0) return siteZones;

  const representedBuildingIds = new Set(
    siteZones
      .map((zone) => zone.building_id)
      .filter((buildingId): buildingId is string => Boolean(buildingId)),
  );
  const now = new Date(0).toISOString();
  const synthetic = buildings.flatMap((building): SiteZone[] => {
    const coordinates = building.footprint_coordinates;
    if (
      !modeledBuildingIds.has(building.id)
      || representedBuildingIds.has(building.id)
      || !coordinates
      || coordinates.length < 3
    ) {
      return [];
    }

    const specifications = building.specifications ?? {};
    return [{
      id: `modeled-building:${building.id}`,
      project_id: projectId,
      name: building.name ?? 'Generated 3D building',
      zone_type: 'building',
      coordinates,
      color: GENERATED_MODEL_ZONE_COLOR,
      properties: {
        height: building.height_meters,
        floors: building.floor_count,
        architectural_style: building.architectural_style,
        archetype_id: specifications.archetype_id
          ?? (specifications.legoAssembly as { archetype_id?: string } | undefined)?.archetype_id,
        _model_footprint_render_zone: true,
      },
      sort_order: Number.MAX_SAFE_INTEGER,
      building_id: building.id,
      created_at: building.created_at || now,
      updated_at: now,
    }];
  });

  return synthetic.length > 0 ? [...siteZones, ...synthetic] : siteZones;
}
