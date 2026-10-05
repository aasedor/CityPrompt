import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { checkCatalogueJson, duplicateJsonKeys } from './check-catalogue-json.mjs';

test('rejects conflicting and identical keys, including escaped names, in their own object',()=>{
  const text=String.raw`{"first":{"area":390,"area":650},"array":[{"id":1},{"id":2}],"same":true,"same":true,"name":1,"na\u006de":2}`;
  assert.deepEqual(duplicateJsonKeys(text).map(row=>row.key),['area','same','name']);
  assert.deepEqual(duplicateJsonKeys('{"quote":"braces {,} and \\\"key\\\": value", "array":[{"id":1},{"id":2}]}'),[]);
});
test('the actual catalogue has no silent duplicate-key overrides',()=>{
  assert.deepEqual(checkCatalogueJson(fileURLToPath(new URL('../src/data',import.meta.url))),[]);
});
