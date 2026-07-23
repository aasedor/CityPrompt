import * as THREE from 'three';

// ---------------------------------------------------------------------------
// Entourage Figure Catalog — pre-made photorealistic PNG cutouts
// ---------------------------------------------------------------------------

export interface EntourageFigure {
  id: string;
  path: string;
  label: string;
  contexts: Array<'park' | 'water' | 'street'>;
}

export const ENTOURAGE_CATALOG: EntourageFigure[] = [
  { id: 'sarah_architect',  path: '/entourage/01_sarah_architect.png',  label: 'Architect walking',     contexts: ['street', 'water'] },
  { id: 'james_cyclist',    path: '/entourage/02_james_cyclist.png',    label: 'Cyclist',               contexts: ['street'] },
  { id: 'priya_student',    path: '/entourage/03_priya_student.png',    label: 'Student walking',       contexts: ['park', 'street', 'water'] },
  { id: 'marcus_dad',       path: '/entourage/04_marcus_dad.png',       label: 'Dad with child',        contexts: ['park', 'street'] },
  { id: 'mei_professional', path: '/entourage/05_mei_professional.png', label: 'Professional walking',  contexts: ['street', 'water'] },
  { id: 'omar_elder',       path: '/entourage/06_omar_elder.png',       label: 'Elder strolling',       contexts: ['park', 'water'] },
  { id: 'alex_runner',      path: '/entourage/07_alex_runner.png',      label: 'Runner',                contexts: ['park', 'street'] },
  { id: 'elena_dog_walker', path: '/entourage/08_elena_dog_walker.png', label: 'Dog walker',            contexts: ['park'] },
  { id: 'raj_cafe',         path: '/entourage/09_raj_cafe.png',         label: 'Person at cafe',        contexts: ['street'] },
  { id: 'linnea_skater',    path: '/entourage/10_linnea_skater.png',    label: 'Skater',                contexts: ['park', 'street'] },
];

// ---------------------------------------------------------------------------
// Texture cache — loaded once, reused across renders
// ---------------------------------------------------------------------------

const textureCache = new Map<string, THREE.Texture>();
let loadPromise: Promise<void> | null = null;

/** Load all entourage PNG textures into cache. No-op after first call. */
export function ensureEntourageLoaded(): Promise<void> {
  if (loadPromise) return loadPromise;

  const loader = new THREE.TextureLoader();
  loadPromise = Promise.all(
    ENTOURAGE_CATALOG.map(
      (fig) =>
        new Promise<void>((resolve) => {
          loader.load(
            fig.path,
            (tex) => {
              tex.colorSpace = THREE.SRGBColorSpace;
              textureCache.set(fig.id, tex);
              resolve();
            },
            undefined,
            () => {
              console.warn(`[Entourage] Failed to load ${fig.path}`);
              resolve(); // silently skip failures
            },
          );
        }),
    ),
  ).then(() => {
    console.log(`[Entourage] Loaded ${textureCache.size}/${ENTOURAGE_CATALOG.length} textures`);
  });

  return loadPromise;
}

/** Synchronous getter for cached textures. Call ensureEntourageLoaded() first. */
export function getEntourageTextures(): Map<string, THREE.Texture> {
  return textureCache;
}

// ---------------------------------------------------------------------------
// Context-aware figure selection
// ---------------------------------------------------------------------------

/**
 * Pick `count` figures appropriate for the given context using seeded random.
 * Returns figures with their cached textures.
 */
export function selectEntourage(
  context: 'park' | 'water' | 'street' | 'default',
  count: number,
  seed: number,
): Array<{ figure: EntourageFigure; texture: THREE.Texture }> {
  // Filter by context (default = all)
  const eligible = context === 'default'
    ? ENTOURAGE_CATALOG
    : ENTOURAGE_CATALOG.filter((f) => f.contexts.includes(context as 'park' | 'water' | 'street'));

  // Only include figures with loaded textures
  const available = eligible.filter((f) => textureCache.has(f.id));
  if (available.length === 0) return [];

  // Seeded random (same LCG as tree placement in clay render)
  let s = Math.abs(seed) % 2147483648;
  const rand = () => {
    s = (s * 1103515245 + 12345) % 2147483648;
    return s / 2147483648;
  };

  // Shuffle and pick
  const shuffled = [...available].sort(() => rand() - 0.5);
  const picked = shuffled.slice(0, Math.min(count, shuffled.length));

  return picked.map((fig) => ({
    figure: fig,
    texture: textureCache.get(fig.id)!,
  }));
}
