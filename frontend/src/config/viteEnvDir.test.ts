import { describe, expect, it } from 'vitest';

import { selectViteEnvDir } from './viteEnvDir';

const baseCandidates = {
  projectRoot: 'C:/worktree',
  projectEnvExists: true,
  projectEnvHasAssignments: false,
  sharedGitDir: 'C:/repo/.git',
  sharedEnvExists: true,
  fallbackEnvDir: 'C:/worktree/frontend',
};

describe('Vite environment directory resolution', () => {
  it('does not let an empty recovery .env shadow the shared Git key store', () => {
    expect(selectViteEnvDir(baseCandidates)).toBe('C:/repo/.git');
  });

  it('keeps a populated worktree .env as an explicit override', () => {
    expect(selectViteEnvDir({
      ...baseCandidates,
      projectEnvHasAssignments: true,
    })).toBe('C:/worktree');
  });

  it('honors VITE_ENV_DIR ahead of repository discovery', () => {
    expect(selectViteEnvDir({
      ...baseCandidates,
      explicitEnvDir: 'C:/explicit-env',
    })).toBe('C:/explicit-env');
  });
});
