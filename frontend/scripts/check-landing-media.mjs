import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

// Vite source imports bypass CITYPROMPT_PUBLIC_DIR and must be hydrated too.
const directory = process.argv[2] || fileURLToPath(new URL('../src/features/landing/media/', import.meta.url));
const names = ['kensington-aerial.png', 'kensington-context.png', 'tree-lined-street.png', 'tree-lined-street.mp4'];
let bytes = 0;
for (const name of names) {
  const data = readFileSync(join(directory, name));
  if (data.subarray(0, 42).toString('ascii').startsWith('version https://git-lfs.github.com/spec/v1')) {
    throw Error(`Unhydrated Git LFS pointer: ${name}. Hydrate the tracked landing media before building.`);
  }
  // The committed context capture is JPEG despite its historical .png filename.
  const contextJpeg = name === 'kensington-context.png' && data.length >= 4
    && data.subarray(0, 3).toString('hex') === 'ffd8ff' && data.subarray(-2).toString('hex') === 'ffd9';
  const valid = contextJpeg || (name.endsWith('.png')
    ? data.length >= 24 && data.subarray(0, 8).toString('hex') === '89504e470d0a1a0a'
      && data.toString('ascii', 12, 16) === 'IHDR' && data.readUInt32BE(16) > 0 && data.readUInt32BE(20) > 0
    : data.length >= 16 && data.toString('ascii', 4, 8) === 'ftyp'
      && data.readUInt32BE(0) >= 16 && data.readUInt32BE(0) <= data.length);
  if (!valid) throw Error(`Invalid landing media: ${name}. Restore the tracked image or MP4 before building.`);
  bytes += data.length;
}
console.log(`Landing media: ${names.length} hydrated image/video files, ${(bytes / 1048576).toFixed(1)} MiB.`);
