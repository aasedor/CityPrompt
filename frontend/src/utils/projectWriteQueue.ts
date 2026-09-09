import type { QueryClient } from '@tanstack/react-query';

const queues = new WeakMap<QueryClient, Map<string, Promise<unknown>>>();
/** Serialize this tab's authored and derived writes. Server revision checks still protect other editors. */
export function runProjectWrite<T>(client: QueryClient, projectId: string, write: () => Promise<T>): Promise<T> {
  let projects = queues.get(client);
  if (!projects) { projects = new Map(); queues.set(client, projects); }
  const previous = projects.get(projectId);
  const result = (previous ?? Promise.resolve()).catch(() => undefined).then(write);
  projects.set(projectId, result);
  void result.finally(() => {
    if (projects.get(projectId) === result) projects.delete(projectId);
  }).catch(() => undefined);
  return result;
}
