import { describe, expect, it, vi } from 'vitest';
import { Box3, BoxGeometry, Group, Mesh, Vector3 } from 'three';
import { localTeachingBuildings, LOCAL_TEACHING_BUILDINGS } from './localTeachingBuildings';
import { CATALOGUE_ASSETS, validateRegistry } from './assetRegistry';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { assetForZone, placementProperties } from './catalogue';
import { nativeBuildingUrl } from './nativeBuildingContract';
import { rectangleAt, resizeRectangleCorner } from './geometry';
import { centreNativeClayClone } from '@/features/legoAssembly/nativeClayPlacement';
import { lessonForChoice, styleDefinition } from '@/features/catalogueLearning/teaching';
import { eraIds, historyForChoice } from '@/features/catalogueLearning/planningHistory';
import { nativeBuildingRoutes } from './nativeBuildingRouting';
import type { SiteZone } from '@/types';

vi.mock('./localTeachingBuildings', async () => {
  const actual = await vi.importActual<typeof import('./localTeachingBuildings')>('./localTeachingBuildings');
  return { ...actual, LOCAL_TEACHING_BUILDINGS: actual.localTeachingBuildings(true),
    LOCAL_TEACHING_LESSONS: actual.localTeachingLessons(true),
    LOCAL_TEACHING_HISTORY: actual.localTeachingHistory(true),
    LOCAL_TEACHING_STYLES: actual.localTeachingStyles(true) };
});

describe('seven exact local teaching buildings', () => {
  it('exposes precisely the reviewed seven in development only', () => {
    expect(localTeachingBuildings(false)).toEqual([]);
    expect(localTeachingBuildings(true)).toHaveLength(7);
    expect(new Set(LOCAL_TEACHING_BUILDINGS.map(a => a.id)).size).toBe(7);
    expect(LOCAL_TEACHING_BUILDINGS.some(a => /shoebox/i.test(a.id))).toBe(false);
    expect(validateRegistry(CATALOGUE_ASSETS)).toEqual([]);
  });

  it('registers exactly one discoverable placement for each reviewed revision', () => {
    for (const asset of LOCAL_TEACHING_BUILDINGS) {
      expect(CATALOGUE_ASSETS.filter(a => a.id === asset.id)).toHaveLength(1);
      expect(CANONICAL_CHOICES.filter(c => c.placements.some(a => a.id === asset.id))).toHaveLength(1);
      expect(asset.model.method).toBe('RLASM 6.1');
      expect(asset.readiness).toBe('pilot');
      expect(asset.width).toBeGreaterThanOrEqual(asset.nativeDimensions![0] + 3);
      expect(asset.depth).toBeGreaterThanOrEqual(asset.nativeDimensions![1] + 3);
    }
  });

  it('keeps native geometry and exact model after save/reopen and rejects stale revisions', () => {
    for (const asset of LOCAL_TEACHING_BUILDINGS) {
      const coordinates = rectangleAt([-114.03, 51.04], asset.width, asset.depth, 37);
      const saved = JSON.parse(JSON.stringify({ coordinates, properties: placementProperties(asset) }));
      expect(assetForZone(saved)?.id).toBe(asset.id);
      expect(nativeBuildingUrl(saved)).toBe(asset.properties.validation_native_url);
      expect(resizeRectangleCorner(coordinates, 0, [-114.031, 51.041], asset)).toEqual(coordinates);
      expect(asset.reshapeMode).toBe('fixed_native');
      expect(asset.storeyProgram?.mode).toBe('fixed_authored_assembly');
      expect(asset.storeyProgram?.minStoreys).toBe(asset.storeyProgram?.maxStoreys);
      saved.properties.pick_place_model_revision = 'unreviewed-model';
      expect(assetForZone(saved)).toBeUndefined();
      expect(nativeBuildingUrl(saved)).toBeUndefined();
    }
  });

  it('owns stale saved trial identities before any planned-massing or other model fallback', () => {
    const asset = LOCAL_TEACHING_BUILDINGS[0];
    const stale = { id: 'saved-plot', project_id:'project', color:'#fff', sort_order:0, created_at:'before', updated_at:'before',
      building_id: 'saved-building', building_ids: ['saved-building', 'old-extra'],
      zone_type: 'building', properties: { ...placementProperties(asset), pick_place_model_revision: 'unavailable-revision' },
      coordinates: rectangleAt([-114.03, 51.04], asset.width, asset.depth) } as SiteZone;
    const planned = { id: 'saved-building', metadata: { community_3d: { generator: 'planned_massing' } } };
    const routes = nativeBuildingRoutes([stale], [planned, { id: 'old-extra' }, { id: 'unrelated' }]);
    expect(routes.reviewZones).toEqual([stale]);
    expect(routes.unavailableZones).toEqual([stale]);
    expect(routes.buildingIds).toEqual(new Set(['saved-building', 'old-extra']));
    expect(routes.otherBuildings.map(b => b.id)).toEqual(['unrelated']);
    const current = { ...stale, properties: placementProperties(asset) };
    expect(nativeBuildingRoutes([current], [planned]).unavailableZones).toEqual([]);
    expect(nativeBuildingRoutes([current], [planned]).otherBuildings).toEqual([]);
  });

  it('centres the asymmetric side-split envelope without scaling or changing shared source', () => {
    const asset = LOCAL_TEACHING_BUILDINGS.find(a => a.properties.development_archetype_id === 'postwar_side_split_house')!;
    const [w, d, h] = asset.nativeDimensions!;
    const source = new Group();
    const mesh = new Mesh(new BoxGeometry(w, h, d));
    mesh.position.set(-.0025, h / 2, .29); source.add(mesh);
    const before = new Box3().setFromObject(source);
    const centred = centreNativeClayClone(source.clone(true));
    const bounds = new Box3().setFromObject(centred);
    expect(bounds.getSize(new Vector3()).x).toBeCloseTo(w, 4);
    expect(bounds.getSize(new Vector3()).z).toBeCloseTo(d, 4);
    expect(bounds.min.y).toBeCloseTo(0);
    expect(bounds.getCenter(new Vector3()).x).toBeCloseTo(0);
    expect(bounds.getCenter(new Vector3()).z).toBeCloseTo(0);
    expect(new Box3().setFromObject(source)).toEqual(before);
    expect(mesh.scale.toArray()).toEqual([1, 1, 1]);
  });

  it('attaches reviewed basic teaching to exact models and withholds stale style and era', () => {
    for (const asset of LOCAL_TEACHING_BUILDINGS) {
      const choice = CANONICAL_CHOICES.find(c => c.placements.some(a => a.id === asset.id))!;
      const match = lessonForChoice(choice)!;
      expect(match.status).toBe('classified');
      expect(match.lesson.typeLabel).toBeTruthy();
      expect(match.lesson.styleIds.every(id => !!styleDefinition(id))).toBe(true);
      expect(eraIds(choice).length).toBeGreaterThan(0);
      expect(historyForChoice(choice)?.lesson.constructionYear).toBeNull();
      const stale = { ...choice, placements: [{ ...asset, model: { ...asset.model, revision: 'unknown' } }] };
      expect(lessonForChoice(stale)?.status).toBe('stale');
      expect(eraIds(stale)).toEqual([]);
    }
  });
});
