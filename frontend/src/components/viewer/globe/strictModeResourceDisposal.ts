const resourceGenerations = new WeakMap<object, number>();

type Disposable = { dispose: () => void };
interface PreparedModuleResources {
  buildingOnly: { ownedGeometries: readonly Disposable[] };
  landscape?: { ownedGeometries: readonly Disposable[]; ownedMaterials: readonly Disposable[] } | null;
}

/** A module stack gets one lease; separate registrations would cancel each other. */
export function retainPreparedModuleResources<T extends PreparedModuleResources>(modules: T[]): () => void {
  return retainResourceForDeferredDisposal(modules, values => {
    const owned = new Set<Disposable>();
    for (const {buildingOnly, landscape} of values) {
      for (const resource of [...buildingOnly.ownedGeometries,
        ...(landscape?.ownedGeometries ?? []), ...(landscape?.ownedMaterials ?? [])]) owned.add(resource);
    }
    owned.forEach(resource => resource.dispose());
  });
}

/**
 * Delay Three.js resource disposal by one microtask and cancel it when React
 * immediately retains the same memoized resource again.
 *
 * React 18 StrictMode intentionally runs effect cleanup and setup twice in
 * development. Disposing a geometry in that simulated cleanup leaves the live
 * second setup holding an already-disposed geometry, which makes planning
 * polygons disappear while their HTML labels remain visible.
 */
export function retainResourceForDeferredDisposal<T extends object>(
  resource: T,
  dispose: (resource: T) => void,
): () => void {
  const generation = (resourceGenerations.get(resource) ?? 0) + 1;
  resourceGenerations.set(resource, generation);

  return () => {
    queueMicrotask(() => {
      if (resourceGenerations.get(resource) !== generation) return;
      resourceGenerations.delete(resource);
      dispose(resource);
    });
  };
}
