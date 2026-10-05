import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';

export function gitLfsObjectRoot(repo) {
  const pointer = path.join(repo, '.git');
  if (!fs.existsSync(pointer)) return null;
  let admin = pointer;
  if (!fs.statSync(pointer).isDirectory()) {
    const content = fs.readFileSync(pointer, 'utf8').trim();
    if (!content.startsWith('gitdir:')) return null;
    admin = path.resolve(repo, content.slice(7).trim());
  }
  const common = path.join(admin, 'commondir');
  return path.join(fs.existsSync(common) ? path.resolve(admin, fs.readFileSync(common, 'utf8').trim()) : admin, 'lfs/objects');
}

export function readVerifiedLfsObject(root, digest, size) {
  if (!root || !/^[a-f0-9]{64}$/.test(digest)) throw new Error('Exact Git LFS object unavailable');
  const file = path.join(root, digest.slice(0,2), digest.slice(2,4), digest);
  const bytes = fs.readFileSync(file);
  if ((size !== undefined && bytes.length !== size) || createHash('sha256').update(bytes).digest('hex') !== digest) throw new Error('Exact Git LFS object differs');
  return bytes;
}

export function parseLfsPointer(bytes) {
  const match = /^version https:\/\/git-lfs.github.com\/spec\/v1\r?\noid sha256:([a-f0-9]{64})\r?\nsize (\d+)\r?\n?$/.exec(bytes.toString());
  return match ? { sha256: match[1], size: Number(match[2]) } : null;
}
