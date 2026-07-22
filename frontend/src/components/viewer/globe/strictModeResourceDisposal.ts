const resourceGenerations = new WeakMap<object, number>();

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
