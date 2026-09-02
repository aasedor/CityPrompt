import { describe, expect, it } from 'vitest';

import { selectViteEnvDir } from './viteEnvDir';

const baseCandidates = {
  projectRoot: 'C:/worktree',
  projectEnvExists: true,
  projectEnvHasAssignments: false,
  sharedGitDir: 'C:/repo/.git',
  sharedEnvExists: false,
  primaryCheckoutRoot: 'C:/repo',
  primaryEnvExists: true,
  fallbackEnvDir: 'C:/worktree/frontend',
};

describe('Vite environment directory resolution', () => {
  it('does not let an empty recovery .env shadow the shared Git key store', () => {
    expect(selectViteEnvDir(baseCandidates)).toBe('C:/repo');
  });

  it('falls back to the historical Git key store when the primary checkout has no env', () => {
    expect(selectViteEnvDir({
      ...baseCandidates,
      primaryEnvExists: false,
      sharedEnvExists: true,
    })).toBe('C:/repo/.git');
  });

  it('keeps the primary checkout key store ahead of a stale populated worktree env', () => {
    expect(selectViteEnvDir({
      ...baseCandidates,
      projectEnvHasAssignments: true,
    })).toBe('C:/repo');
  });

  it('uses a populated worktree env when no primary checkout env exists', () => {
    expect(selectViteEnvDir({
      ...baseCandidates,
      projectEnvHasAssignments: true,
      primaryEnvExists: false,
    })).toBe('C:/worktree');
  });

  it('honors VITE_ENV_DIR ahead of repository discovery', () => {
    expect(selectViteEnvDir({
      ...baseCandidates,
      explicitEnvDir: 'C:/explicit-env',
    })).toBe('C:/explicit-env');
  });
});
