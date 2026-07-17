import { Component, useMemo, type ReactNode } from 'react';
import * as THREE from 'three';
import { Html, useGLTF, useProgress } from '@react-three/drei';
import { Loader2 } from 'lucide-react';
import { resolveApiFileUrl } from '@/services/api';
import type { SiteZoneProperties } from '@/types';
import { BUILDING_AESTHETIC_OPTIONS_V2, type AestheticOption } from '@/components/viewer/aestheticCatalog';
import type { LegoAssemblyInstance, LegoAssemblyPlan } from './legoAssemblyApi';

// Shared building blocks for the single-zone composer (LegoAssemblyPreview)
// and the plan-level builder (LegoBuilderPanel).

export const MIN_DIMENSION_M = 4;
export const MAX_DIMENSION_M = 300;
export const MIN_FLOORS = 1;
export const MAX_FLOORS = 100;
export const SCALE_WARNING_THRESHOLD = 0.05;

export function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

/** Strip variant suffixes (`_front_day`, `_variant_3`) so catalogue lookups hit the base archetype id. */
export function normalizeArchetypeId(id: string | undefined): string | undefined {
  if (!id) return undefined;
  return id.replace(/_front_day$/, '').replace(/_variant_\d+$/, '');
}

/** Catalogue entry for an archetype id — tries the raw id first, then the normalized base id. */
export function findCatalogOption(archetypeId: string | undefined): AestheticOption | undefined {
  if (!archetypeId) return undefined;
  const normalizedId = normalizeArchetypeId(archetypeId);
  return (
    BUILDING_AESTHETIC_OPTIONS_V2.find((option) => option.id === archetypeId)
    || BUILDING_AESTHETIC_OPTIONS_V2.find((option) => option.id === normalizedId)
  );
}

/**
 * Default assembly targets for a zone: catalogue suggested width/depth, floors
 * from the zone (falling back to the catalogue floor midpoint), and sane
 * 24 × 18 × 4 fallbacks when there is no catalogue hit.
 */
export function deriveZoneTargets(
  catalogOption: AestheticOption | undefined,
  zoneProperties: SiteZoneProperties | undefined,
): { width_m: number; depth_m: number; floors: number } {
  const zoneFloors = zoneProperties?.floors;
  const floors = typeof zoneFloors === 'number' && zoneFloors > 0
    ? Math.round(zoneFloors)
    : catalogOption?.minFloors != null && catalogOption?.maxFloors != null
      ? Math.round((catalogOption.minFloors + catalogOption.maxFloors) / 2)
      : catalogOption?.minFloors ?? catalogOption?.maxFloors ?? 4;
  return {
    width_m: clamp(catalogOption?.suggestedWidth_m ?? 24, MIN_DIMENSION_M, MAX_DIMENSION_M),
    depth_m: clamp(catalogOption?.suggestedDepth_m ?? 18, MIN_DIMENSION_M, MAX_DIMENSION_M),
    floors: clamp(floors, MIN_FLOORS, MAX_FLOORS),
  };
}

/** Archetype-compiler commands that create + import a module family for an archetype. */
export function familyGenerationCommands(archetypeId: string): string {
  const family = archetypeId.replace(/_/g, '-');
  const output = `build/archetypes/${archetypeId}`;
  return [
    `python tools/archetype_compiler/generate_family.py --archetype-id ${archetypeId} --output ${output} --skip-thumbnail`,
    `python tools/archetype_compiler/generate_facade_sheets.py --family ${output}`,
    `python tools/archetype_compiler/generate_family.py --archetype-id ${archetypeId} --output ${output} --facade-sheets tools/archetype_compiler/facade_sheets/${family} --facade-sheet-detail city --no-ao`,
    `python tools/archetype_compiler/import_manifest.py ${output}`,
  ].join('\n');
}

/** True when the planner had to stretch modules noticeably to hit the target footprint. */
export function fitIsStretched(fit: LegoAssemblyPlan['fit'] | null | undefined): boolean {
  if (!fit) return false;
  return (
    Math.abs(fit.scale_x - 1) > SCALE_WARNING_THRESHOLD
    || Math.abs(fit.scale_y - 1) > SCALE_WARNING_THRESHOLD
  );
}

export function Progress() {
  const { progress } = useProgress();
  return (
    <Html center>
      <div className="flex items-center gap-2 whitespace-nowrap rounded bg-black/70 px-3 py-2 text-xs font-semibold text-white">
        <Loader2 className="h-4 w-4 animate-spin" />
        {progress > 0 ? `${progress.toFixed(0)}%` : 'Loading modules…'}
      </div>
    </Html>
  );
}

export class PreviewErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? (
      <Html center>
        <div className="rounded bg-red-950/90 px-3 py-2 text-xs font-semibold text-red-200">
          A module could not be loaded.
        </div>
      </Html>
    ) : this.props.children;
  }
}

/** Calibrate a cloned module for the standalone LEGO composer preview. */
export function normalizeLegoModuleMaterials(root: THREE.Object3D): void {
  root.traverse((object) => {
    const mesh = object as THREE.Mesh;
    if (!mesh.isMesh) return;
    const isMaterialArray = Array.isArray(mesh.material);
    const sourceMaterials: THREE.Material[] = isMaterialArray
      ? mesh.material as THREE.Material[]
      : [mesh.material as THREE.Material];
    const materials = sourceMaterials.map((source) => source.clone());
    mesh.material = isMaterialArray ? materials : materials[0];
    for (const material of materials) {
      const standard = material as THREE.MeshStandardMaterial;
      if (!standard?.isMeshStandardMaterial) continue;
      if (standard.aoMap) {
        standard.aoMap = null;
        standard.aoMapIntensity = 0;
      }
      if (standard.name.startsWith('MAT_Sheet_')) {
        // The elevation is already de-lit and contains its own fine facade
        // shading; a second strong IBL/specular pass makes photographic albedo
        // look pale and synthetic in City Prompt's intentionally bright scene.
        standard.envMapIntensity = 0.18;
        standard.color.setScalar(0.5);
        standard.roughnessMap = null;
        standard.roughness = 1;
        standard.metalness = 0;
      } else {
        standard.envMapIntensity = 0.9;
      }
      if (standard.map) standard.map.colorSpace = THREE.SRGBColorSpace;
      standard.needsUpdate = true;
    }
  });
}

/**
 * One planned module GLB. Backend plans are Z-up while three.js is Y-up —
 * hence the [x, z, y] position and [sx, sz, sy] scale swizzle.
 */
export function ModuleInstance({ instance }: { instance: LegoAssemblyInstance }) {
  const url = resolveApiFileUrl(instance.model_url);
  const { scene } = useGLTF(url);
  const model = useMemo(() => {
    const cloned = scene.clone(true);
    normalizeLegoModuleMaterials(cloned);
    return cloned;
  }, [scene]);
  const [sx, sy, sz] = instance.scale;
  const [x, y, z] = instance.position;

  return (
    <primitive
      object={model}
      position={[x, z, y]}
      scale={[sx, sz, sy]}
      rotation={[0, -instance.rotation_degrees * Math.PI / 180, 0]}
    />
  );
}
