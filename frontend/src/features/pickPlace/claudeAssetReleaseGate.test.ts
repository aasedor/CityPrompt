import { describe, expect, it } from 'vitest';
import { LOCAL_CLAUDE_ASSETS, LOCAL_CLAUDE_SAVED_ASSETS, isLocalClaudeTrialEnvironment } from './claudeAssetLocalTrial';

describe('unpublished Claude pilot release boundary', () => {
  it('keeps the standard test roster identical to production unless the local pilot is explicitly exercised', () => {
    expect(LOCAL_CLAUDE_ASSETS).toEqual([]);
    expect(LOCAL_CLAUDE_SAVED_ASSETS).toEqual([]);
  });
  it('enables only the development server, never production, test or other build modes', () => {
    expect(isLocalClaudeTrialEnvironment(true, 'development')).toBe(true);
    for (const mode of ['production', 'test', 'staging']) {
      expect(isLocalClaudeTrialEnvironment(true, mode)).toBe(false);
    }
    expect(isLocalClaudeTrialEnvironment(false, 'development')).toBe(false);
  });
});
