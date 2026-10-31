import { describe, expect, it } from 'vitest';
import { execFileSync } from 'node:child_process';

describe('local teaching trial production boundary', () => {
  it('tree-shakes trial buildings, lessons and style payload out of a production consumer', () => {
    // Run esbuild in native Node; JSDOM's Uint8Array realm cannot run its binary API.
    const bundle = execFileSync(process.execPath, ['--input-type=module', '-e', `
      import {build} from 'esbuild'; import path from 'node:path';
      const result = await build({
      stdin: { contents: "import {LOCAL_TEACHING_BUILDINGS,LOCAL_TEACHING_LESSONS,LOCAL_TEACHING_HISTORY,LOCAL_TEACHING_STYLES} from './localTeachingBuildings'; console.log(LOCAL_TEACHING_BUILDINGS,LOCAL_TEACHING_LESSONS,LOCAL_TEACHING_HISTORY,LOCAL_TEACHING_STYLES);",
        resolveDir: path.resolve('src/features/pickPlace'), loader: 'ts' },
      bundle: true, write: false, treeShaking: true, format: 'esm',
      define: { 'import.meta.env.DEV': 'false', 'import.meta.env.MODE': '"production"' },
      tsconfig: path.resolve('tsconfig.json'),
      }); process.stdout.write(result.outputFiles[0].text);
    `], { encoding: 'utf8' });
    expect(bundle).not.toContain('prairie_school_house');
    expect(bundle).not.toContain('local_teaching_');
    expect(bundle).not.toContain('occupied attic');
    expect(bundle).not.toContain('approved_offline_architectural_clay');
    expect(bundle).toContain('console.log');
  });
});
