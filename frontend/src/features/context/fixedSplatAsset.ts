const PATH = '/gaussian-splat/knock-community-hall.sog';
const SIZE = 27830709;
const SHA256 = '2c9ef67e619878cdb85d8f972cc6b1b8a8c76cbd7b4ed1137ac97bbd78785202';

/** One pinned, licensed local sample. Untrusted archives never reach its decoder. */
export async function readFixedSplat(signal: AbortSignal): Promise<Uint8Array> {
  const response = await fetch(PATH, { signal });
  if (!response.ok || Number(response.headers.get('content-length')) !== SIZE || !response.body) {
    throw new Error('Unexpected Gaussian sample response');
  }
  const reader = response.body.getReader();
  const bytes = new Uint8Array(SIZE);
  let offset = 0;
  try {
    while (true) {
      const part = await reader.read();
      if (part.done) break;
      if (offset + part.value.length > SIZE) throw new Error('Gaussian sample exceeds size limit');
      bytes.set(part.value, offset); offset += part.value.length;
    }
    if (offset !== SIZE) throw new Error('Incomplete Gaussian sample');
  } finally { await reader.cancel(); }
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  const sha = Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, '0')).join('');
  if (sha !== SHA256) throw new Error('Gaussian sample fingerprint mismatch');
  return bytes;
}
