/** Promise.allSettled semantics without starting an unbounded request storm. */
export async function allSettledWithConcurrency<T, TResult>(
  items: readonly T[],
  worker: (item: T, index: number) => Promise<TResult>,
  concurrency = 8,
): Promise<Array<PromiseSettledResult<TResult>>> {
  if (items.length === 0) return [];

  const limit = Math.min(
    items.length,
    Math.max(1, Math.floor(Number.isFinite(concurrency) ? concurrency : 1)),
  );
  const results = new Array<PromiseSettledResult<TResult>>(items.length);
  let nextIndex = 0;

  const runWorker = async () => {
    while (nextIndex < items.length) {
      const index = nextIndex;
      nextIndex += 1;
      try {
        results[index] = {
          status: 'fulfilled',
          value: await worker(items[index], index),
        };
      } catch (reason) {
        results[index] = { status: 'rejected', reason };
      }
    }
  };

  await Promise.all(Array.from({ length: limit }, () => runWorker()));
  return results;
}
