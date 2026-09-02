export interface ViteEnvDirCandidates {
  explicitEnvDir?: string;
  projectRoot: string;
  projectEnvExists: boolean;
  projectEnvHasAssignments: boolean;
  sharedGitDir: string | null;
  sharedEnvExists: boolean;
  primaryCheckoutRoot?: string | null;
  primaryEnvExists?: boolean;
  fallbackEnvDir: string;
}

/** Select one Vite env directory without reading or exposing secret values. */
export function selectViteEnvDir({
  explicitEnvDir,
  projectRoot,
  projectEnvExists,
  projectEnvHasAssignments,
  sharedGitDir,
  sharedEnvExists,
  primaryCheckoutRoot,
  primaryEnvExists,
  fallbackEnvDir,
}: ViteEnvDirCandidates): string {
  if (explicitEnvDir) return explicitEnvDir;
  if (primaryCheckoutRoot && primaryEnvExists) return primaryCheckoutRoot;
  if (projectEnvHasAssignments) return projectRoot;
  if (sharedGitDir && sharedEnvExists) return sharedGitDir;
  // Preserve mode-specific worktree env discovery when no shared store exists.
  if (projectEnvExists) return projectRoot;
  return fallbackEnvDir;
}
